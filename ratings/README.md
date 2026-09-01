# Wave 4 human-review handoff

The two reviewers must work independently. Send **only** the contents of `reviewer_a` to Reviewer A and **only** the contents of `reviewer_b` to Reviewer B.

Do not send anything from the `analysis` directory. The admin blinding key reveals product identity and original run IDs.

After each reviewer exports their final JSON file:

1. place the files in `ratings/completed_originals/`;
2. hash-lock both originals before opening them side by side;
3. calculate raw agreement and Cohen's kappa from the original labels;
4. adjudicate only after agreement analysis, preserving both originals.
