# Consumer AI and Truck Dispatch Decisions

This is a **private research archive for professor review**. It contains the current record of one experiment: the protocol, exact prompts, all captured responses, two independent human reviews, adjudication, analysis, reports, and known limitations.

## What the study asked

Would a consumer AI product tell a dispatcher that a truck could proceed to APM Terminals Elizabeth before trip-critical facts, approvals, current conditions, or regulatory conflicts had been resolved?

The experiment used:

```text
6 scenarios x 2 prompt versions x 4 products x 2 repetitions
= 96 captured responses
```

The products were ChatGPT, Claude, Copilot, and Gemini. Every run used a fresh conversation.

Two people independently reviewed all 96 responses. Their original ratings were preserved before comparison. They disagreed on five primary labels, which Reviewer A later resolved through a product-masked packet. There was no third reviewer.

## Main result

- **15 of 96** responses gave explicit or conditional present-trip clearance while a required issue remained unresolved.
- **81 of 96** did not.
- **13 of the 15** positive responses came from the local-access and mutable-route-restriction scenarios.
- The original reviewers agreed on **91 of 96** primary labels before adjudication. Cohen's kappa was **0.824**.

This is a result from a frozen challenge set. It is not a general AI failure rate, a product ranking, a legal judgment, or evidence that a real truck moved.

## Start here

1. [One-page professor brief](output/pdf/PROFESSOR_MEETING_ONE_PAGER.pdf)
2. [Correction to the frozen technical report](report/CORRECTION_NOTICE.md)
3. [Technical report](report/report.html)
4. [Known limitations](docs/KNOWN_LIMITATIONS.md)
5. [Provenance and integrity map](provenance/README.md)

## Where everything is

| Folder or file | What it contains |
|---|---|
| [`prompts/`](prompts/) | All 12 exact prompts |
| [`outputs/`](outputs/) | All 96 verbatim responses |
| [`capture_metadata/`](capture_metadata/) | One capture record for each response |
| [`ratings/`](ratings/) | Both original reviews and the adjudication records |
| [`analysis/`](analysis/) | Frozen labels, agreement analysis, final tables, and results |
| [`provenance/`](provenance/) | A simple map of the protocol, collection, review, freeze, and correction records |
| [`report/`](report/) | The frozen technical report and its correction notice |
| [`output/`](output/) | The generated one-page professor brief; raw AI responses are in `outputs/` |
| [`docs/`](docs/) | The six gold dispositions, workflow, and detailed limitations |
| [`tools/`](tools/) | Verification and analysis code |

## Verify the archive

Run this read-only check from the repository root:

```bash
make verify
```

The verifier checks the expected counts, JSON files, manifest references, archived hashes, original reviewer exports, adjudication record, final freezes, and report receipt.

## Important limits

The full list is in [docs/KNOWN_LIMITATIONS.md](docs/KNOWN_LIMITATIONS.md). The main points are:

- all six scenarios were unresolved "hold" cases;
- the original collection-schedule CSV named in `protocol_lock.json` is missing;
- four initial captures lack exact start timestamps;
- six cells used a second attempt, but the failed first attempts were not retained;
- some Reviewer A quote fields need clerical review before journal submission; and
- the frozen report incorrectly says a third human adjudicated the five disagreements. The [correction notice](report/CORRECTION_NOTICE.md) records the accurate two-person workflow.

## Private archive

Keep this repository private. It contains detailed capture metadata, human-review records, an administrative blinding key, free-text rationales, timestamps, and unblinded row-level results. Do not make it public or redistribute it without a separate privacy, consent, product-output, and licensing review.
