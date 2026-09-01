# Provenance

This page maps the full evidence trail for the experiment.

The canonical files remain in their original locations. They were not copied or moved into this folder because several are frozen by hashes, refer to one another by path, or preserve the historical order of the work.

## 1. Study plan frozen before collection

| Record | Purpose |
|---|---|
| [`design.json`](../design.json) | Research question, 96-cell design, products, repetitions, endpoint, and collection rules |
| [`protocol_lock.json`](../protocol_lock.json) | Pre-collection hashes for the design, evidence lock, gold dispositions, codebook, prompts, and original schedule |
| [`evidence_lock.json`](../evidence_lock.json) | Exact external evidence commit, retained source hashes, and evidence boundary |
| [`gold_dispositions.json`](../gold_dispositions.json) | Frozen reference decision for each of the six scenarios |
| [`docs/GOLD_DISPOSITIONS.md`](../docs/GOLD_DISPOSITIONS.md) | Plain-language explanation of the six reference decisions |
| [`human_rating_codebook.json`](../human_rating_codebook.json) | Rules used by both original reviewers |
| [`prompts/`](../prompts/) | The 12 exact prompt texts |
| [`docs/STUDY_WORKFLOW.md`](../docs/STUDY_WORKFLOW.md) | Step-by-step study workflow from protocol lock through final tables |

The external evidence source is the public [`last-mile-drayage-pilot`](https://github.com/itsnotmarvin/last-mile-drayage-pilot/tree/7fe49ebb0fc8376f0f183e1f614c06d284c13343) repository at commit `7fe49ebb0fc8376f0f183e1f614c06d284c13343`.

## 2. Collection record

| Record | Purpose |
|---|---|
| [`collection_manifest.csv`](../collection_manifest.csv) | Complete 96-row collection matrix |
| [`outputs/`](../outputs/) | All 96 verbatim captured responses |
| [`capture_metadata/`](../capture_metadata/) | Product mode, timing, attempt, source, and hashes for all 96 runs |

Known collection gaps are preserved rather than repaired after the fact. Four initial captures lack exact start timestamps. Six retained cells used a second attempt, but the failed first-attempt artifacts and reasons were not retained. The original `collection_manifest_initial_schedule.csv` is named and hashed in `protocol_lock.json` but is missing from the archive.

## 3. Independent human review

| Record | Purpose |
|---|---|
| [`ratings/completed_originals/`](../ratings/completed_originals/) | Preserved original exports from Reviewer A and Reviewer B |
| [`analysis/review_packet_manifest.json`](../analysis/review_packet_manifest.json) | Product-masked review packet manifest |
| [`analysis/PRE_ADJUDICATION_FREEZE.json`](../analysis/PRE_ADJUDICATION_FREEZE.json) | Lock over the original reviews before comparison and adjudication |
| [`analysis/human_agreement_pre_adjudication.json`](../analysis/human_agreement_pre_adjudication.json) | Agreement results from the two original reviews |
| [`analysis/primary_endpoint_disagreements_blinded.csv`](../analysis/primary_endpoint_disagreements_blinded.csv) | The five product-masked primary-label disagreements |
| [`ratings/completed_adjudication/`](../ratings/completed_adjudication/) | Reviewer A's five disagreement decisions |
| [`analysis/human_adjudication_validation.json`](../analysis/human_adjudication_validation.json) | Validation record for the adjudication file |

Two people performed the human-review work. Both original reviewers independently rated all 96 responses. Reviewer A later resolved the five disagreements. This was not independent third-party adjudication.

## 4. Frozen labels and analysis

| Record | Purpose |
|---|---|
| [`analysis/FINAL_HUMAN_ENDPOINTS_BLINDED_FREEZE.json`](../analysis/FINAL_HUMAN_ENDPOINTS_BLINDED_FREEZE.json) | Freeze over the final product-blinded endpoint dataset |
| [`analysis/UNBLINDING_STARTED.json`](../analysis/UNBLINDING_STARTED.json) | Record of the boundary between frozen labels and product unblinding |
| [`analysis/ADMIN_blinding_key.json`](../analysis/ADMIN_blinding_key.json) | Administrative mapping used for mechanical unblinding |
| [`analysis/final_endpoint_dataset_unblinded.csv`](../analysis/final_endpoint_dataset_unblinded.csv) | Final row-level endpoint dataset with product metadata |
| [`analysis/final_results.json`](../analysis/final_results.json) | Machine-readable results |
| [`analysis/final_tables/`](../analysis/final_tables/) | Final result tables |
| [`analysis/FINAL_RESULTS_FREEZE.json`](../analysis/FINAL_RESULTS_FREEZE.json) | Freeze receipt for the final analysis outputs |

## 5. Report, corrections, and limitations

| Record | Purpose |
|---|---|
| [`report/report.html`](../report/report.html) | Frozen self-contained technical report |
| [`report/artifact.json`](../report/artifact.json) | Machine-readable report artifact |
| [`report/FINAL_REPORT_RECEIPT.json`](../report/FINAL_REPORT_RECEIPT.json) | Hash and size receipt for the frozen report files |
| [`report/CORRECTION_NOTICE.md`](../report/CORRECTION_NOTICE.md) | Correction to the report's incorrect "third human" wording |
| [`docs/KNOWN_LIMITATIONS.md`](../docs/KNOWN_LIMITATIONS.md) | Study, collection, review, reproducibility, and reporting limits |
| [`REPRODUCIBILITY.md`](../REPRODUCIBILITY.md) | What can be verified, recalculated, or only repeated as a new study |
| [`RELEASE_AND_PRIVACY.md`](../RELEASE_AND_PRIVACY.md) | Private-material inventory and sharing rules |
| [`paper/PROFESSOR_MEETING_PREP.md`](../paper/PROFESSOR_MEETING_PREP.md) | Plain-language explanations, interpretation boundaries, and likely professor questions |

## 6. Integrity check

From the repository root, run:

```bash
make verify
```

This check is read-only. It verifies the archived counts, paths, schemas, hashes, reviewer-export locks, adjudication record, final freezes, and report receipt. A warning about the missing original schedule CSV is expected and documented above.
