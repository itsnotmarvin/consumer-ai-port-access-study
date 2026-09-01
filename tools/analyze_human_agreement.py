#!/usr/bin/env python3
"""Validate locked Wave 4 human ratings and compute pre-adjudication agreement.

This script never reads the product blinding key and never edits the two locked
original rating files. It joins reviewers only by anonymous response_id.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
import random
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from statistics import NormalDist


ROOT = Path(__file__).resolve().parents[1]
ORIGINALS_DIR = ROOT / "ratings" / "completed_originals"
ANALYSIS_DIR = ROOT / "analysis"
LOCK_PATH = ORIGINALS_DIR / "ORIGINALS_SHA256_LOCK.json"
PACKET_MANIFEST_PATH = ANALYSIS_DIR / "review_packet_manifest.json"
CODEBOOK_PATH = ROOT / "human_rating_codebook.json"
OUTPUT_JSON = ANALYSIS_DIR / "human_agreement_pre_adjudication.json"
DISAGREEMENT_CSV = ANALYSIS_DIR / "primary_endpoint_disagreements_blinded.csv"

RATING_FILES = {
    "A": ORIGINALS_DIR / "wave4_reviewer_a_ratings_FINAL.json",
    "B": ORIGINALS_DIR / "wave4_reviewer_b_ratings_FINAL.json",
}

PACKET_FILES = {
    "A": ROOT / "ratings" / "reviewer_a" / "wave4_reviewer_a_blinded.html",
    "B": ROOT / "ratings" / "reviewer_b" / "wave4_reviewer_b_blinded.html",
}

REQUIRED_TOP_LEVEL_KEYS = {
    "schema_version",
    "status",
    "reviewer_code",
    "reviewer_name",
    "packet_id",
    "packet_sha256",
    "codebook_sha256",
    "exported_at",
    "ratings",
}

REQUIRED_RATING_KEYS = {
    "response_id",
    "packet_position",
    "movement_disposition",
    "primary_endpoint",
    "decisive_quote",
    "material_unresolved_input",
    "rationale",
    "ambiguity_flag",
    "reviewed_at",
}

LABELS = {
    "primary_endpoint": ["yes", "no", "unclear"],
    "movement_disposition": [
        "explicit_clearance",
        "conditional_clearance",
        "withhold_clearance",
        "unclear_or_nonresponsive",
    ],
    "ambiguity_flag": ["yes", "no"],
}

BOOTSTRAP_SEED = 20260831
BOOTSTRAP_REPLICATES = 100_000


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def parse_timestamp(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def extract_packet(path: Path) -> dict:
    html = path.read_text(encoding="utf-8")
    match = re.search(r"const PACKET = ([\s\S]*?);\nconst STORAGE_KEY =", html)
    if not match:
        raise ValueError(f"Embedded packet not found in {path}")
    return json.loads(match.group(1).replace(r"\u003c", "<"))


def normalize_quote_text(value: str) -> str:
    value = value.replace("“", '"').replace("”", '"')
    value = value.replace("‘", "'").replace("’", "'")
    value = re.sub(r"[\*_`>#]", "", value)
    value = value.replace(r"\n", "\n")
    value = re.sub(r"\s+", " ", value).strip()
    value = re.sub(r"^[\"']+|[\"']+$", "", value).strip()
    return value.casefold()


def quote_segments_match(quote: str, response: str) -> bool:
    response_normalized = normalize_quote_text(response)
    parts = [
        normalize_quote_text(part)
        for part in re.split(r"(?:\[…\]|\[\.\.\.\]|\.{3}|…)", quote)
    ]
    parts = [part for part in parts if len(part) >= 4]
    return bool(parts) and all(part in response_normalized for part in parts)


def strict_validate(
    reviewer_code: str,
    data: dict,
    packet: dict,
    packet_manifest: dict,
    lock_entry: dict,
) -> dict:
    errors: list[str] = []
    warnings: list[str] = []

    if set(data) != REQUIRED_TOP_LEVEL_KEYS:
        errors.append("Top-level keys do not match the frozen export schema")
    if data.get("schema_version") != "1.0-wave4-human-ratings":
        errors.append("Unexpected schema_version")
    if data.get("status") != "complete":
        errors.append("Status is not complete")
    if data.get("reviewer_code") != reviewer_code:
        errors.append("Reviewer code does not match the file assignment")
    if not str(data.get("reviewer_name", "")).strip():
        errors.append("Reviewer name is blank")

    ratings = data.get("ratings", [])
    if len(ratings) != 96:
        errors.append(f"Expected 96 ratings; found {len(ratings)}")

    response_ids = [row.get("response_id") for row in ratings]
    if len(set(response_ids)) != len(response_ids):
        errors.append("Duplicate response_id values are present")
    if any(not re.fullmatch(r"W4-[A-F0-9]{12}", str(value)) for value in response_ids):
        errors.append("At least one response_id has an invalid format")

    positions = [row.get("packet_position") for row in ratings]
    if sorted(positions) != list(range(1, 97)):
        errors.append("packet_position is not a unique permutation of 1 through 96")

    for index, row in enumerate(ratings, start=1):
        if set(row) != REQUIRED_RATING_KEYS:
            errors.append(f"Rating row {index} keys do not match the frozen schema")
        for key in REQUIRED_RATING_KEYS - {"packet_position"}:
            if row.get(key) is None or not str(row.get(key)).strip():
                errors.append(f"Rating row {index} has a blank required field: {key}")
        for field, allowed in LABELS.items():
            if row.get(field) not in allowed:
                errors.append(f"Rating row {index} has an invalid {field} label")
        try:
            parse_timestamp(str(row.get("reviewed_at")))
        except (TypeError, ValueError):
            errors.append(f"Rating row {index} has an invalid reviewed_at timestamp")

    expected_packet = next(
        item for item in packet_manifest["reviewers"] if item["reviewer_code"] == reviewer_code
    )
    if data.get("packet_id") != packet.get("packet_id") or data.get("packet_id") != expected_packet.get("packet_id"):
        errors.append("packet_id does not match the frozen packet")
    if data.get("packet_sha256") != packet.get("packet_sha256") or data.get("packet_sha256") != expected_packet.get("packet_sha256"):
        errors.append("packet_sha256 does not match the frozen packet")
    if data.get("codebook_sha256") != packet_manifest.get("codebook_sha256"):
        errors.append("codebook_sha256 does not match the frozen codebook")

    packet_by_id = {item["response_id"]: item for item in packet["items"]}
    if set(response_ids) != set(packet_by_id):
        errors.append("Rating response IDs do not equal the packet response IDs")

    file_hash = sha256_bytes(RATING_FILES[reviewer_code].read_bytes())
    if file_hash != lock_entry["sha256"]:
        errors.append("Locked rating file hash has changed")

    reviewed_at = [str(row["reviewed_at"]) for row in ratings]
    unique_reviewed_at = len(set(reviewed_at))
    all_reviewed_at_equal_export = all(value == data["exported_at"] for value in reviewed_at)
    if all_reviewed_at_equal_export:
        warnings.append(
            "Every reviewed_at timestamp equals exported_at; confirm how this rating file was produced before claiming item-level app timestamps."
        )

    exact_quote_misses = []
    normalized_segment_misses = []
    for row in ratings:
        response = packet_by_id[row["response_id"]]["response"]
        if row["decisive_quote"] not in response:
            exact_quote_misses.append(row["response_id"])
        if not quote_segments_match(row["decisive_quote"], response):
            normalized_segment_misses.append(row["response_id"])

    if normalized_segment_misses:
        warnings.append(
            "Some decisive_quote values could not be matched mechanically to the verbatim response after conservative formatting normalization; originals remain unchanged."
        )

    return {
        "valid": not errors,
        "errors": errors,
        "warnings": warnings,
        "rating_count": len(ratings),
        "unique_response_id_count": len(set(response_ids)),
        "packet_positions_complete": sorted(positions) == list(range(1, 97)),
        "packet_identity_matches": not any("packet_" in error for error in errors),
        "codebook_hash_matches": not any("codebook_sha256" in error for error in errors),
        "locked_sha256": file_hash,
        "reviewed_at": {
            "unique_count": unique_reviewed_at,
            "minimum": min(reviewed_at),
            "maximum": max(reviewed_at),
            "all_equal_exported_at": all_reviewed_at_equal_export,
        },
        "quote_traceability": {
            "exact_contiguous_matches": len(ratings) - len(exact_quote_misses),
            "exact_contiguous_miss_ids": exact_quote_misses,
            "normalized_segment_matches": len(ratings) - len(normalized_segment_misses),
            "normalized_segment_miss_ids": normalized_segment_misses,
            "note": "Mechanical matching is conservative and is not semantic adjudication.",
        },
    }


def agreement(rows_a: list[dict], rows_b_by_id: dict[str, dict], field: str) -> dict:
    categories = LABELS[field]
    matrix = {row: {column: 0 for column in categories} for row in categories}
    disagreements = []

    for row_a in rows_a:
        row_b = rows_b_by_id[row_a["response_id"]]
        label_a = row_a[field]
        label_b = row_b[field]
        matrix[label_a][label_b] += 1
        if label_a != label_b:
            disagreements.append(
                {
                    "response_id": row_a["response_id"],
                    "reviewer_a": label_a,
                    "reviewer_b": label_b,
                }
            )

    n = len(rows_a)
    row_totals = {category: sum(matrix[category].values()) for category in categories}
    column_totals = {
        category: sum(matrix[row][category] for row in categories) for category in categories
    }
    agree_count = sum(matrix[category][category] for category in categories)
    observed = agree_count / n
    expected = sum(
        (row_totals[category] / n) * (column_totals[category] / n)
        for category in categories
    )
    kappa = None if math.isclose(expected, 1.0) else (observed - expected) / (1 - expected)

    return {
        "field": field,
        "categories_in_matrix_order": categories,
        "n": n,
        "agreement_count": agree_count,
        "disagreement_count": n - agree_count,
        "raw_agreement": observed,
        "chance_expected_agreement": expected,
        "cohens_kappa_unweighted": kappa,
        "reviewer_a_counts": row_totals,
        "reviewer_b_counts": column_totals,
        "confusion_matrix_reviewer_a_rows_reviewer_b_columns": matrix,
        "disagreements": sorted(disagreements, key=lambda row: row["response_id"]),
    }


def kappa_from_pairs(pairs: list[tuple[str, str]], categories: list[str]) -> float:
    n = len(pairs)
    rows = Counter(left for left, _ in pairs)
    columns = Counter(right for _, right in pairs)
    observed = sum(left == right for left, right in pairs) / n
    expected = sum((rows[category] / n) * (columns[category] / n) for category in categories)
    if math.isclose(expected, 1.0):
        return math.nan
    return (observed - expected) / (1 - expected)


def quantile_type7(values: list[float], probability: float) -> float:
    if not values:
        return math.nan
    position = (len(values) - 1) * probability
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return values[lower]
    weight = position - lower
    return values[lower] * (1 - weight) + values[upper] * weight


def primary_kappa_intervals(
    rows_a: list[dict], rows_b_by_id: dict[str, dict], estimate: float
) -> dict:
    categories = LABELS["primary_endpoint"]
    pairs = [
        (row["primary_endpoint"], rows_b_by_id[row["response_id"]]["primary_endpoint"])
        for row in rows_a
    ]
    n = len(pairs)
    rng = random.Random(BOOTSTRAP_SEED)
    bootstraps = []
    for _ in range(BOOTSTRAP_REPLICATES):
        sample = [pairs[rng.randrange(n)] for _ in range(n)]
        value = kappa_from_pairs(sample, categories)
        if not math.isnan(value):
            bootstraps.append(value)
    bootstraps.sort()

    percentile_interval = [
        quantile_type7(bootstraps, 0.025),
        quantile_type7(bootstraps, 0.975),
    ]

    less = sum(value < estimate for value in bootstraps)
    equal = sum(math.isclose(value, estimate, rel_tol=0, abs_tol=1e-15) for value in bootstraps)
    proportion_below = (less + 0.5 * equal) / len(bootstraps)
    proportion_below = min(max(proportion_below, 1e-12), 1 - 1e-12)
    normal = NormalDist()
    z0 = normal.inv_cdf(proportion_below)

    jackknife = [
        kappa_from_pairs(pairs[:index] + pairs[index + 1 :], categories)
        for index in range(n)
    ]
    jackknife_mean = sum(jackknife) / len(jackknife)
    differences = [jackknife_mean - value for value in jackknife]
    numerator = sum(value**3 for value in differences)
    denominator = 6 * (sum(value**2 for value in differences) ** 1.5)
    acceleration = 0.0 if math.isclose(denominator, 0.0) else numerator / denominator

    adjusted_probabilities = []
    for alpha in (0.025, 0.975):
        z_alpha = normal.inv_cdf(alpha)
        adjusted_z = z0 + (z0 + z_alpha) / (1 - acceleration * (z0 + z_alpha))
        adjusted_probabilities.append(normal.cdf(adjusted_z))
    bca_interval = [
        quantile_type7(bootstraps, adjusted_probabilities[0]),
        quantile_type7(bootstraps, adjusted_probabilities[1]),
    ]

    matrix = Counter(pairs)
    probabilities = {
        (row, column): matrix[(row, column)] / n
        for row in categories
        for column in categories
    }
    row_probabilities = {
        row: sum(probabilities[(row, column)] for column in categories)
        for row in categories
    }
    column_probabilities = {
        column: sum(probabilities[(row, column)] for row in categories)
        for column in categories
    }
    observed = sum(probabilities[(category, category)] for category in categories)
    expected = sum(
        row_probabilities[category] * column_probabilities[category]
        for category in categories
    )
    gradients = {}
    for row in categories:
        for column in categories:
            d_observed = 1.0 if row == column else 0.0
            d_expected = column_probabilities[row] + row_probabilities[column]
            gradients[(row, column)] = (
                d_observed + (estimate - 1) * d_expected
            ) / (1 - expected)
    mean_gradient = sum(
        probabilities[cell] * gradients[cell] for cell in probabilities
    )
    asymptotic_variance = (
        sum(probabilities[cell] * gradients[cell] ** 2 for cell in probabilities)
        - mean_gradient**2
    ) / n
    asymptotic_se = math.sqrt(asymptotic_variance)
    z_975 = normal.inv_cdf(0.975)
    asymptotic_interval = [
        estimate - z_975 * asymptotic_se,
        estimate + z_975 * asymptotic_se,
    ]

    return {
        "primary_method": "paired response-level nonparametric BCa bootstrap",
        "bootstrap_seed": BOOTSTRAP_SEED,
        "bootstrap_replicates_requested": BOOTSTRAP_REPLICATES,
        "bootstrap_replicates_valid": len(bootstraps),
        "bca_95_percent_ci": bca_interval,
        "bca_bias_correction_z0": z0,
        "bca_acceleration": acceleration,
        "percentile_bootstrap_95_percent_ci_sensitivity": percentile_interval,
        "multinomial_delta_method_standard_error_sensitivity": asymptotic_se,
        "multinomial_delta_method_95_percent_ci_sensitivity": asymptotic_interval,
        "note": "Each resample preserves the two reviewer labels attached to the same anonymous response ID.",
    }


def main() -> None:
    lock = read_json(LOCK_PATH)
    lock_by_reviewer = {entry["reviewer_code"]: entry for entry in lock["files"]}
    packet_manifest = read_json(PACKET_MANIFEST_PATH)
    codebook_hash = sha256_bytes(CODEBOOK_PATH.read_bytes())
    if codebook_hash != packet_manifest["codebook_sha256"]:
        raise SystemExit("Frozen codebook hash does not match the packet manifest")

    data = {code: read_json(path) for code, path in RATING_FILES.items()}
    packets = {code: extract_packet(path) for code, path in PACKET_FILES.items()}
    validation = {
        code: strict_validate(
            code, data[code], packets[code], packet_manifest, lock_by_reviewer[code]
        )
        for code in ("A", "B")
    }
    if not all(item["valid"] for item in validation.values()):
        raise SystemExit(json.dumps(validation, indent=2))

    ids_a = {row["response_id"] for row in data["A"]["ratings"]}
    ids_b = {row["response_id"] for row in data["B"]["ratings"]}
    if ids_a != ids_b or len(ids_a) != 96:
        raise SystemExit("The two reviewers do not have the same 96 response IDs")

    rows_b_by_id = {row["response_id"]: row for row in data["B"]["ratings"]}
    results = {
        field: agreement(data["A"]["ratings"], rows_b_by_id, field)
        for field in LABELS
    }
    primary = results["primary_endpoint"]
    primary["cohens_kappa_95_percent_confidence_interval"] = primary_kappa_intervals(
        data["A"]["ratings"], rows_b_by_id, primary["cohens_kappa_unweighted"]
    )

    ordinary_cross_field_map = {
        "explicit_clearance": "yes",
        "conditional_clearance": "yes",
        "withhold_clearance": "no",
        "unclear_or_nonresponsive": "unclear",
    }
    cross_field_flags = {}
    for code in ("A", "B"):
        cross_field_flags[code] = [
            {
                "response_id": row["response_id"],
                "movement_disposition": row["movement_disposition"],
                "primary_endpoint": row["primary_endpoint"],
                "ordinary_mapping_primary_endpoint": ordinary_cross_field_map[
                    row["movement_disposition"]
                ],
            }
            for row in data[code]["ratings"]
            if ordinary_cross_field_map[row["movement_disposition"]]
            != row["primary_endpoint"]
        ]

    report = {
        "schema_version": "1.0-wave4-pre-adjudication-human-agreement",
        "status": "agreement_calculated_from_locked_originals_before_adjudication",
        "generated_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "blinding_status": "product identity not opened during this analysis",
        "join_key": "anonymous response_id",
        "source_lock": {
            "path": str(LOCK_PATH.relative_to(ROOT)),
            "status": lock["status"],
            "locked_at_utc": lock["locked_at_utc"],
            "reviewer_a_sha256": lock_by_reviewer["A"]["sha256"],
            "reviewer_b_sha256": lock_by_reviewer["B"]["sha256"],
            "codebook_sha256": codebook_hash,
        },
        "validation": {
            "reviewers": validation,
            "same_96_anonymous_response_ids": True,
            "label_domain_source": "frozen codebook plus frozen reviewer packet controls for ambiguity_flag yes/no",
            "cross_field_consistency_queries_not_recoded": cross_field_flags,
            "workflow_confirmation_required": {
                "reviewer_b_all_reviewed_at_equal_exported_at": validation["B"][
                    "reviewed_at"
                ]["all_equal_exported_at"],
                "question": "Confirm that Reviewer B independently reviewed all 96 responses as a human and explain whether the final JSON was converted or regenerated outside the reviewer app.",
            },
        },
        "agreement": results,
        "interpretation_guardrails": [
            "These are original pre-adjudication human labels; no label was changed.",
            "No response was semantically rescored by this script.",
            "The ambiguity-flag kappa is prevalence-degenerate because Reviewer A used only no; report its raw agreement descriptively.",
            "Product-level outcome analysis remains deferred until workflow confirmation and blinded human adjudication are complete.",
        ],
    }

    ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_JSON.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    with DISAGREEMENT_CSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=["response_id", "reviewer_a", "reviewer_b"]
        )
        writer.writeheader()
        writer.writerows(primary["disagreements"])

    print(
        json.dumps(
            {
                "output_json": str(OUTPUT_JSON),
                "disagreement_csv": str(DISAGREEMENT_CSV),
                "primary_raw_agreement": primary["raw_agreement"],
                "primary_cohens_kappa": primary["cohens_kappa_unweighted"],
                "primary_bca_95_percent_ci": primary[
                    "cohens_kappa_95_percent_confidence_interval"
                ]["bca_95_percent_ci"],
                "primary_disagreement_count": primary["disagreement_count"],
                "workflow_confirmation_required": report["validation"][
                    "workflow_confirmation_required"
                ],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
