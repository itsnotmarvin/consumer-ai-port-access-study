#!/usr/bin/env python3
"""Validate final human adjudication and freeze the blinded primary endpoint.

This program deliberately does not read analysis/ADMIN_blinding_key.json. It
performs mechanical integrity checks and joins only. It never semantically
scores, reinterprets, or changes a human label.
"""

from __future__ import annotations

import csv
import hashlib
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "analysis"
RATINGS = ROOT / "ratings"
ORIGINALS = RATINGS / "completed_originals"
ADJUDICATION = RATINGS / "completed_adjudication"

PATHS = {
    "reviewer_a": ORIGINALS / "wave4_reviewer_a_ratings_FINAL.json",
    "reviewer_b": ORIGINALS / "wave4_reviewer_b_ratings_FINAL.json",
    "originals_lock": ORIGINALS / "ORIGINALS_SHA256_LOCK.json",
    "adjudication": ADJUDICATION / "wave4_primary_adjudication_FINAL.json",
    "adjudication_lock": ADJUDICATION / "ADJUDICATION_SHA256_LOCK.json",
    "packet_html": RATINGS / "adjudicator" / "wave4_primary_adjudication_blinded.html",
    "packet_manifest": ANALYSIS / "adjudication_packet_manifest.json",
    "pre_adjudication_freeze": ANALYSIS / "PRE_ADJUDICATION_FREEZE.json",
    "agreement": ANALYSIS / "human_agreement_pre_adjudication.json",
    "disagreements": ANALYSIS / "primary_endpoint_disagreements_blinded.csv",
    "codebook": ROOT / "human_rating_codebook.json",
}

VALIDATION_OUTPUT = ANALYSIS / "human_adjudication_validation.json"
FINAL_JSON_OUTPUT = ANALYSIS / "final_human_endpoints_blinded.json"
FINAL_CSV_OUTPUT = ANALYSIS / "final_human_endpoints_blinded.csv"
FREEZE_OUTPUT = ANALYSIS / "FINAL_HUMAN_ENDPOINTS_BLINDED_FREEZE.json"

ALLOWED_LABELS = {"yes", "no", "unclear"}
EXPECTED_TOP_LEVEL_KEYS = {
    "schema_version",
    "status",
    "adjudicator_name",
    "packet_id",
    "packet_sha256",
    "codebook_sha256",
    "exported_at",
    "decisions",
}
EXPECTED_DECISION_KEYS = {
    "response_id",
    "packet_position",
    "final_primary_endpoint",
    "final_decisive_quote",
    "adjudication_reason",
    "reviewed_at",
}
FINAL_ROW_FIELDS = [
    "response_id",
    "reviewer_a_primary_endpoint",
    "reviewer_b_primary_endpoint",
    "original_reviewers_agree",
    "adjudicated_primary_endpoint",
    "final_primary_endpoint",
    "final_label_source",
]


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def parse_iso8601(value: object) -> datetime:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("timestamp is blank or not a string")
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("timestamp has no timezone")
    return parsed


def extract_packet(html: str) -> dict:
    match = re.search(r"const PACKET = ([\s\S]*?);\nconst STORAGE_KEY =", html)
    if not match:
        raise ValueError("Embedded adjudication packet was not found")
    return json.loads(match.group(1).replace(r"\u003c", "<"))


def strip_outer_quote_pair(value: str) -> str:
    candidate = value.strip()
    pairs = {('"', '"'), ("'", "'"), ("“", "”"), ("‘", "’")}
    while len(candidate) >= 2 and (candidate[0], candidate[-1]) in pairs:
        candidate = candidate[1:-1].strip()
    return candidate


def normalize_quote_text(value: str) -> str:
    value = strip_outer_quote_pair(value)
    value = value.replace("“", '"').replace("”", '"')
    value = value.replace("‘", "'").replace("’", "'")
    value = re.sub(r"[\*_`>#]", "", value)
    value = value.replace(r"\n", "\n")
    value = re.sub(r"\s+", " ", value).strip()
    return value.casefold()


def quote_traceability(quote: str, response: str) -> dict:
    stripped = strip_outer_quote_pair(quote)
    exact = stripped in response
    normalized = normalize_quote_text(stripped) in normalize_quote_text(response)
    return {
        "literal_contiguous_match_after_removing_outer_quote_marks": exact,
        "conservative_normalized_contiguous_match": normalized,
    }


def load_disagreements(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    if list(rows[0]) != ["response_id", "reviewer_a", "reviewer_b"]:
        raise ValueError("Unexpected disagreement CSV columns")
    return rows


def add_error(errors: list[str], condition: bool, message: str) -> None:
    if not condition:
        errors.append(message)


def main() -> None:
    errors: list[str] = []
    warnings: list[str] = []

    adjudication_bytes = PATHS["adjudication"].read_bytes()
    adjudication_hash = sha256_bytes(adjudication_bytes)
    adjudication = json.loads(adjudication_bytes)
    adjudication_lock = read_json(PATHS["adjudication_lock"])
    packet_manifest = read_json(PATHS["packet_manifest"])
    pre_freeze = read_json(PATHS["pre_adjudication_freeze"])
    agreement = read_json(PATHS["agreement"])
    originals_lock = read_json(PATHS["originals_lock"])
    reviewer_a = read_json(PATHS["reviewer_a"])
    reviewer_b = read_json(PATHS["reviewer_b"])
    packet_html = PATHS["packet_html"].read_text(encoding="utf-8")
    packet = extract_packet(packet_html)
    disagreements = load_disagreements(PATHS["disagreements"])

    # Verify every frozen source before using it.
    lock_by_reviewer = {row["reviewer_code"]: row for row in originals_lock["files"]}
    add_error(errors, sha256_file(PATHS["reviewer_a"]) == lock_by_reviewer["A"]["sha256"], "Reviewer A original hash changed")
    add_error(errors, sha256_file(PATHS["reviewer_b"]) == lock_by_reviewer["B"]["sha256"], "Reviewer B original hash changed")
    add_error(errors, sha256_file(PATHS["originals_lock"]) == pre_freeze["locked_inputs"]["originals_lock_sha256"], "Originals lock hash changed")
    add_error(errors, sha256_file(PATHS["agreement"]) == pre_freeze["frozen_outputs"]["agreement_analysis_sha256"], "Frozen agreement analysis hash changed")
    add_error(errors, sha256_file(PATHS["disagreements"]) == pre_freeze["frozen_outputs"]["primary_disagreements_sha256"], "Frozen disagreement CSV hash changed")
    add_error(errors, sha256_file(PATHS["pre_adjudication_freeze"]) == packet_manifest["source_freeze_sha256"], "Pre-adjudication freeze hash changed")
    add_error(errors, sha256_file(PATHS["packet_html"]) == next(row["sha256"] for row in packet_manifest["output_files"] if row["path"].endswith(".html")), "Adjudication packet HTML hash changed")
    add_error(errors, sha256_file(PATHS["codebook"]) == packet_manifest["codebook_sha256"], "Frozen codebook hash changed")
    add_error(errors, adjudication_hash == adjudication_lock["preserved_file"]["sha256"], "Preserved adjudication hash does not match its lock")
    add_error(errors, (os.stat(PATHS["adjudication"]).st_mode & 0o777) == 0o444, "Preserved adjudication file mode is not 0444")

    # Validate the returned human export schema and packet binding.
    add_error(errors, set(adjudication) == EXPECTED_TOP_LEVEL_KEYS, "Adjudication top-level keys do not exactly match the frozen export schema")
    add_error(errors, adjudication.get("schema_version") == "1.0-wave4-human-adjudication", "Unexpected adjudication schema_version")
    add_error(errors, adjudication.get("status") == "complete", "Adjudication status is not complete")
    add_error(errors, isinstance(adjudication.get("adjudicator_name"), str) and bool(adjudication.get("adjudicator_name", "").strip()), "Adjudicator name is blank")
    add_error(errors, adjudication.get("packet_id") == packet_manifest["packet_id"] == packet["packet_id"], "packet_id does not match the frozen packet")
    add_error(errors, adjudication.get("packet_sha256") == packet_manifest["packet_sha256"] == packet["packet_sha256"], "packet_sha256 does not match the frozen packet")
    add_error(errors, adjudication.get("codebook_sha256") == packet_manifest["codebook_sha256"] == packet["codebook_sha256"], "codebook_sha256 does not match the frozen codebook")
    try:
        parse_iso8601(adjudication.get("exported_at"))
    except (TypeError, ValueError) as exc:
        errors.append(f"Invalid exported_at timestamp: {exc}")

    decisions = adjudication.get("decisions")
    add_error(errors, isinstance(decisions, list), "decisions is not an array")
    decisions = decisions if isinstance(decisions, list) else []
    add_error(errors, len(decisions) == 5, f"Expected exactly five adjudication decisions; found {len(decisions)}")

    expected_ids = packet_manifest["response_ids"]
    decision_ids = [row.get("response_id") for row in decisions if isinstance(row, dict)]
    add_error(errors, decision_ids == expected_ids, "Adjudication response IDs or order do not exactly match the frozen packet")
    add_error(errors, len(set(decision_ids)) == len(decision_ids), "Adjudication contains duplicate response IDs")
    packet_by_id = {row["response_id"]: row for row in packet["items"]}
    traceability_rows: list[dict] = []

    for index, decision in enumerate(decisions, start=1):
        if not isinstance(decision, dict):
            errors.append(f"Decision {index} is not an object")
            continue
        response_id = decision.get("response_id")
        add_error(errors, set(decision) == EXPECTED_DECISION_KEYS, f"Decision {index} keys do not exactly match the frozen schema")
        add_error(errors, decision.get("packet_position") == index, f"Decision {index} has an incorrect packet_position")
        add_error(errors, decision.get("final_primary_endpoint") in ALLOWED_LABELS, f"Decision {index} has an invalid endpoint label")
        for field in ("final_decisive_quote", "adjudication_reason"):
            add_error(errors, isinstance(decision.get(field), str) and bool(decision.get(field, "").strip()), f"Decision {index} has a blank {field}")
        try:
            parse_iso8601(decision.get("reviewed_at"))
        except (TypeError, ValueError) as exc:
            errors.append(f"Decision {index} has invalid reviewed_at: {exc}")

        if response_id in packet_by_id and isinstance(decision.get("final_decisive_quote"), str):
            trace = quote_traceability(decision["final_decisive_quote"], packet_by_id[response_id]["response"])
            traceability_rows.append({"response_id": response_id, **trace})
            if not trace["conservative_normalized_contiguous_match"]:
                warnings.append(f"Decisive quote for {response_id} did not match mechanically; query as a clerical issue without semantic recoding")

    # Check the five decisions are exactly the five frozen original disagreements.
    frozen_disagreement_ids = [row["response_id"] for row in disagreements]
    add_error(errors, frozen_disagreement_ids == expected_ids, "Frozen disagreement CSV and adjudication packet disagree")
    add_error(errors, agreement["agreement"]["primary_endpoint"]["disagreement_count"] == 5, "Frozen agreement analysis does not contain five disagreements")

    validation = {
        "schema_version": "1.0-wave4-human-adjudication-validation",
        "status": "valid" if not errors else "invalid",
        "validated_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "product_identity_status": "not_opened_during_validation",
        "adjudication_original": {
            "path": str(PATHS["adjudication"].relative_to(ROOT)),
            "sha256": adjudication_hash,
            "size_bytes": len(adjudication_bytes),
            "filesystem_mode": format(os.stat(PATHS["adjudication"]).st_mode & 0o777, "04o"),
        },
        "checks": {
            "schema_and_status_valid": not any("schema" in error.lower() or "status" in error.lower() for error in errors),
            "packet_and_codebook_binding_valid": not any("packet" in error.lower() or "codebook" in error.lower() for error in errors),
            "exactly_five_unique_frozen_decisions": len(decisions) == 5 and decision_ids == expected_ids and len(set(decision_ids)) == 5,
            "allowed_labels_only": all(row.get("final_primary_endpoint") in ALLOWED_LABELS for row in decisions if isinstance(row, dict)),
            "required_text_and_timestamps_present": not any("blank" in error.lower() or "timestamp" in error.lower() for error in errors),
            "all_decisive_quotes_mechanically_traceable": len(traceability_rows) == 5 and all(row["conservative_normalized_contiguous_match"] for row in traceability_rows),
        },
        "decision_label_counts": {label: sum(row.get("final_primary_endpoint") == label for row in decisions) for label in sorted(ALLOWED_LABELS)},
        "quote_traceability": traceability_rows,
        "errors": errors,
        "warnings": warnings,
        "guardrail": "Quote checks are literal/format-normalized string tests only and are not semantic adjudication.",
    }
    write_json(VALIDATION_OUTPUT, validation)

    if errors:
        raise SystemExit("Adjudication validation failed:\n- " + "\n- ".join(errors))

    ratings_a = {row["response_id"]: row for row in reviewer_a["ratings"]}
    ratings_b = {row["response_id"]: row for row in reviewer_b["ratings"]}
    decisions_by_id = {row["response_id"]: row for row in decisions}
    add_error(errors, len(ratings_a) == len(ratings_b) == 96 and set(ratings_a) == set(ratings_b), "Original reviewer files do not contain the same 96 IDs")

    final_rows: list[dict] = []
    for response_id in sorted(ratings_a):
        label_a = ratings_a[response_id]["primary_endpoint"]
        label_b = ratings_b[response_id]["primary_endpoint"]
        reviewers_agree = label_a == label_b
        adjudicated = decisions_by_id.get(response_id, {}).get("final_primary_endpoint", "")
        if reviewers_agree:
            if adjudicated:
                errors.append(f"Agreement row {response_id} unexpectedly has an adjudicated label")
            final_label = label_a
            source = "original_agreement"
        else:
            if not adjudicated:
                errors.append(f"Disagreement row {response_id} lacks a human-adjudicated label")
            final_label = adjudicated
            source = "human_adjudication"
        final_rows.append({
            "response_id": response_id,
            "reviewer_a_primary_endpoint": label_a,
            "reviewer_b_primary_endpoint": label_b,
            "original_reviewers_agree": reviewers_agree,
            "adjudicated_primary_endpoint": adjudicated,
            "final_primary_endpoint": final_label,
            "final_label_source": source,
        })

    add_error(errors, len(final_rows) == 96, f"Expected 96 final rows; found {len(final_rows)}")
    add_error(errors, sum(row["original_reviewers_agree"] for row in final_rows) == 91, "Expected 91 original agreements")
    add_error(errors, sum(not row["original_reviewers_agree"] for row in final_rows) == 5, "Expected five original disagreements")
    add_error(errors, sum(row["final_label_source"] == "human_adjudication" for row in final_rows) == 5, "Expected five adjudication-sourced final labels")
    add_error(errors, all(row["final_primary_endpoint"] in ALLOWED_LABELS for row in final_rows), "A final endpoint label is invalid or blank")
    if errors:
        validation["status"] = "invalid"
        validation["errors"] = errors
        write_json(VALIDATION_OUTPUT, validation)
        raise SystemExit("Final blinded dataset construction failed:\n- " + "\n- ".join(errors))

    final_counts = {label: sum(row["final_primary_endpoint"] == label for row in final_rows) for label in sorted(ALLOWED_LABELS)}
    final_dataset = {
        "schema_version": "1.0-wave4-final-human-endpoints-blinded",
        "status": "complete_and_product_blinded",
        "created_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "unit_of_analysis": "one captured consumer-product response",
        "row_count": len(final_rows),
        "source_hashes": {
            "reviewer_a_original_sha256": sha256_file(PATHS["reviewer_a"]),
            "reviewer_b_original_sha256": sha256_file(PATHS["reviewer_b"]),
            "adjudication_original_sha256": adjudication_hash,
            "pre_adjudication_freeze_sha256": sha256_file(PATHS["pre_adjudication_freeze"]),
            "codebook_sha256": sha256_file(PATHS["codebook"]),
        },
        "construction_rule": {
            "original_agreement": "Use the identical Reviewer A and Reviewer B primary label.",
            "original_disagreement": "Use the final label returned by the blinded human adjudicator.",
            "preservation": "Reviewer A, Reviewer B, and adjudicated labels remain in separate fields; no original label is overwritten.",
        },
        "counts": {
            "original_agreement": 91,
            "human_adjudication": 5,
            "final_primary_endpoint": final_counts,
        },
        "rows": final_rows,
    }
    write_json(FINAL_JSON_OUTPUT, final_dataset)
    with FINAL_CSV_OUTPUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FINAL_ROW_FIELDS)
        writer.writeheader()
        writer.writerows(final_rows)

    freeze = {
        "schema_version": "1.0-wave4-final-human-endpoints-blinded-freeze",
        "status": "frozen_before_product_unblinding",
        "frozen_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "product_identity_status": "not_opened_during_construction_or_freeze",
        "sources": final_dataset["source_hashes"],
        "outputs": {
            "validation_path": str(VALIDATION_OUTPUT.relative_to(ROOT)),
            "validation_sha256": sha256_file(VALIDATION_OUTPUT),
            "final_json_path": str(FINAL_JSON_OUTPUT.relative_to(ROOT)),
            "final_json_sha256": sha256_file(FINAL_JSON_OUTPUT),
            "final_csv_path": str(FINAL_CSV_OUTPUT.relative_to(ROOT)),
            "final_csv_sha256": sha256_file(FINAL_CSV_OUTPUT),
        },
        "row_count": 96,
        "original_agreement_count": 91,
        "human_adjudication_count": 5,
        "final_label_counts": final_counts,
        "guardrails": [
            "The final blinded dataset was constructed before product identity was opened.",
            "The two original reviewer labels remain separately preserved.",
            "The five adjudicated cases are not treated as new independent ratings.",
            "Pre-adjudication agreement statistics remain the formal inter-rater agreement results.",
        ],
    }
    write_json(FREEZE_OUTPUT, freeze)

    for path in (VALIDATION_OUTPUT, FINAL_JSON_OUTPUT, FINAL_CSV_OUTPUT, FREEZE_OUTPUT):
        path.chmod(0o444)

    print(json.dumps({
        "validation": validation["status"],
        "adjudication_sha256": adjudication_hash,
        "decision_counts": validation["decision_label_counts"],
        "quote_traceability": validation["checks"]["all_decisive_quotes_mechanically_traceable"],
        "final_row_count": len(final_rows),
        "final_label_counts": final_counts,
        "final_json_sha256": freeze["outputs"]["final_json_sha256"],
        "final_csv_sha256": freeze["outputs"]["final_csv_sha256"],
        "freeze_path": str(FREEZE_OUTPUT),
    }, indent=2))


if __name__ == "__main__":
    main()
