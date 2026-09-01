# Known Limitations and Open Documentation Issues

This list is intentionally candid. It separates an auditable challenge-set result from claims the current design cannot support.

## Study-design limits

- All six scenarios were unresolved “hold” cases. The study does not measure balanced accuracy or false refusal.
- The 96 rows are captured responses in a fixed factorial matrix. They are not 96 independent people, trips, or population draws.
- Consumer products and their routing can change. The findings belong to the dated recorded surfaces and modes.
- Collection order was structured, not randomized. The neutral-versus-pressure comparison is descriptive.
- Scenario identity bundles wording, rules, missing facts, ambiguity type, route orientation, and authority structure. The S2/S4 concentration does not isolate a causal route effect.
- Product totals are small and secondary. No pairwise product tests were prespecified.
- The two repetitions provide only a limited stability check.
- The gold dispositions define a bounded operational reference decision. Independent transportation or regulatory expert review would strengthen them.

## Collection-provenance limits

- Four initial captures lack exact submission/start timestamps.
- Six retained cells used the allowed second attempt.
- Failed first-attempt artifacts and failure reasons were not preserved.
- Live collection was manual and has no retained automation script.
- Repeating the prompts now would be a temporal replication, not a byte-for-byte reproduction.

## Missing frozen item

`protocol_lock.json` records a hash for `collection_manifest_initial_schedule.csv`, but that exact file is absent from the current archive.

The hash remains part of the prospective record. The missing file should be restored if a matching original can be found. It must not be reconstructed and presented as the original after outcomes are known.

## Human-review documentation

- Two original reviewers independently rated all 96 responses before comparison.
- Five primary-label disagreements received post-agreement adjudication decisions from Reviewer A.
- The archive indicates only two unique human contributors to the review workflow. The original ratings were independent, but the adjudication was not independent third-party review.
- Reviewer qualifications, codebook familiarization, relationships, and conflicts still require documentation.
- Reviewer B’s item-level timestamps cannot establish item-by-item review timing because the export uses a common timestamp.
- A conservative mechanical audit flagged ten Reviewer A decisive-quote fields for clerical traceability review.
- At least one flagged supporting quote/rationale appears to refer to a different scenario. Both original reviewers assigned that item the same primary label, so it did not create a demonstrated headline-count error. It still requires correction or disclosure before journal submission.

## Reproducibility limits

- Several lock and freeze receipts have no retained generator script.
- Generated timestamps prevent byte-identical reruns even when substantive results match.
- Finalization and final-analysis scripts write into archived paths and make outputs read-only. They should be run only in a clean reproduction copy.
- `tools/build_collection_manifest.sh` is initialization-only and would overwrite the completed manifest if run in the archive.
- The HTML report’s temporary JSX/CSS source project is missing.
- The professor brief is retained only as the generated PDF; its source document, build scripts, fonts, and exact package versions are not included.

## Reporting limits

- The locked question uses “frontier tool-using agents,” but the actual sample was four dated consumer AI product surfaces. The frozen wording belongs in the audit trail; empirical claims should use the narrower language.
- The 15/96 result is not a general prevalence estimate.
- Wilson intervals stored in machine-readable tables describe captured-response proportions. They should not be presented as population-prevalence uncertainty.
- No real truck was dispatched. No real-world reliance, violation, denial, delay, injury, or harm was observed.
- Several frozen secondary constructs were not fully scored. They must not be reconstructed retrospectively after seeing outcomes.
