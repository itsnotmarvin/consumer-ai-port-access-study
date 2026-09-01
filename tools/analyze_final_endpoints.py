#!/usr/bin/env python3
"""Join frozen human endpoints to the administrative key and summarize Wave 4.

The human labels are already final and frozen when this script runs. This code
only validates identifiers, joins administrative metadata, and calculates
descriptive counts, rates, and Wilson intervals. It never reads or interprets
response text.
"""

from __future__ import annotations

import csv
import hashlib
import itertools
import json
import math
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "analysis"
TABLES = ANALYSIS / "final_tables"

BLINDED_DATASET = ANALYSIS / "final_human_endpoints_blinded.json"
BLINDED_FREEZE = ANALYSIS / "FINAL_HUMAN_ENDPOINTS_BLINDED_FREEZE.json"
BLINDING_KEY = ANALYSIS / "ADMIN_blinding_key.json"
DESIGN = ROOT / "design.json"
GOLD = ROOT / "gold_dispositions.json"
COLLECTION_MANIFEST = ROOT / "collection_manifest.csv"
CODEBOOK = ROOT / "human_rating_codebook.json"
HUMAN_AGREEMENT = ANALYSIS / "human_agreement_pre_adjudication.json"

UNBLINDED_JSON = ANALYSIS / "final_endpoint_dataset_unblinded.json"
UNBLINDED_CSV = ANALYSIS / "final_endpoint_dataset_unblinded.csv"
RESULTS_JSON = ANALYSIS / "final_results.json"
RESULTS_FREEZE = ANALYSIS / "FINAL_RESULTS_FREEZE.json"

PRODUCT_LABELS = {
    "chatgpt": "ChatGPT",
    "claude": "Claude",
    "copilot": "Copilot",
    "gemini": "Gemini",
}

# These are the two route-specific scenario families in the frozen design.
# Other scenarios are not forced into a route category that was not randomized.
ROUTE_PATHS = {
    "s2_dimensions_local_access": {
        "route_path_id": "north_avenue_cr624_direct_terminal_access",
        "route_path_label": "U.S. 1&9 → North Avenue / CR 624 → direct local terminal access",
    },
    "s4_oversize_mutable_port_st": {
        "route_path_id": "port_street_brewster_marlin",
        "route_path_label": "Port Street between Brewster Road and Marlin Street",
    },
}

UNBLINDED_FIELDS = [
    "response_id",
    "run_id",
    "product",
    "product_display",
    "scenario_id",
    "scenario_title",
    "variant",
    "repetition",
    "ambiguity_type",
    "authority_count_band",
    "route_path_id",
    "route_path_label",
    "prompt_path",
    "prompt_sha256",
    "response_path",
    "response_sha256",
    "reviewer_a_primary_endpoint",
    "reviewer_b_primary_endpoint",
    "original_reviewers_agree",
    "adjudicated_primary_endpoint",
    "final_primary_endpoint",
    "final_label_source",
]

SUMMARY_FIELDS = [
    "n",
    "yes",
    "no",
    "unclear",
    "yes_rate",
    "yes_rate_percent",
    "wilson_95_lower",
    "wilson_95_upper",
    "wilson_95_lower_percent",
    "wilson_95_upper_percent",
]


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_csv(path: Path, rows: list[dict], fieldnames: list[str] | None = None) -> None:
    if fieldnames is None:
        if not rows:
            raise ValueError(f"Cannot infer columns for empty CSV: {path}")
        fieldnames = list(rows[0])
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def wilson_interval(yes: int, n: int, z: float = 1.959963984540054) -> tuple[float, float]:
    if n == 0:
        return (math.nan, math.nan)
    p = yes / n
    denominator = 1 + z * z / n
    center = (p + z * z / (2 * n)) / denominator
    half_width = z * math.sqrt((p * (1 - p) + z * z / (4 * n)) / n) / denominator
    lower = max(0.0, center - half_width)
    upper = min(1.0, center + half_width)
    # Normalize floating-point dust at the mathematical boundaries.
    if abs(lower) < 1e-15:
        lower = 0.0
    if abs(upper - 1.0) < 1e-15:
        upper = 1.0
    return (lower, upper)


def endpoint_summary(rows: list[dict]) -> dict:
    counts = Counter(row["final_primary_endpoint"] for row in rows)
    n = len(rows)
    yes = counts["yes"]
    lower, upper = wilson_interval(yes, n)
    return {
        "n": n,
        "yes": yes,
        "no": counts["no"],
        "unclear": counts["unclear"],
        "yes_rate": yes / n if n else None,
        "yes_rate_percent": 100 * yes / n if n else None,
        "wilson_95_lower": lower if n else None,
        "wilson_95_upper": upper if n else None,
        "wilson_95_lower_percent": 100 * lower if n else None,
        "wilson_95_upper_percent": 100 * upper if n else None,
    }


def grouped_summary(rows: list[dict], keys: list[str], order: dict[str, list] | None = None) -> list[dict]:
    groups: dict[tuple, list[dict]] = defaultdict(list)
    for row in rows:
        groups[tuple(row[key] for key in keys)].append(row)

    def sort_key(values: tuple) -> tuple:
        ranked = []
        for key, value in zip(keys, values):
            if order and key in order:
                ranked.append(order[key].index(value))
            else:
                ranked.append(value)
        return tuple(ranked)

    output = []
    for values in sorted(groups, key=sort_key):
        group_rows = groups[values]
        output.append({**dict(zip(keys, values)), **endpoint_summary(group_rows)})
    return output


def lower_scenario_id(value: str) -> str:
    return value.lower()


def main() -> None:
    errors: list[str] = []
    blinded = read_json(BLINDED_DATASET)
    blinded_freeze = read_json(BLINDED_FREEZE)
    key = read_json(BLINDING_KEY)
    design = read_json(DESIGN)
    gold = read_json(GOLD)
    agreement = read_json(HUMAN_AGREEMENT)

    # Verify the exact blinded endpoint and all metadata bindings before joining.
    if sha256_file(BLINDED_DATASET) != blinded_freeze["outputs"]["final_json_sha256"]:
        errors.append("Frozen blinded endpoint JSON hash changed")
    if sha256_file(DESIGN) != key["design_sha256"]:
        errors.append("Design hash does not match the blinding key")
    if sha256_file(GOLD) != key["gold_dispositions_sha256"]:
        errors.append("Gold-dispositions hash does not match the blinding key")
    if sha256_file(COLLECTION_MANIFEST) != key["collection_manifest_sha256"]:
        errors.append("Collection-manifest hash does not match the blinding key")
    if sha256_file(CODEBOOK) != key["codebook_sha256"]:
        errors.append("Human-rating codebook hash does not match the blinding key")
    if key.get("status") != "locked_before_human_rating":
        errors.append("Blinding key status is unexpected")
    if blinded.get("status") != "complete_and_product_blinded":
        errors.append("Blinded endpoint dataset status is unexpected")

    blinded_rows = blinded.get("rows")
    if not isinstance(blinded_rows, list):
        errors.append("Blinded endpoint rows is not an array")
        blinded_rows = []
    raw_blinded_ids = [row.get("response_id") for row in blinded_rows if isinstance(row, dict)]
    if len(blinded_rows) != 96 or blinded.get("row_count") != 96:
        errors.append("Blinded endpoint raw row count or declared row_count is not 96")
    if len(raw_blinded_ids) != 96 or len(set(raw_blinded_ids)) != 96:
        errors.append("Blinded endpoint rows do not contain exactly 96 unique response IDs")
    if any(row.get("final_primary_endpoint") not in {"yes", "no", "unclear"} for row in blinded_rows if isinstance(row, dict)):
        errors.append("Blinded endpoint rows contain an invalid final label")

    labels_by_id = {row["response_id"]: row for row in blinded_rows if isinstance(row, dict) and "response_id" in row}
    key_by_id = {row["response_id"]: row for row in key["items"]}
    if len(labels_by_id) != 96 or len(key_by_id) != 96:
        errors.append("Expected 96 unique response IDs in both blinded labels and administrative key")
    if set(labels_by_id) != set(key_by_id):
        errors.append("Blinded endpoint IDs and administrative-key IDs do not match")

    products = design["primary_surfaces"]
    scenario_order = [lower_scenario_id(row["scenario_id"]) for row in gold["scenarios"]]
    variants = ["neutral", "pressure"]
    repetitions = [1, 2]
    expected_cells = set(itertools.product(products, scenario_order, variants, repetitions))
    observed_cells = {
        (row["product"], row["scenario_id"], row["variant"], row["repetition"])
        for row in key["items"]
    }
    if observed_cells != expected_cells or len(observed_cells) != 96:
        errors.append("Administrative key is not the exact frozen 4 × 6 × 2 × 2 factorial")
    if set(products) != set(PRODUCT_LABELS):
        errors.append("Frozen product set is not exactly ChatGPT, Claude, Copilot, and Gemini")
    if errors:
        raise SystemExit("Final endpoint analysis validation failed:\n- " + "\n- ".join(errors))

    scenario_by_id = {lower_scenario_id(row["scenario_id"]): row for row in gold["scenarios"]}
    joined_rows: list[dict] = []
    for response_id in sorted(labels_by_id):
        label = labels_by_id[response_id]
        admin = key_by_id[response_id]
        scenario = scenario_by_id[admin["scenario_id"]]
        route = ROUTE_PATHS.get(admin["scenario_id"], {"route_path_id": "", "route_path_label": ""})
        joined_rows.append({
            "response_id": response_id,
            "run_id": admin["run_id"],
            "product": admin["product"],
            "product_display": PRODUCT_LABELS[admin["product"]],
            "scenario_id": admin["scenario_id"],
            "scenario_title": scenario["title"],
            "variant": admin["variant"],
            "repetition": admin["repetition"],
            "ambiguity_type": scenario["ambiguity_type"],
            "authority_count_band": scenario["authority_count_band"],
            "route_path_id": route["route_path_id"],
            "route_path_label": route["route_path_label"],
            "prompt_path": admin["prompt_path"],
            "prompt_sha256": admin["prompt_sha256"],
            "response_path": admin["response_path"],
            "response_sha256": admin["response_sha256"],
            "reviewer_a_primary_endpoint": label["reviewer_a_primary_endpoint"],
            "reviewer_b_primary_endpoint": label["reviewer_b_primary_endpoint"],
            "original_reviewers_agree": label["original_reviewers_agree"],
            "adjudicated_primary_endpoint": label["adjudicated_primary_endpoint"],
            "final_primary_endpoint": label["final_primary_endpoint"],
            "final_label_source": label["final_label_source"],
        })

    order = {
        "product": products,
        "product_display": [PRODUCT_LABELS[value] for value in products],
        "scenario_id": scenario_order,
        "variant": variants,
        "repetition": repetitions,
        "route_path_id": [ROUTE_PATHS[scenario]["route_path_id"] for scenario in ROUTE_PATHS],
    }

    route_rows = [row for row in joined_rows if row["route_path_id"]]
    other_scenario_rows = [row for row in joined_rows if not row["route_path_id"]]
    tables = {
        "overall": [{"scope": "all_96_captured_responses", **endpoint_summary(joined_rows)}],
        "by_product": grouped_summary(joined_rows, ["product", "product_display"], order),
        "by_scenario": grouped_summary(joined_rows, ["scenario_id", "scenario_title"], order),
        "by_variant": grouped_summary(joined_rows, ["variant"], order),
        "by_repetition": grouped_summary(joined_rows, ["repetition"], order),
        "by_ambiguity_type": grouped_summary(joined_rows, ["ambiguity_type"]),
        "by_authority_complexity": grouped_summary(joined_rows, ["authority_count_band"]),
        "by_route_path_subset": grouped_summary(route_rows, ["route_path_id", "route_path_label"], order),
        "route_scenarios_vs_other_scenarios": [
            {"scenario_group": "S2 and S4 route-specific scenarios", **endpoint_summary(route_rows)},
            {"scenario_group": "S1, S3, S5, and S6 other scenarios", **endpoint_summary(other_scenario_rows)},
        ],
        "product_by_scenario": grouped_summary(joined_rows, ["product", "product_display", "scenario_id", "scenario_title"], order),
        "product_by_route_path_subset": grouped_summary(route_rows, ["product", "product_display", "route_path_id", "route_path_label"], order),
        "product_by_variant": grouped_summary(joined_rows, ["product", "product_display", "variant"], order),
    }

    # Pair repetition 1 and 2 within each product × scenario × pressure cell.
    repetition_cells: dict[tuple, dict[int, dict]] = defaultdict(dict)
    for row in joined_rows:
        key_tuple = (row["product"], row["scenario_id"], row["variant"])
        repetition_cells[key_tuple][row["repetition"]] = row
    repetition_pairs = []
    for key_tuple in sorted(repetition_cells):
        by_rep = repetition_cells[key_tuple]
        if set(by_rep) != {1, 2}:
            raise SystemExit(f"Incomplete repetition pair: {key_tuple}")
        first = by_rep[1]["final_primary_endpoint"]
        second = by_rep[2]["final_primary_endpoint"]
        repetition_pairs.append({
            "product": key_tuple[0],
            "product_display": PRODUCT_LABELS[key_tuple[0]],
            "scenario_id": key_tuple[1],
            "variant": key_tuple[2],
            "repetition_1_label": first,
            "repetition_2_label": second,
            "pattern": f"{first}_to_{second}",
            "same_label": first == second,
        })
    pattern_counts = Counter(row["pattern"] for row in repetition_pairs)
    repetition_pair_summary = {
        "pair_count": len(repetition_pairs),
        "same_label_count": sum(row["same_label"] for row in repetition_pairs),
        "same_label_rate": sum(row["same_label"] for row in repetition_pairs) / len(repetition_pairs),
        "pattern_counts": dict(sorted(pattern_counts.items())),
        "interpretation_boundary": "These are repeated product responses, not independent people; this is a descriptive stability check, not inter-rater agreement.",
    }

    yes_rows = [row for row in joined_rows if row["final_primary_endpoint"] == "yes"]
    yes_by_scenario = Counter(row["scenario_id"] for row in yes_rows)
    yes_by_product = Counter(row["product"] for row in yes_rows)
    yes_by_variant = Counter(row["variant"] for row in yes_rows)
    yes_by_repetition = Counter(row["repetition"] for row in yes_rows)
    max_scenario_count = max(yes_by_scenario.values(), default=0)
    max_product_count = max(yes_by_product.values(), default=0)
    concentration = {
        "total_yes": len(yes_rows),
        "scenarios_with_at_least_one_yes": sum(yes_by_scenario[scenario] > 0 for scenario in scenario_order),
        "products_with_at_least_one_yes": sum(yes_by_product[product] > 0 for product in products),
        "variants_with_at_least_one_yes": sum(yes_by_variant[variant] > 0 for variant in variants),
        "repetitions_with_at_least_one_yes": sum(yes_by_repetition[rep] > 0 for rep in repetitions),
        "yes_by_scenario": dict(yes_by_scenario),
        "yes_by_product": dict(yes_by_product),
        "yes_by_variant": dict(yes_by_variant),
        "yes_by_repetition": {str(key): value for key, value in sorted(yes_by_repetition.items())},
        "largest_single_scenario_yes_count": max_scenario_count,
        "largest_single_scenario_share_of_all_yes": max_scenario_count / len(yes_rows) if yes_rows else None,
        "largest_single_product_yes_count": max_product_count,
        "largest_single_product_share_of_all_yes": max_product_count / len(yes_rows) if yes_rows else None,
        "route_specific_subset_yes": sum(row["final_primary_endpoint"] == "yes" for row in route_rows),
        "route_specific_subset_n": len(route_rows),
    }

    source_hashes = {
        "final_blinded_endpoint_sha256": sha256_file(BLINDED_DATASET),
        "final_blinded_freeze_sha256": sha256_file(BLINDED_FREEZE),
        "admin_blinding_key_sha256": sha256_file(BLINDING_KEY),
        "design_sha256": sha256_file(DESIGN),
        "gold_dispositions_sha256": sha256_file(GOLD),
        "collection_manifest_sha256": sha256_file(COLLECTION_MANIFEST),
        "codebook_sha256": sha256_file(CODEBOOK),
        "human_agreement_pre_adjudication_sha256": sha256_file(HUMAN_AGREEMENT),
    }
    unblinded_dataset = {
        "schema_version": "1.0-wave4-final-endpoint-dataset-unblinded",
        "status": "complete",
        "created_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "row_count": len(joined_rows),
        "join_key": "response_id",
        "source_hashes": source_hashes,
        "rows": joined_rows,
    }
    write_json(UNBLINDED_JSON, unblinded_dataset)
    write_csv(UNBLINDED_CSV, joined_rows, UNBLINDED_FIELDS)

    TABLES.mkdir(parents=True, exist_ok=True)
    table_paths: dict[str, str] = {}
    for name, table_rows in tables.items():
        path = TABLES / f"{name}.csv"
        write_csv(path, table_rows)
        table_paths[name] = str(path.relative_to(ROOT))
    write_csv(TABLES / "repetition_pairs.csv", repetition_pairs)
    table_paths["repetition_pairs"] = str((TABLES / "repetition_pairs.csv").relative_to(ROOT))
    yes_case_fields = [
        "response_id", "run_id", "product", "product_display", "scenario_id",
        "scenario_title", "variant", "repetition", "route_path_id",
        "final_label_source", "reviewer_a_primary_endpoint",
        "reviewer_b_primary_endpoint", "adjudicated_primary_endpoint",
    ]
    write_csv(TABLES / "yes_endpoint_cases.csv", [{key: row[key] for key in yes_case_fields} for row in yes_rows], yes_case_fields)
    table_paths["yes_endpoint_cases"] = str((TABLES / "yes_endpoint_cases.csv").relative_to(ROOT))
    adjudicated_rows = [row for row in joined_rows if row["final_label_source"] == "human_adjudication"]
    write_csv(TABLES / "adjudicated_cases_unblinded.csv", [{key: row[key] for key in yes_case_fields} for row in adjudicated_rows], yes_case_fields)
    table_paths["adjudicated_cases_unblinded"] = str((TABLES / "adjudicated_cases_unblinded.csv").relative_to(ROOT))

    results = {
        "schema_version": "1.0-wave4-final-results",
        "status": "complete",
        "created_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "research_question": design["locked_research_question"],
        "primary_endpoint": design["primary_endpoint"],
        "design": {
            "formula": design["design"]["formula"],
            "products": [{"id": product, "display": PRODUCT_LABELS[product]} for product in products],
            "scenario_count": len(scenario_order),
            "pressure_variants": variants,
            "repetitions": repetitions,
            "planned_runs": design["design"]["planned_primary_runs"],
            "completed_and_scored_runs": len(joined_rows),
        },
        "source_hashes": source_hashes,
        "primary_human_agreement": {
            "source": "analysis/human_agreement_pre_adjudication.json",
            "n": agreement["agreement"]["primary_endpoint"]["n"],
            "agreement_count": agreement["agreement"]["primary_endpoint"]["agreement_count"],
            "raw_agreement": agreement["agreement"]["primary_endpoint"]["raw_agreement"],
            "cohens_kappa_unweighted": agreement["agreement"]["primary_endpoint"]["cohens_kappa_unweighted"],
            "bca_95_percent_ci": agreement["agreement"]["primary_endpoint"]["cohens_kappa_95_percent_confidence_interval"]["bca_95_percent_ci"],
            "timing": "calculated from the two locked original human ratings before adjudication and before product unblinding",
        },
        "adjudication": {
            "disagreement_count": 5,
            "final_adjudicated_label_counts": dict(Counter(row["final_primary_endpoint"] for row in adjudicated_rows)),
            "treatment": "The adjudicator supplied the final label for the five disagreements; these are not additional independent ratings.",
        },
        "uncertainty": {
            "interval": "two-sided 95% Wilson score interval for the observed yes proportion",
            "z": 1.959963984540054,
            "interpretation_boundary": "Intervals describe uncertainty around rates across these captured responses. Repeated runs are repeated stochastic outputs, not independent people or a prevalence sample of all logistics questions.",
            "pairwise_hypothesis_tests": "not performed",
        },
        "route_subset_definition": {
            "scope": "Only S2 and S4 are route-specific scenario families; the other four scenarios are not assigned to an invented route category.",
            "paths": ROUTE_PATHS,
        },
        "tables": tables,
        "repetition_pair_summary": repetition_pair_summary,
        "concentration": concentration,
        "machine_readable_files": table_paths,
        "interpretation_guardrails": [
            "Report scenarios separately before interpreting the aggregate.",
            "The 15/96 overall rate is not a general logistics prevalence estimate.",
            "Product comparisons are descriptive and secondary; no provider ranking or pairwise significance claim is made.",
            "No final unclear labels occurred; every response remains in the 96-response denominator.",
            "The human labels were frozen before product identity was joined.",
        ],
    }
    write_json(RESULTS_JSON, results)

    output_paths = [UNBLINDED_JSON, UNBLINDED_CSV, RESULTS_JSON, *sorted(TABLES.glob("*.csv"))]
    freeze = {
        "schema_version": "1.0-wave4-final-results-freeze",
        "status": "frozen_after_product_unblinding",
        "frozen_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "source_hashes": source_hashes,
        "outputs": [
            {"path": str(path.relative_to(ROOT)), "sha256": sha256_file(path), "size_bytes": path.stat().st_size}
            for path in output_paths
        ],
        "primary_result": endpoint_summary(joined_rows),
        "guardrails": results["interpretation_guardrails"],
    }
    write_json(RESULTS_FREEZE, freeze)

    for path in [*output_paths, RESULTS_FREEZE]:
        path.chmod(0o444)

    print(json.dumps({
        "status": "complete",
        "overall": tables["overall"][0],
        "by_product": tables["by_product"],
        "by_scenario": tables["by_scenario"],
        "by_variant": tables["by_variant"],
        "by_repetition": tables["by_repetition"],
        "by_route_path_subset": tables["by_route_path_subset"],
        "repetition_pair_summary": repetition_pair_summary,
        "concentration": concentration,
        "results_path": str(RESULTS_JSON),
        "freeze_path": str(RESULTS_FREEZE),
    }, indent=2))


if __name__ == "__main__":
    main()
