# Code Review & Fix Plan - TODO

- [x] 1) `email_validator.py`
  - [x] Remove unreachable duplicated block after `check_domain_reputation` return
  - [x] Narrow broad `except:` blocks where practical
  - [x] Keep behavior backward-compatible

- [x] 2) `parallel_processor.py`
  - [x] Eliminate shared mutable validator contention across threads
  - [x] Ensure each task uses isolated `EmailValidator` instance (or safe alternative)

- [x] 3) `api_server.py`
  - [x] Add stricter input validation for `/api/domains` items (must be strings)
  - [x] Improve robustness for malformed inputs

- [x] 4) Validation
  - [x] Run test suite
  - [x] Report findings and deep-review summary

- [x] 5) `gui_app.py` Enterprise Redesign
  - [x] Replace current crowded layout with clean enterprise IA
  - [x] Introduce left navigation, top app bar, and workspace sections
  - [x] Improve forms/tables/readability and simplify visual hierarchy
  - [x] Preserve validator/batch/reporter integrations
  - [x] Launch and verify redesigned GUI

- [ ] 6) Universal Import + Same-Format Export
  - [ ] Add support for txt/csv/xls/xlsx import
  - [ ] Auto-detect/select sheet/row/email field mapping
  - [ ] Validate selected data with row-level statuses
  - [ ] Export enriched results in same source format
  - [ ] Update dependencies in requirements.txt
  - [ ] Run validation test of new workflow
