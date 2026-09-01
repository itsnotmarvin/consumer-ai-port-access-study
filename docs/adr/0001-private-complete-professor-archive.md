# 0001 — Private Complete Professor Archive

**Status:** Accepted  
**Date:** 31 August 2026

## Context

The immediate goal is to let a professor inspect the current experiment in full.

The archive contains all prompts, verbatim responses, capture metadata, human-review records, adjudication materials, analysis datasets, reports, and working-paper files. Some of those materials require privacy, consent, or redistribution review before public release.

## Decision

Create one private GitHub repository containing the complete current research archive.

Include the full evidentiary chain. Exclude only operating-system files, caches, virtual environments, credentials, and other non-research machine debris.

Keep the repository focused on the experiment. Do not add course, institution, or personal-profile framing to the project narrative.

Do not reorganize the frozen study tree merely for aesthetics. Existing relative paths and scripts depend on the current layout.

## Consequences

- The professor can inspect every prompt, response, rating, analysis artifact, and report from one place.
- Every invited repository collaborator can read all tracked material.
- The repository must remain private.
- A future public release requires a separate sanitized export and its own consent, redistribution, metadata, and license review.
- Documentation must clearly distinguish archive verification, numerical recalculation, and a new temporal replication.
