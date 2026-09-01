# Study Workflow

This page explains what happened, in order. It distinguishes preserved evidence from steps that still require better automation or documentation.

## 1. Bound the evidence

The study pinned the public `last-mile-drayage-pilot` repository to commit `7fe49ebb0fc8376f0f183e1f614c06d284c13343`.

[`../evidence_lock.json`](../evidence_lock.json) records the eight retained file hashes and explains the evidence boundary. Mutable facts still required a live recheck. Unresolved conflicts remained unresolved.

## 2. Define the experiment

The project created:

- six unresolved challenge scenarios;
- one neutral and one dispatch-pressure prompt per scenario;
- a four-product consumer-surface sample;
- two repeated outputs per exact condition;
- one action-level primary endpoint; and
- a frozen human-review codebook.

The design is stored in [`../design.json`](../design.json). The six reference decisions are stored in [`../gold_dispositions.json`](../gold_dispositions.json).

## 3. Freeze the protocol

Before primary collection, the study hash-locked:

- the design;
- reference dispositions;
- evidence receipt;
- human codebook;
- planned collection schedule hash; and
- all 12 exact prompt texts.

[`../protocol_lock.json`](../protocol_lock.json) records the lock time and hashes. This was an internal prospective lock, not a public preregistration.

## 4. Capture the product responses

The complete matrix was:

```text
6 scenarios × 2 variants × 4 products × 2 repetitions = 96 responses
```

Each run used a fresh conversation. The exact prompt was submitted to the recorded consumer surface. The complete response was copied through the product-native response-copy control.

The archive contains:

- [`../collection_manifest.csv`](../collection_manifest.csv);
- all exact prompts under [`../prompts/`](../prompts/);
- all verbatim responses under [`../outputs/`](../outputs/); and
- one provenance record per response under [`../capture_metadata/`](../capture_metadata/).

Ninety runs succeeded on the first allowed attempt. Six used the protocol’s second attempt. All 96 planned cells were retained as usable.

## 5. Build product-masked review packets

[`../tools/build_blinded_review_packets.mjs`](../tools/build_blinded_review_packets.mjs) validated the collection and built two differently ordered browser packets.

The packets used anonymous response IDs. They omitted product, run, repetition, attempt, and timing metadata where feasible. Complete blinding could not be guaranteed because a response could identify its own product.

The administrative mapping was kept separately in `analysis/ADMIN_blinding_key.json`.

## 6. Conduct independent human review

Two original reviewers independently classified all 96 responses under the frozen codebook. They recorded:

- movement disposition;
- primary endpoint label;
- decisive quote;
- material unresolved input;
- written rationale; and
- ambiguity flag.

Their original exports were preserved and hash-locked before labels were compared.

## 7. Measure agreement before adjudication

[`../tools/analyze_human_agreement.py`](../tools/analyze_human_agreement.py) calculated agreement from the preserved original files.

The original reviewers agreed on 91 of 96 primary labels. Cohen’s kappa was 0.824. Five primary-label disagreements remained.

## 8. Record disagreement decisions

The five disagreements were placed into a product-masked adjudication packet. Reviewer A then recorded the five final disagreement decisions. The completed decisions and their hash receipt are preserved under `ratings/completed_adjudication/`.

The repository preserves two unique human contributors to the review workflow. The original ratings were independent, but the later adjudication was performed by one of those original reviewers. It was not independent third-party adjudication.

## 9. Freeze final labels while still product-blinded

[`../tools/finalize_human_endpoints_blinded.py`](../tools/finalize_human_endpoints_blinded.py) combined:

- the common label for the 91 original agreements; and
- the recorded adjudication decision for the five disagreements.

The complete 96-row product-blinded dataset was frozen before the administrative mapping was opened.

Final blinded counts were 15 `yes`, 81 `no`, and zero `unclear`.

## 10. Join product metadata and calculate results

[`../tools/analyze_final_endpoints.py`](../tools/analyze_final_endpoints.py) joined the frozen labels to the administrative metadata without rescoring any response text.

It generated:

- the row-level final dataset;
- scenario, product, variant, and repetition tables;
- matched-repetition summaries;
- route-oriented descriptive tables;
- [`../analysis/final_results.json`](../analysis/final_results.json); and
- [`../analysis/FINAL_RESULTS_FREEZE.json`](../analysis/FINAL_RESULTS_FREEZE.json).

## 11. Build the report and professor brief

The project produced:

- a self-contained [technical HTML report](../report/report.html);
- a machine-readable [report artifact](../report/artifact.json);
- a [one-page professor brief](../output/pdf/PROFESSOR_MEETING_ONE_PAGER.pdf).

The report can be opened and integrity-checked. Its original temporary JSX/CSS build project is not present, so the HTML cannot currently be rebuilt end to end from this archive. The professor brief is retained as a generated PDF; its source document and build scripts are not included.
