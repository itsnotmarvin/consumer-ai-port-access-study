#!/usr/bin/env python3
"""Verify the frozen Wave 4 research archive without modifying it.

The verifier intentionally uses only the Python standard library and opens
archive files for reading only.  It checks the collection, human-review lock
chain, analysis freezes, and final report receipt.  It never prints response
text, reviewer/adjudicator names, or other private field values.
"""

from __future__ import annotations

import csv
import hashlib
import hmac
import json
import re
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

EXPECTED_PROMPTS = 12
EXPECTED_RUNS = 96
EXPECTED_RATINGS_PER_REVIEWER = 96
EXPECTED_ADJUDICATIONS = 5
KNOWN_MISSING_PROTOCOL_FILE = "collection_manifest_initial_schedule.csv"

IGNORED_JSON_DIRECTORIES = {
    ".git",
    ".venv",
    "venv",
    "node_modules",
    "__pycache__",
}
SHA256_RE = re.compile(r"^[0-9a-fA-F]{64}$")
MAX_REPORTED_ERRORS = 20
MAX_REPORTED_WARNINGS = 10


class ArchiveVerifier:
    """Stateful, read-only verifier for one archive root."""

    def __init__(self, root: Path) -> None:
        self.root = root.resolve()
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.error_count = 0
        self.warning_count = 0
        self.json_cache: dict[Path, Any] = {}
        self.invalid_json: set[Path] = set()
        self.sha_cache: dict[Path, str] = {}
        self.hash_assertions = 0
        self.json_file_count = 0
        self.rating_counts: list[int] = []
        self.adjudication_count = 0

        # Filled by the lock-chain checks and reused by later freeze checks.
        self.originals_by_role: dict[str, dict[str, Any]] = {}
        self.original_response_ids: set[str] = set()
        self.adjudication_path: Path | None = None

    def error(self, message: str) -> None:
        self.error_count += 1
        if len(self.errors) < MAX_REPORTED_ERRORS:
            self.errors.append(message)

    def warning(self, message: str) -> None:
        self.warning_count += 1
        if len(self.warnings) < MAX_REPORTED_WARNINGS:
            self.warnings.append(message)

    def display_path(self, path: Path) -> str:
        try:
            return path.resolve().relative_to(self.root).as_posix()
        except (OSError, ValueError):
            return "archive path"

    def safe_path(
        self,
        raw_path: object,
        context: str,
        *,
        base: Path | None = None,
    ) -> Path | None:
        """Resolve a receipt path while refusing paths outside the archive."""
        if not isinstance(raw_path, str) or not raw_path.strip():
            self.error(f"{context}: missing or invalid path")
            return None

        supplied = Path(raw_path)
        if supplied.is_absolute():
            self.error(f"{context}: absolute paths are not allowed")
            return None

        candidate = ((base or self.root) / supplied).resolve()
        try:
            candidate.relative_to(self.root)
        except ValueError:
            self.error(f"{context}: path escapes the archive")
            return None
        return candidate

    def sha256(self, path: Path, context: str) -> str | None:
        path = path.resolve()
        if path in self.sha_cache:
            return self.sha_cache[path]
        try:
            digest = hashlib.sha256()
            with path.open("rb") as handle:
                for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                    digest.update(chunk)
            value = digest.hexdigest()
        except OSError:
            self.error(f"{context}: file could not be read")
            return None
        self.sha_cache[path] = value
        return value

    def check_hash(self, path: Path | None, expected: object, context: str) -> bool:
        if path is None:
            return False
        if not path.is_file():
            self.error(f"{context}: referenced file is missing")
            return False
        if not isinstance(expected, str) or not SHA256_RE.fullmatch(expected):
            self.error(f"{context}: receipt does not contain a valid SHA-256")
            return False

        actual = self.sha256(path, context)
        if actual is None:
            return False
        self.hash_assertions += 1
        if not hmac.compare_digest(actual.lower(), expected.lower()):
            self.error(f"{context}: SHA-256 mismatch")
            return False
        return True

    def check_size(self, path: Path | None, expected: object, context: str) -> bool:
        if path is None or not path.is_file():
            return False
        if not isinstance(expected, int) or isinstance(expected, bool) or expected < 0:
            self.error(f"{context}: receipt does not contain a valid byte count")
            return False
        try:
            actual = path.stat().st_size
        except OSError:
            self.error(f"{context}: file size could not be read")
            return False
        if actual != expected:
            self.error(f"{context}: byte count mismatch")
            return False
        return True

    def parse_json_file(self, path: Path) -> Any | None:
        path = path.resolve()
        if path in self.json_cache:
            return self.json_cache[path]
        if path in self.invalid_json:
            return None
        try:
            with path.open("r", encoding="utf-8") as handle:
                value = json.load(handle)
        except (OSError, UnicodeError, json.JSONDecodeError):
            self.invalid_json.add(path)
            self.error(f"JSON parse failed: {self.display_path(path)}")
            return None
        self.json_cache[path] = value
        return value

    def require_object(self, path: Path, context: str) -> dict[str, Any] | None:
        value = self.parse_json_file(path)
        if not isinstance(value, dict):
            if value is not None:
                self.error(f"{context}: expected a JSON object")
            return None
        return value

    def parse_all_archive_json(self) -> None:
        paths = sorted(
            path
            for path in self.root.rglob("*.json")
            if path.is_file()
            and not any(part in IGNORED_JSON_DIRECTORIES for part in path.parts)
        )
        self.json_file_count = len(paths)
        for path in paths:
            self.parse_json_file(path)

    @staticmethod
    def normalized_role(value: object) -> str | None:
        if not isinstance(value, str):
            return None
        normalized = value.strip().lower().replace("-", "_").replace(" ", "_")
        if normalized in {"a", "reviewer_a"}:
            return "a"
        if normalized in {"b", "reviewer_b"}:
            return "b"
        return None

    @staticmethod
    def unique_string_ids(rows: object, key: str) -> set[str] | None:
        if not isinstance(rows, list):
            return None
        values: list[str] = []
        for row in rows:
            if not isinstance(row, dict):
                return None
            value = row.get(key)
            if not isinstance(value, str) or not value:
                return None
            values.append(value)
        if len(values) != len(set(values)):
            return None
        return set(values)

    def verify_counts_and_collection(self) -> None:
        prompt_files = sorted(path for path in (self.root / "prompts").glob("*.txt") if path.is_file())
        output_files = sorted(path for path in (self.root / "outputs").glob("*.txt") if path.is_file())
        metadata_files = sorted(
            path for path in (self.root / "capture_metadata").glob("*.json") if path.is_file()
        )

        if len(prompt_files) != EXPECTED_PROMPTS:
            self.error(f"prompt corpus: expected {EXPECTED_PROMPTS} files, found {len(prompt_files)}")
        if len(output_files) != EXPECTED_RUNS:
            self.error(f"response corpus: expected {EXPECTED_RUNS} files, found {len(output_files)}")
        if len(metadata_files) != EXPECTED_RUNS:
            self.error(
                f"capture metadata: expected {EXPECTED_RUNS} files, found {len(metadata_files)}"
            )

        manifest_path = self.root / "collection_manifest.csv"
        try:
            with manifest_path.open("r", encoding="utf-8-sig", newline="") as handle:
                reader = csv.DictReader(handle)
                rows = list(reader)
                fieldnames = set(reader.fieldnames or [])
        except (OSError, UnicodeError, csv.Error):
            self.error("collection manifest: file could not be parsed")
            return

        required_fields = {
            "run_id",
            "prompt_path",
            "prompt_sha256",
            "output_path",
            "capture_metadata_path",
        }
        if not required_fields.issubset(fieldnames):
            self.error("collection manifest: required columns are missing")
            return
        if len(rows) != EXPECTED_RUNS:
            self.error(f"collection manifest: expected {EXPECTED_RUNS} rows, found {len(rows)}")

        run_ids = [row.get("run_id", "") for row in rows]
        if any(not value for value in run_ids) or len(run_ids) != len(set(run_ids)):
            self.error("collection manifest: run IDs are missing or not unique")

        referenced_prompts: set[Path] = set()
        referenced_outputs: set[Path] = set()
        referenced_metadata: set[Path] = set()

        for row_number, row in enumerate(rows, start=2):
            context = f"collection manifest row {row_number}"
            prompt_path = self.safe_path(row.get("prompt_path"), f"{context} prompt")
            output_path = self.safe_path(row.get("output_path"), f"{context} response")
            metadata_path = self.safe_path(
                row.get("capture_metadata_path"), f"{context} capture metadata"
            )

            if prompt_path is not None:
                referenced_prompts.add(prompt_path)
                self.check_hash(prompt_path, row.get("prompt_sha256"), f"{context} prompt")
            if output_path is not None:
                referenced_outputs.add(output_path)
                if not output_path.is_file():
                    self.error(f"{context} response: referenced file is missing")
            if metadata_path is not None:
                referenced_metadata.add(metadata_path)
                if not metadata_path.is_file():
                    self.error(f"{context} capture metadata: referenced file is missing")
                    continue

            if metadata_path is None or not metadata_path.is_file():
                continue
            metadata = self.require_object(metadata_path, f"{context} capture metadata")
            if metadata is None:
                continue

            if metadata.get("run_id") != row.get("run_id"):
                self.error(f"{context}: capture metadata run binding mismatch")
            if metadata.get("prompt_path") != row.get("prompt_path"):
                self.error(f"{context}: capture metadata prompt binding mismatch")
            if metadata.get("response_path") != row.get("output_path"):
                self.error(f"{context}: capture metadata response binding mismatch")

            manifest_prompt_hash = row.get("prompt_sha256")
            metadata_prompt_hash = metadata.get("prompt_sha256")
            if (
                isinstance(manifest_prompt_hash, str)
                and isinstance(metadata_prompt_hash, str)
                and not hmac.compare_digest(
                    manifest_prompt_hash.lower(), metadata_prompt_hash.lower()
                )
            ):
                self.error(f"{context}: manifest and capture prompt hashes disagree")

            if prompt_path is not None:
                self.check_hash(
                    prompt_path,
                    metadata_prompt_hash,
                    f"{context} captured prompt",
                )
            if output_path is not None:
                self.check_hash(
                    output_path,
                    metadata.get("response_sha256"),
                    f"{context} captured response",
                )

        actual_prompts = {path.resolve() for path in prompt_files}
        actual_outputs = {path.resolve() for path in output_files}
        actual_metadata = {path.resolve() for path in metadata_files}
        if referenced_prompts != actual_prompts:
            self.error("collection manifest: prompt references do not match the prompt corpus")
        if referenced_outputs != actual_outputs:
            self.error("collection manifest: response references do not match the response corpus")
        if referenced_metadata != actual_metadata:
            self.error("collection manifest: capture references do not match the metadata corpus")

        self.manifest_row_count = len(rows)
        self.prompt_count = len(prompt_files)
        self.output_count = len(output_files)
        self.metadata_count = len(metadata_files)

    def verify_protocol_lock(self) -> None:
        lock_path = self.root / "protocol_lock.json"
        lock = self.require_object(lock_path, "protocol lock")
        if lock is None:
            return

        if lock.get("planned_runs") != EXPECTED_RUNS:
            self.error("protocol lock: planned run count is not 96")

        locked_files = lock.get("locked_files")
        if not isinstance(locked_files, dict):
            self.error("protocol lock: locked_files is missing or invalid")
        else:
            if KNOWN_MISSING_PROTOCOL_FILE not in locked_files:
                self.error("protocol lock: known initial-schedule entry is absent from the receipt")
            for raw_path, expected_hash in locked_files.items():
                path = self.safe_path(raw_path, "protocol locked file")
                if path is None:
                    continue
                if not path.is_file() and raw_path == KNOWN_MISSING_PROTOCOL_FILE:
                    self.warning(
                        "Known retention gap: the protocol-locked initial collection schedule is absent"
                    )
                    continue
                self.check_hash(path, expected_hash, f"protocol locked file {raw_path}")

        prompt_hashes = lock.get("prompt_hashes")
        if not isinstance(prompt_hashes, dict):
            self.error("protocol lock: prompt_hashes is missing or invalid")
            return
        if len(prompt_hashes) != EXPECTED_PROMPTS:
            self.error(
                f"protocol lock: expected {EXPECTED_PROMPTS} prompt hashes, found {len(prompt_hashes)}"
            )
        for raw_path, expected_hash in prompt_hashes.items():
            path = self.safe_path(raw_path, "protocol prompt")
            self.check_hash(path, expected_hash, f"protocol prompt {raw_path}")

    def verify_review_packet_manifest(self) -> dict[str, dict[str, Any]]:
        path = self.root / "analysis" / "review_packet_manifest.json"
        manifest = self.require_object(path, "review packet manifest")
        if manifest is None:
            return {}
        if manifest.get("item_count") != EXPECTED_RUNS:
            self.error("review packet manifest: item count is not 96")

        self.check_hash(
            self.root / "human_rating_codebook.json",
            manifest.get("codebook_sha256"),
            "review packet codebook",
        )
        self.check_hash(
            self.root / "gold_dispositions.json",
            manifest.get("gold_dispositions_sha256"),
            "review packet gold dispositions",
        )
        self.check_hash(
            self.root / "collection_manifest.csv",
            manifest.get("collection_manifest_sha256"),
            "review packet collection manifest",
        )

        reviewer_records = manifest.get("reviewers")
        if not isinstance(reviewer_records, list) or len(reviewer_records) != 2:
            self.error("review packet manifest: expected two reviewer records")
            return {}
        by_role: dict[str, dict[str, Any]] = {}
        for record in reviewer_records:
            if not isinstance(record, dict):
                self.error("review packet manifest: invalid reviewer record")
                continue
            role = self.normalized_role(record.get("reviewer_code"))
            if role is None or role in by_role:
                self.error("review packet manifest: reviewer roles are invalid or duplicated")
                continue
            by_role[role] = record
        return by_role

    def verify_original_review_lock(self) -> None:
        packet_by_role = self.verify_review_packet_manifest()
        lock_path = self.root / "ratings" / "completed_originals" / "ORIGINALS_SHA256_LOCK.json"
        lock = self.require_object(lock_path, "original review lock")
        if lock is None:
            return
        records = lock.get("files")
        if not isinstance(records, list) or len(records) != 2:
            self.error("original review lock: expected two locked files")
            return

        response_sets: list[set[str]] = []
        for index, record in enumerate(records, start=1):
            context = f"original review lock entry {index}"
            if not isinstance(record, dict):
                self.error(f"{context}: invalid record")
                continue
            role = self.normalized_role(record.get("reviewer_code"))
            if role is None or role in self.originals_by_role:
                self.error(f"{context}: reviewer role is invalid or duplicated")
                continue

            path = self.safe_path(
                record.get("filename"),
                context,
                base=lock_path.parent,
            )
            self.check_hash(path, record.get("sha256"), context)
            self.check_size(path, record.get("bytes"), context)
            if path is None or not path.is_file():
                continue

            review = self.require_object(path, f"original review file {index}")
            if review is None:
                continue
            if self.normalized_role(review.get("reviewer_code")) != role:
                self.error(f"{context}: reviewer role binding mismatch")

            ratings = review.get("ratings")
            if not isinstance(ratings, list):
                self.error(f"original review file {index}: ratings list is missing")
                continue
            self.rating_counts.append(len(ratings))
            if len(ratings) != EXPECTED_RATINGS_PER_REVIEWER:
                self.error(
                    f"original review file {index}: expected 96 ratings, found {len(ratings)}"
                )
            response_ids = self.unique_string_ids(ratings, "response_id")
            if response_ids is None:
                self.error(f"original review file {index}: response IDs are missing or not unique")
                response_ids = set()
            response_sets.append(response_ids)

            self.check_hash(
                self.root / "human_rating_codebook.json",
                review.get("codebook_sha256"),
                f"original review file {index} codebook",
            )
            packet_record = packet_by_role.get(role)
            if packet_record is None:
                self.error(f"original review file {index}: review packet binding is missing")
            elif (
                review.get("packet_id") != packet_record.get("packet_id")
                or review.get("packet_sha256") != packet_record.get("packet_sha256")
            ):
                self.error(f"original review file {index}: review packet binding mismatch")

            actual_hash = self.sha256(path, context)
            self.originals_by_role[role] = {
                "path": path,
                "sha256": actual_hash,
                "document": review,
            }

        if set(self.originals_by_role) != {"a", "b"}:
            self.error("original review lock: both reviewer roles were not resolved")
        if len(response_sets) == 2:
            if response_sets[0] != response_sets[1]:
                self.error("original reviews: the two 96-response ID sets differ")
            else:
                self.original_response_ids = response_sets[0]

    def role_path(self, role: str) -> Path | None:
        record = self.originals_by_role.get(role)
        path = record.get("path") if isinstance(record, dict) else None
        return path if isinstance(path, Path) else None

    def verify_pre_adjudication_freeze(self) -> None:
        freeze_path = self.root / "analysis" / "PRE_ADJUDICATION_FREEZE.json"
        freeze = self.require_object(freeze_path, "pre-adjudication freeze")
        if freeze is None:
            return
        locked = freeze.get("locked_inputs")
        if not isinstance(locked, dict):
            self.error("pre-adjudication freeze: locked_inputs is invalid")
        else:
            originals_lock_path = self.safe_path(
                locked.get("originals_lock_path"), "pre-adjudication originals lock"
            )
            self.check_hash(
                originals_lock_path,
                locked.get("originals_lock_sha256"),
                "pre-adjudication originals lock",
            )
            self.check_hash(
                self.role_path("a"),
                locked.get("reviewer_a_sha256"),
                "pre-adjudication original review A",
            )
            self.check_hash(
                self.role_path("b"),
                locked.get("reviewer_b_sha256"),
                "pre-adjudication original review B",
            )

        outputs = freeze.get("frozen_outputs")
        if not isinstance(outputs, dict):
            self.error("pre-adjudication freeze: frozen_outputs is invalid")
            return
        for stem in ("agreement_analysis", "primary_disagreements"):
            path = self.safe_path(outputs.get(f"{stem}_path"), f"pre-adjudication {stem}")
            self.check_hash(
                path,
                outputs.get(f"{stem}_sha256"),
                f"pre-adjudication {stem}",
            )
        if outputs.get("primary_n") != EXPECTED_RUNS:
            self.error("pre-adjudication freeze: primary count is not 96")
        if outputs.get("primary_disagreement_count") != EXPECTED_ADJUDICATIONS:
            self.error("pre-adjudication freeze: disagreement count is not 5")

    def verify_adjudication_lock(self) -> None:
        lock_path = (
            self.root
            / "ratings"
            / "completed_adjudication"
            / "ADJUDICATION_SHA256_LOCK.json"
        )
        lock = self.require_object(lock_path, "adjudication lock")
        if lock is None:
            return
        preserved = lock.get("preserved_file")
        if not isinstance(preserved, dict):
            self.error("adjudication lock: preserved_file is invalid")
            return
        path = self.safe_path(preserved.get("path"), "adjudication preserved file")
        self.check_hash(path, preserved.get("sha256"), "adjudication preserved file")
        self.check_size(path, preserved.get("size_bytes"), "adjudication preserved file")
        self.adjudication_path = path

        if path is None or not path.is_file():
            return
        adjudication = self.require_object(path, "adjudication preserved file")
        if adjudication is None:
            return
        decisions = adjudication.get("decisions")
        if not isinstance(decisions, list):
            self.error("adjudication preserved file: decisions list is missing")
            return
        self.adjudication_count = len(decisions)
        if len(decisions) != EXPECTED_ADJUDICATIONS:
            self.error(f"adjudication: expected 5 decisions, found {len(decisions)}")
        decision_ids = self.unique_string_ids(decisions, "response_id")
        if decision_ids is None:
            self.error("adjudication: response IDs are missing or not unique")
            decision_ids = set()
        if self.original_response_ids and not decision_ids.issubset(self.original_response_ids):
            self.error("adjudication: decision IDs are not a subset of the original reviews")

        packet_manifest_path = self.root / "analysis" / "adjudication_packet_manifest.json"
        packet_manifest = self.require_object(packet_manifest_path, "adjudication packet manifest")
        if packet_manifest is not None:
            if packet_manifest.get("item_count") != EXPECTED_ADJUDICATIONS:
                self.error("adjudication packet manifest: item count is not 5")
            packet_ids = packet_manifest.get("response_ids")
            if not isinstance(packet_ids, list) or set(packet_ids) != decision_ids:
                self.error("adjudication: frozen packet and decision ID sets differ")
            for index, record in enumerate(packet_manifest.get("output_files", []), start=1):
                if not isinstance(record, dict):
                    self.error(f"adjudication packet output {index}: invalid receipt")
                    continue
                output_path = self.safe_path(
                    record.get("path"), f"adjudication packet output {index}"
                )
                self.check_hash(
                    output_path,
                    record.get("sha256"),
                    f"adjudication packet output {index}",
                )

        binding = lock.get("binding_inputs")
        if not isinstance(binding, dict):
            self.error("adjudication lock: binding_inputs is invalid")
            return
        if binding.get("packet_id") != adjudication.get("packet_id"):
            self.error("adjudication lock: packet ID binding mismatch")
        if binding.get("packet_sha256") != adjudication.get("packet_sha256"):
            self.error("adjudication lock: packet hash binding mismatch")
        if binding.get("codebook_sha256") != adjudication.get("codebook_sha256"):
            self.error("adjudication lock: codebook binding mismatch")

        if packet_manifest is not None:
            if (
                binding.get("packet_id") != packet_manifest.get("packet_id")
                or binding.get("packet_sha256") != packet_manifest.get("packet_sha256")
            ):
                self.error("adjudication lock: packet manifest binding mismatch")
            if binding.get("codebook_sha256") != packet_manifest.get("codebook_sha256"):
                self.error("adjudication lock: packet codebook binding mismatch")
            self.check_hash(
                self.root / "analysis" / "PRE_ADJUDICATION_FREEZE.json",
                packet_manifest.get("source_freeze_sha256"),
                "adjudication packet source freeze",
            )

        self.check_hash(
            self.root / "human_rating_codebook.json",
            binding.get("codebook_sha256"),
            "adjudication binding codebook",
        )
        self.check_hash(
            self.root / "analysis" / "PRE_ADJUDICATION_FREEZE.json",
            binding.get("pre_adjudication_freeze_sha256"),
            "adjudication binding pre-freeze",
        )
        self.check_hash(
            self.role_path("a"),
            binding.get("reviewer_a_original_sha256"),
            "adjudication binding original review A",
        )
        self.check_hash(
            self.role_path("b"),
            binding.get("reviewer_b_original_sha256"),
            "adjudication binding original review B",
        )

    def check_path_hash_pairs(
        self,
        values: object,
        pairs: tuple[tuple[str, str], ...],
        context: str,
    ) -> None:
        if not isinstance(values, dict):
            self.error(f"{context}: receipt object is invalid")
            return
        for path_key, hash_key in pairs:
            path = self.safe_path(values.get(path_key), f"{context} {path_key}")
            self.check_hash(path, values.get(hash_key), f"{context} {path_key}")

    def verify_final_endpoint_freeze(self) -> None:
        freeze_path = self.root / "analysis" / "FINAL_HUMAN_ENDPOINTS_BLINDED_FREEZE.json"
        freeze = self.require_object(freeze_path, "final blinded endpoint freeze")
        if freeze is None:
            return
        sources = freeze.get("sources")
        if not isinstance(sources, dict):
            self.error("final blinded endpoint freeze: sources is invalid")
        else:
            source_paths = {
                "reviewer_a_original_sha256": self.role_path("a"),
                "reviewer_b_original_sha256": self.role_path("b"),
                "adjudication_original_sha256": self.adjudication_path,
                "pre_adjudication_freeze_sha256": self.root
                / "analysis"
                / "PRE_ADJUDICATION_FREEZE.json",
                "codebook_sha256": self.root / "human_rating_codebook.json",
            }
            for key, path in source_paths.items():
                self.check_hash(path, sources.get(key), f"final blinded freeze source {key}")

        self.check_path_hash_pairs(
            freeze.get("outputs"),
            (
                ("validation_path", "validation_sha256"),
                ("final_json_path", "final_json_sha256"),
                ("final_csv_path", "final_csv_sha256"),
            ),
            "final blinded freeze output",
        )
        if freeze.get("row_count") != EXPECTED_RUNS:
            self.error("final blinded endpoint freeze: row count is not 96")
        if freeze.get("human_adjudication_count") != EXPECTED_ADJUDICATIONS:
            self.error("final blinded endpoint freeze: adjudication count is not 5")
        label_counts = freeze.get("final_label_counts")
        if not isinstance(label_counts, dict) or sum(
            value for value in label_counts.values() if isinstance(value, int)
        ) != EXPECTED_RUNS:
            self.error("final blinded endpoint freeze: label counts do not sum to 96")

        endpoint_path = self.root / "analysis" / "final_human_endpoints_blinded.json"
        endpoint = self.require_object(endpoint_path, "final blinded endpoint dataset")
        if endpoint is not None:
            rows = endpoint.get("rows")
            if not isinstance(rows, list) or len(rows) != EXPECTED_RUNS:
                self.error("final blinded endpoint dataset: expected 96 rows")
            else:
                endpoint_ids = self.unique_string_ids(rows, "response_id")
                if endpoint_ids is None:
                    self.error("final blinded endpoint dataset: response IDs are invalid")
                elif self.original_response_ids and endpoint_ids != self.original_response_ids:
                    self.error("final blinded endpoint dataset: response ID set changed")

    def check_record_list(self, records: object, context: str) -> None:
        if not isinstance(records, list):
            self.error(f"{context}: expected a list of file receipts")
            return
        seen: set[Path] = set()
        for index, record in enumerate(records, start=1):
            item_context = f"{context} {index}"
            if not isinstance(record, dict):
                self.error(f"{item_context}: invalid file receipt")
                continue
            path = self.safe_path(record.get("path"), item_context)
            if path is not None:
                if path in seen:
                    self.error(f"{item_context}: duplicate output path")
                seen.add(path)
            self.check_hash(path, record.get("sha256"), item_context)
            if "size_bytes" in record:
                self.check_size(path, record.get("size_bytes"), item_context)

    def verify_final_results_freeze(self) -> None:
        freeze_path = self.root / "analysis" / "FINAL_RESULTS_FREEZE.json"
        freeze = self.require_object(freeze_path, "final results freeze")
        if freeze is None:
            return
        sources = freeze.get("source_hashes")
        if not isinstance(sources, dict):
            self.error("final results freeze: source_hashes is invalid")
        else:
            source_paths = {
                "final_blinded_endpoint_sha256": self.root
                / "analysis"
                / "final_human_endpoints_blinded.json",
                "final_blinded_freeze_sha256": self.root
                / "analysis"
                / "FINAL_HUMAN_ENDPOINTS_BLINDED_FREEZE.json",
                "admin_blinding_key_sha256": self.root / "analysis" / "ADMIN_blinding_key.json",
                "design_sha256": self.root / "design.json",
                "gold_dispositions_sha256": self.root / "gold_dispositions.json",
                "collection_manifest_sha256": self.root / "collection_manifest.csv",
                "codebook_sha256": self.root / "human_rating_codebook.json",
                "human_agreement_pre_adjudication_sha256": self.root
                / "analysis"
                / "human_agreement_pre_adjudication.json",
            }
            for key, path in source_paths.items():
                self.check_hash(path, sources.get(key), f"final results freeze source {key}")

        self.check_record_list(freeze.get("outputs"), "final results output")
        primary = freeze.get("primary_result")
        if not isinstance(primary, dict):
            self.error("final results freeze: primary result is invalid")
        else:
            if primary.get("n") != EXPECTED_RUNS:
                self.error("final results freeze: primary n is not 96")
            counts = [primary.get(key) for key in ("yes", "no", "unclear")]
            if not all(isinstance(value, int) for value in counts) or sum(counts) != EXPECTED_RUNS:
                self.error("final results freeze: primary label counts do not sum to 96")

    def verify_report_receipt(self) -> None:
        receipt_path = self.root / "report" / "FINAL_REPORT_RECEIPT.json"
        receipt = self.require_object(receipt_path, "final report receipt")
        if receipt is None:
            return
        outputs = receipt.get("report_outputs")
        if not isinstance(outputs, dict):
            self.error("final report receipt: report_outputs is invalid")
        else:
            for key in ("canonical_artifact", "standalone_html", "build_notes"):
                record = outputs.get(key)
                if not isinstance(record, dict):
                    self.error(f"final report receipt: {key} receipt is invalid")
                    continue
                path = self.safe_path(record.get("path"), f"final report {key}")
                self.check_hash(path, record.get("sha256"), f"final report {key}")
                self.check_size(path, record.get("size_bytes"), f"final report {key}")

        frozen = receipt.get("frozen_analysis_inputs")
        if not isinstance(frozen, dict):
            self.error("final report receipt: frozen_analysis_inputs is invalid")
            return
        input_paths = {
            "final_results_sha256": self.root / "analysis" / "final_results.json",
            "human_agreement_pre_adjudication_sha256": self.root
            / "analysis"
            / "human_agreement_pre_adjudication.json",
            "final_results_freeze_sha256": self.root
            / "analysis"
            / "FINAL_RESULTS_FREEZE.json",
            "final_blinded_endpoint_sha256": self.root
            / "analysis"
            / "final_human_endpoints_blinded.json",
            "analysis_script_sha256": self.root / "tools" / "analyze_final_endpoints.py",
        }
        for key, path in input_paths.items():
            self.check_hash(path, frozen.get(key), f"final report frozen input {key}")

        # These builder hashes describe external/prebuilt tooling or an internal
        # reviewed snapshot rather than separately archived files.  Validate the
        # receipt fields as hashes without pretending they can be re-derived here.
        builder = receipt.get("builder_receipt")
        builder_details = builder.get("builder") if isinstance(builder, dict) else None
        if not isinstance(builder_details, dict):
            self.error("final report receipt: builder receipt is invalid")
        else:
            for key in ("runtime_sha256", "compiler_sha256", "reviewed_snapshot_sha256"):
                value = builder_details.get(key)
                if not isinstance(value, str) or not SHA256_RE.fullmatch(value):
                    self.error(f"final report receipt: {key} is not a valid SHA-256")

    def run(self) -> int:
        self.parse_all_archive_json()
        self.verify_counts_and_collection()
        self.verify_protocol_lock()
        self.verify_original_review_lock()
        self.verify_pre_adjudication_freeze()
        self.verify_adjudication_lock()
        self.verify_final_endpoint_freeze()
        self.verify_final_results_freeze()
        self.verify_report_receipt()
        self.print_summary()
        return 1 if self.error_count else 0

    def print_summary(self) -> None:
        status = "PASS" if self.error_count == 0 else "FAIL"
        manifest_rows = getattr(self, "manifest_row_count", 0)
        prompts = getattr(self, "prompt_count", 0)
        outputs = getattr(self, "output_count", 0)
        metadata = getattr(self, "metadata_count", 0)
        if len(self.rating_counts) == 2 and len(set(self.rating_counts)) == 1:
            ratings = f"{self.rating_counts[0]} ratings per reviewer (2 reviewers)"
        elif self.rating_counts:
            ratings = f"rating counts {','.join(str(value) for value in self.rating_counts)}"
        else:
            ratings = "ratings unavailable"

        print(f"Archive verification: {status}")
        print(
            "  Collection: "
            f"{prompts} prompts, {manifest_rows} manifest rows, "
            f"{outputs} responses, {metadata} capture records"
        )
        print(f"  Human review: {ratings}, {self.adjudication_count} adjudications")
        print(
            f"  Integrity: {self.json_file_count} JSON files parsed, "
            f"{self.hash_assertions} hash assertions checked"
        )

        if self.warning_count:
            print(f"Warnings ({self.warning_count}):")
            for message in self.warnings:
                print(f"  - {message}")
            omitted = self.warning_count - len(self.warnings)
            if omitted:
                print(f"  - {omitted} additional warning(s) omitted")

        if self.error_count:
            print(f"Unexpected integrity failures ({self.error_count}):")
            for message in self.errors:
                print(f"  - {message}")
            omitted = self.error_count - len(self.errors)
            if omitted:
                print(f"  - {omitted} additional failure(s) omitted")


def main() -> int:
    return ArchiveVerifier(ROOT).run()


if __name__ == "__main__":
    sys.exit(main())
