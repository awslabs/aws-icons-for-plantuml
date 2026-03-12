# Requirements Document

## Introduction

This feature adds a `--validate-config` CLI flag to `icon-builder.py` that performs a dedicated validation pass on `config.yml` without running the full build. It checks for structural issues (missing required fields), uniqueness violations (duplicate `Target` and `Target2` names), and semantic issues (invalid color references). Currently, duplicate detection only occurs during `--create-config-template` and merely adds a YAML comment rather than failing. This feature provides early, clear error reporting so maintainers can catch config problems before attempting a build.

## Glossary

- **Config_Validator**: The validation module invoked by the `--validate-config` CLI flag that loads and checks `config.yml`
- **Config_File**: The `scripts/config.yml` YAML file containing `Defaults` and `Categories` sections that map source icons to build targets
- **Icon_Entry**: A single icon mapping within a category's `Icons` list, containing fields such as `Source`, `SourceDir`, `Target`, and `Target2`
- **Color_Palette**: The set of named colors defined in `Defaults.Colors` within the Config_File (e.g., Galaxy, Cosmos, Smile)
- **Target**: The PascalCase identifier used as the PlantUML macro name for an icon (must be globally unique)
- **Target2**: The kebab-case identifier used as the Mermaid icon name for an icon (must be globally unique)
- **Category**: A top-level grouping under `Categories` in the Config_File, each with a `Color` and an `Icons` list
- **Validation_Report**: The structured output produced by the Config_Validator listing all detected issues

## Requirements

### Requirement 1: CLI Flag Registration

**User Story:** As a maintainer, I want a `--validate-config` flag on `icon-builder.py`, so that I can validate the config file without running the full build.

#### Acceptance Criteria

1. WHEN the `--validate-config` flag is provided, THE Config_Validator SHALL load and validate the Config_File and exit without performing any build steps
2. THE Config_Validator SHALL be usable independently of `--check-env`, `--create-config-template`, `--symbols-only`, and `--create-color-json` flags
3. WHEN the `--validate-config` flag is provided and validation passes with zero issues, THE Config_Validator SHALL print a success message and exit with code 0
4. WHEN the `--validate-config` flag is provided and validation detects one or more issues, THE Config_Validator SHALL print all issues and exit with a non-zero exit code

### Requirement 2: YAML Structure Validation

**User Story:** As a maintainer, I want the validator to check that `config.yml` is well-formed and has the expected top-level structure, so that I catch structural problems early.

#### Acceptance Criteria

1. WHEN the Config_File cannot be parsed as valid YAML, THE Config_Validator SHALL report a parse error with the YAML error details
2. WHEN the Config_File is missing the `Defaults` top-level key, THE Config_Validator SHALL report a missing `Defaults` section error
3. WHEN the Config_File is missing the `Categories` top-level key, THE Config_Validator SHALL report a missing `Categories` section error
4. WHEN the `Defaults` section is missing the `Colors` key, THE Config_Validator SHALL report a missing `Defaults.Colors` error

### Requirement 3: Required Field Validation for Icon Entries

**User Story:** As a maintainer, I want the validator to check that every icon entry has the required fields, so that I catch incomplete entries before building.

#### Acceptance Criteria

1. WHEN an Icon_Entry is missing the `Source` field, THE Config_Validator SHALL report the missing field with the Category name and entry index
2. WHEN an Icon_Entry is missing the `SourceDir` field, THE Config_Validator SHALL report the missing field with the Category name and entry index
3. WHEN an Icon_Entry is missing the `Target` field, THE Config_Validator SHALL report the missing field with the Category name and entry index
4. WHEN an Icon_Entry is missing the `Target2` field, THE Config_Validator SHALL report the missing field with the Category name and entry index

### Requirement 4: Duplicate Target Name Detection

**User Story:** As a maintainer, I want the validator to detect duplicate `Target` names across all categories, so that I avoid PlantUML macro name collisions.

#### Acceptance Criteria

1. THE Config_Validator SHALL check `Target` values for uniqueness across all Icon_Entry items in all Categories
2. WHEN two or more Icon_Entry items share the same `Target` value, THE Config_Validator SHALL report each duplicate with the Category name and `Target` value
3. WHEN all `Target` values are unique, THE Config_Validator SHALL report no duplicate Target issues

### Requirement 5: Duplicate Target2 Name Detection

**User Story:** As a maintainer, I want the validator to detect duplicate `Target2` names across all categories, so that I avoid Mermaid icon name collisions.

#### Acceptance Criteria

1. THE Config_Validator SHALL check `Target2` values for uniqueness across all Icon_Entry items in all Categories
2. WHEN two or more Icon_Entry items share the same `Target2` value, THE Config_Validator SHALL report each duplicate with the Category name and `Target2` value
3. WHEN all `Target2` values are unique, THE Config_Validator SHALL report no duplicate Target2 issues

### Requirement 6: Category Color Validation

**User Story:** As a maintainer, I want the validator to check that each category's `Color` references a valid palette name, so that I catch typos in color assignments.

#### Acceptance Criteria

1. WHEN a Category has a `Color` value that does not match any name in the Color_Palette, THE Config_Validator SHALL report the invalid color with the Category name and the invalid value
2. WHEN a Category does not specify a `Color` value, THE Config_Validator SHALL accept the entry without error, as the default color from `Defaults.Category.Color` applies
3. THE Config_Validator SHALL treat Color_Palette names as case-sensitive when checking validity

### Requirement 7: Icon-Level Color Validation

**User Story:** As a maintainer, I want the validator to check icon-level `Color` overrides, so that I catch invalid color references on individual icons.

#### Acceptance Criteria

1. WHEN an Icon_Entry has a `Color` field whose value is a bare name that does not match any Color_Palette name and does not start with `#` or `$`, THE Config_Validator SHALL report the invalid color with the Category name and Target value
2. WHEN an Icon_Entry has a `Color` field whose value starts with `#` (hex color) or `$` (PlantUML variable), THE Config_Validator SHALL accept the value without error
3. WHEN an Icon_Entry does not have a `Color` field, THE Config_Validator SHALL accept the entry without error

### Requirement 8: Validation Report Format

**User Story:** As a maintainer, I want validation output to be clear and actionable, so that I can quickly locate and fix problems.

#### Acceptance Criteria

1. THE Config_Validator SHALL prefix each reported issue with the Category name where the issue was found
2. THE Config_Validator SHALL group reported issues by validation check type (structure, missing fields, duplicates, invalid colors)
3. WHEN validation completes with issues, THE Config_Validator SHALL print a summary line stating the total number of issues found
4. WHEN validation completes with no issues, THE Config_Validator SHALL print a single success message indicating the Config_File is valid
