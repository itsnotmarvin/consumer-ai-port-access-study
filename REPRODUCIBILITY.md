# Reproducibility Guide

## Three different meanings of “reproduce”

This archive supports three different activities. They should not be conflated.

### 1. Verify the archived experiment

This is the safest and strongest current operation.

```bash
make verify
```

The verifier checks expected file counts, JSON validity, manifest references, prompt and response hashes, preserved human-export locks, final freeze files, and report receipts. It does not rewrite any study artifact.

### 2. Recalculate the numerical results

The preserved inputs and scripts support recalculating most numerical outputs. Do this only in a clean copy or dedicated build directory.

Do not run finalization or final-analysis scripts directly over the archived outputs. Several outputs are read-only, and the scripts write new timestamps and then set files to read-only again.

The historical logical order was:

```text
build reviewer packets
        ↓
complete and lock two independent reviewer exports
        ↓
calculate agreement
        ↓
build and complete disagreement-only adjudication packet
        ↓
freeze final labels while product-blinded
        ↓
record the unblinding boundary
        ↓
join administrative metadata and calculate final tables
        ↓
build report artifact and professor brief
```

The retained commands are:

```bash
node tools/build_blinded_review_packets.mjs
python3 tools/analyze_human_agreement.py
node tools/build_blinded_adjudication_packet.mjs
python3 tools/finalize_human_endpoints_blinded.py
python3 tools/analyze_final_endpoints.py
python3 tools/build_final_report_artifact.py
```

These commands are documentation of the historical workflow. They are not a safe in-place “run all” script.

### 3. Repeat the live consumer-product experiment

Submitting the same prompts again would be a new temporal replication. Consumer products, underlying routing, policies, and web state change. A new collection must receive a new date, run IDs, capture metadata, protocol lock, and results. It must never overwrite this archive.

## Runtime requirements

Core analysis uses:

- Python 3.11 or later;
- Python’s standard library;
- modern Node.js with ECMAScript modules;
- zsh, `shasum`, `awk`, and `mktemp`; and
- a browser with JavaScript, local storage, and file downloads for the review packets.

## Initialization warning

Never run this command in the completed archive:

```bash
zsh tools/build_collection_manifest.sh
```

That script creates an initial all-`planned` manifest and writes directly to `collection_manifest.csv`. Running it here would replace the completed 96-row collection record.

## Report boundary

[`report/report.html`](report/report.html) is self-contained and can be opened directly or served locally:

```bash
make serve-report
```

The HTML and report artifacts can be hash-verified. The temporary Data App project used to compile the HTML is not retained, so an end-to-end rebuild is not currently possible.

The generated professor brief is retained as a PDF. Its source document, build scripts, fonts, and exact package versions are not included.

## Known non-reproducible or manually recorded steps

- creation of some lock and freeze receipts;
- manual live-response collection;
- preservation of failed first attempts;
- exact Reviewer B export/conversion procedure;
- the original Data App report source project;
- the professor brief's source and document-build environment; and
- exact historical document package versions.

These gaps should be disclosed. They should not be filled by reconstructing historical evidence after the fact.
