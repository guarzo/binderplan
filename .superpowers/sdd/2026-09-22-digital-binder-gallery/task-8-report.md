# Task 8 report

## Implementation summary

- Added a standard-library `HTMLParser` rendered-output validator and `--check-public PATH` CLI mode.
- Scoped rendered checks to `[data-binder]` roots so unrelated site pages and images remain valid.
- Accumulates errors for remote card URLs, duplicate leaf/HTML IDs, missing direct-link anchors, card leaves without exactly nine pockets, transition pockets, local-image alt text, loading discipline, binder controls, inspector dialog controls, and unresolved/over-budget initial images.
- Enforces a unique-file initial image budget of 1,572,864 bytes.
- Reads `DIGITAL_BINDER_PREVIOUS_REF`, ignoring absent and all-zero refs while preserving valid-ref transition validation and current-state validation.
- CI now installs Python validation dependencies, runs semantic checks before Hugo, validates a separate draft build containing the pilot, then builds and validates production before uploading the final `public/` artifact.
- Added parser, CLI, zero-binder, draft-binder, production, budget, scoping, and previous-ref tests. Added pytest to the pinned CI requirements.

## TDD evidence

The focused test run failed before implementation with 16 failures caused by the missing `validate_public_output` API and missing environment-ref wiring. After implementation, the focused suite passed with 18 tests; the completed suite contains 132 passing tests.

## Verification

- `python3 -m pip install -r requirements.txt`: passed.
- `python3 -m pytest scripts/test_check_registry.py scripts/test_digital_binder.py -q`: 132 passed.
- `python3 scripts/check-registry.py docs/card-registry.md`: passed; 175 rows.
- `python3 scripts/check-digital-binder.py --check`: passed.
- Draft Hugo build with `--buildDrafts --gc --minify --destination draft-public`: passed; 44 pages and 36 processed images.
- `python3 scripts/check-digital-binder.py --check-public draft-public`: passed.
- Production Hugo build with `--gc --minify --baseURL https://collection.dpao.la/`: passed; 42 pages and zero processed images.
- `python3 scripts/check-digital-binder.py --check-public public`: passed with the intentional zero-binder production output.
- Artifact separation assertion: draft pilot exists only in `draft-public`; production `public` has no pilot page.
- Full `python3 -m pytest -q`: 132 passed.
- `python3 -m py_compile scripts/digital_binder.py scripts/check-digital-binder.py scripts/test_digital_binder.py`: passed.
- Workflow YAML parsed successfully with PyYAML.
- `git diff --check`: passed.

## Scope and concerns

No live content, manifests, specifications, or gallery assets were changed. Production intentionally remains at zero published binders; draft validation is the structural pilot gate. The initial-file budget measures generated files referenced by `data-initial-binder-image`, counting each resolved URL only once.
