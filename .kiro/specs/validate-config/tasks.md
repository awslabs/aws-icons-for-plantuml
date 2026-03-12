# Tasks

- [x] Task 1: Add `--validate-config` CLI flag to argparse
<!-- Requirement: 1 (CLI Flag Registration) -->
<!-- Acceptance Criteria: 1.1, 1.2 -->

Add the `--validate-config` argument to the existing `argparse.ArgumentParser` in `scripts/icon-builder.py`, alongside the other flags. Wire it into `main()` so it dispatches early (like `--create-config-template`) and exits before any build steps.

### Files to modify

- `scripts/icon-builder.py`: Add `parser.add_argument("--validate-config", ...)` and add dispatch in `main()` that calls a `validate_config()` function and exits.

- [x] Task 2: Implement YAML structure validation
<!-- Requirement: 2 (YAML Structure Validation) -->
<!-- Acceptance Criteria: 2.1, 2.2, 2.3, 2.4 -->

Create a `validate_config()` function in `scripts/icon-builder.py` that loads `config.yml` and checks for:

- Valid YAML parsing (catch `yaml.YAMLError`)
- Presence of `Defaults` top-level key
- Presence of `Categories` top-level key
- Presence of `Defaults.Colors` key

Collect issues into a list of structured error dicts with a `check_type` field (e.g., `"structure"`).

### Files to modify

- `scripts/icon-builder.py`: Add `validate_config()` function with structure checks.

- [x] Task 3: Implement required field validation for icon entries
<!-- Requirement: 3 (Required Field Validation for Icon Entries) -->
<!-- Acceptance Criteria: 3.1, 3.2, 3.3, 3.4 -->

Extend `validate_config()` to iterate all categories and their `Icons` lists, checking each entry for required fields: `Source`, `SourceDir`, `Target`, `Target2`. Report missing fields with category name and entry index.

### Files to modify

- `scripts/icon-builder.py`: Extend `validate_config()` with required field checks.

- [x] Task 4: Implement duplicate Target and Target2 detection
<!-- Requirement: 4, 5 (Duplicate Target/Target2 Name Detection) -->
<!-- Acceptance Criteria: 4.1, 4.2, 4.3, 5.1, 5.2, 5.3 -->

Extend `validate_config()` to collect all `Target` values and all `Target2` values across every category, detect duplicates, and report each with the category name and value.

### Files to modify

- `scripts/icon-builder.py`: Extend `validate_config()` with duplicate detection for both `Target` and `Target2`.

- [x] Task 5: Implement color validation for categories and icons
<!-- Requirement: 6, 7 (Category Color Validation, Icon-Level Color Validation) -->
<!-- Acceptance Criteria: 6.1, 6.2, 6.3, 7.1, 7.2, 7.3 -->

Extend `validate_config()` to:

- Check each category's `Color` value against `Defaults.Colors` palette names (case-sensitive). Categories without a `Color` are accepted.
- Check each icon entry's `Color` override: bare names must match the palette; values starting with `#` or `$` are accepted; absent `Color` is accepted.

### Files to modify

- `scripts/icon-builder.py`: Extend `validate_config()` with color validation logic.

- [x] Task 6: Implement validation report formatting and exit codes
<!-- Requirement: 1, 8 (CLI Flag Registration, Validation Report Format) -->
<!-- Acceptance Criteria: 1.3, 1.4, 8.1, 8.2, 8.3, 8.4 -->

Add report output logic to `validate_config()`:

- Group issues by check type (structure, missing fields, duplicates, invalid colors)
- Prefix each issue with the category name
- Print a summary line with total issue count, or a single success message
- Exit with code 0 on success, non-zero on failure

### Files to modify

- `scripts/icon-builder.py`: Add report formatting and `sys.exit()` calls in `validate_config()`.

- [x] Task 7: Add tests for config validation
<!-- Requirement: 1, 2, 3, 4, 5, 6, 7, 8 -->

Create `scripts/test_validate_config.py` with pytest tests covering:

- Valid config passes with no issues
- Missing top-level keys detected
- Missing required icon fields detected
- Duplicate `Target` and `Target2` detected
- Invalid category and icon-level colors detected
- Report format and exit code behavior

### Files to create

- `scripts/test_validate_config.py`
