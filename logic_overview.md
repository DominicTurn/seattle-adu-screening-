# Seattle ADU Permit Readiness – Phase 1 Logic Overview

This project is a **lightweight, informational screening tool**.

## Purpose
Provide homeowners with a quick, non-legal assessment of whether an ADU project is:
- Likely
- Possible
- Unlikely

based on self-reported inputs and a small set of representative Seattle SDCI rules.

## Important Constraints
- Seattle only (Phase 1)
- No parcel lookup or GIS
- No database or admin UI
- No compliance guarantees
- Unknown inputs should bias toward "Possible", not hard failure

## Scoring Model
- Start score: 100
- Blocker rules → "Unlikely"
- Warnings reduce score
- Info rules do not affect score

## Output
Results must include:
- Final label
- List of triggered rules (plain English)
- Optional “what to check next” guidance
- Clear disclaimer that this is not legal advice

This is an MVP intended to validate demand, not replace SDCI review.
