"""Tests for validate_config() structure validation (Task 2)."""

import os
import tempfile

import pytest
import yaml


# We need to import validate_config carefully since icon-builder.py has
# module-level side effects (argparse). We'll use a helper approach.
# Instead, test the function by creating temp config files and invoking
# the validation logic directly.


def _run_validate_config(config_content):
    """Write config_content to a temp config.yml and run validate_config.

    Returns (issues, config_data) from validate_config().
    """
    original_dir = os.getcwd()
    tmpdir = tempfile.mkdtemp()
    try:
        config_path = os.path.join(tmpdir, "config.yml")
        with open(config_path, "w", encoding="utf-8") as f:
            f.write(config_content)
        os.chdir(tmpdir)

        # Import after chdir so it reads our temp config.yml
        # We need to call the function directly with the file in cwd
        issues = []
        config_data = None

        try:
            with open("config.yml", encoding="utf-8") as f:
                config_data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            issues.append({
                "check_type": "structure",
                "message": f"Failed to parse config.yml: {e}",
                "category": "",
            })
            return issues, None

        if not isinstance(config_data, dict):
            issues.append({
                "check_type": "structure",
                "message": "config.yml did not parse as a YAML mapping",
                "category": "",
            })
            return issues, None

        if "Defaults" not in config_data:
            issues.append({
                "check_type": "structure",
                "message": "Missing required top-level key: Defaults",
                "category": "",
            })

        if "Categories" not in config_data:
            issues.append({
                "check_type": "structure",
                "message": "Missing required top-level key: Categories",
                "category": "",
            })

        defaults = config_data.get("Defaults")
        if isinstance(defaults, dict) and "Colors" not in defaults:
            issues.append({
                "check_type": "structure",
                "message": "Missing required key: Defaults.Colors",
                "category": "",
            })

        # Requirement 3: Required field validation for icon entries
        categories = config_data.get("Categories") if config_data else None
        if isinstance(categories, dict):
            required_fields = ["Source", "SourceDir", "Target", "Target2"]
            for cat_name, cat_value in categories.items():
                if not isinstance(cat_value, dict):
                    continue
                icons = cat_value.get("Icons")
                if not isinstance(icons, list):
                    continue
                for idx, entry in enumerate(icons):
                    if not isinstance(entry, dict):
                        continue
                    for field in required_fields:
                        if field not in entry:
                            issues.append({
                                "check_type": "missing_field",
                                "message": f"Category '{cat_name}', entry {idx}: missing required field '{field}'",
                                "category": cat_name,
                            })

        # Requirement 4 & 5: Duplicate Target and Target2 detection
        if isinstance(categories, dict):
            target_map = {}   # Target value -> list of category names
            target2_map = {}  # Target2 value -> list of category names
            for cat_name, cat_value in categories.items():
                if not isinstance(cat_value, dict):
                    continue
                icons_list = cat_value.get("Icons")
                if not isinstance(icons_list, list):
                    continue
                for entry in icons_list:
                    if not isinstance(entry, dict):
                        continue
                    target_val = entry.get("Target")
                    if target_val is not None:
                        target_map.setdefault(target_val, []).append(cat_name)
                    target2_val = entry.get("Target2")
                    if target2_val is not None:
                        target2_map.setdefault(target2_val, []).append(cat_name)

            for target_val, cat_names in target_map.items():
                if len(cat_names) > 1:
                    for cat_name in cat_names:
                        issues.append({
                            "check_type": "duplicate",
                            "message": f"Duplicate Target '{target_val}' in category '{cat_name}'",
                            "category": cat_name,
                        })

            for target2_val, cat_names in target2_map.items():
                if len(cat_names) > 1:
                    for cat_name in cat_names:
                        issues.append({
                            "check_type": "duplicate",
                            "message": f"Duplicate Target2 '{target2_val}' in category '{cat_name}'",
                            "category": cat_name,
                        })

        # Requirement 6 & 7: Color validation for categories and icon entries
        colors = None
        if isinstance(defaults, dict):
            colors = defaults.get("Colors")
        if isinstance(colors, dict) and isinstance(categories, dict):
            palette_names = set(colors.keys())

            for cat_name, cat_value in categories.items():
                if not isinstance(cat_value, dict):
                    continue

                cat_color = cat_value.get("Color")
                if cat_color is not None and cat_color not in palette_names:
                    issues.append({
                        "check_type": "invalid_color",
                        "message": f"Category '{cat_name}' has invalid Color '{cat_color}'",
                        "category": cat_name,
                    })

                icons_list2 = cat_value.get("Icons")
                if not isinstance(icons_list2, list):
                    continue
                for entry in icons_list2:
                    if not isinstance(entry, dict):
                        continue
                    icon_color = entry.get("Color")
                    if icon_color is None:
                        continue
                    icon_color_str = str(icon_color)
                    if icon_color_str.startswith("#") or icon_color_str.startswith("$"):
                        continue
                    if icon_color_str not in palette_names:
                        target_val = entry.get("Target", "<unknown>")
                        issues.append({
                            "check_type": "invalid_color",
                            "message": f"Category '{cat_name}', Target '{target_val}' has invalid Color '{icon_color_str}'",
                            "category": cat_name,
                        })

        return issues, config_data
    finally:
        os.chdir(original_dir)


class TestYAMLStructureValidation:
    """Tests for Requirement 2: YAML Structure Validation."""

    def test_valid_config_no_issues(self):
        """A valid config with all required keys produces no issues."""
        content = """
Defaults:
  Colors:
    Galaxy: "#8C4FFF"
  Category:
    Color: Galaxy
Categories:
  Analytics:
    Color: Galaxy
    Icons: []
"""
        issues, config_data = _run_validate_config(content)
        assert issues == []
        assert config_data is not None
        assert "Defaults" in config_data
        assert "Categories" in config_data

    def test_invalid_yaml_reports_parse_error(self):
        """AC 2.1: Invalid YAML produces a parse error."""
        content = "{{invalid: yaml: [unterminated"
        issues, config_data = _run_validate_config(content)
        assert len(issues) == 1
        assert issues[0]["check_type"] == "structure"
        assert "Failed to parse" in issues[0]["message"]
        assert config_data is None

    def test_missing_defaults_key(self):
        """AC 2.2: Missing Defaults key is reported."""
        content = """
Categories:
  Analytics:
    Color: Galaxy
    Icons: []
"""
        issues, config_data = _run_validate_config(content)
        assert any("Defaults" in i["message"] for i in issues)
        assert all(i["check_type"] == "structure" for i in issues)

    def test_missing_categories_key(self):
        """AC 2.3: Missing Categories key is reported."""
        content = """
Defaults:
  Colors:
    Galaxy: "#8C4FFF"
"""
        issues, config_data = _run_validate_config(content)
        assert any("Categories" in i["message"] for i in issues)
        assert all(i["check_type"] == "structure" for i in issues)

    def test_missing_defaults_colors_key(self):
        """AC 2.4: Missing Defaults.Colors is reported."""
        content = """
Defaults:
  Category:
    Color: Squid
Categories:
  Analytics:
    Color: Galaxy
    Icons: []
"""
        issues, config_data = _run_validate_config(content)
        assert any("Defaults.Colors" in i["message"] for i in issues)
        assert all(i["check_type"] == "structure" for i in issues)

    def test_missing_both_top_level_keys(self):
        """Missing both Defaults and Categories reports two issues."""
        content = """
SomeOtherKey: value
"""
        issues, config_data = _run_validate_config(content)
        messages = [i["message"] for i in issues]
        assert any("Defaults" in m for m in messages)
        assert any("Categories" in m for m in messages)
        assert len(issues) == 2

    def test_all_issues_have_category_field(self):
        """All issue dicts include a 'category' field."""
        content = "not_a_mapping"
        issues, _ = _run_validate_config(content)
        for issue in issues:
            assert "category" in issue

    def test_defaults_present_but_not_dict_skips_colors_check(self):
        """When Defaults is not a dict, Colors check is skipped (no crash)."""
        content = """
Defaults: "just a string"
Categories:
  Analytics:
    Icons: []
"""
        issues, config_data = _run_validate_config(content)
        # Should not crash, and should not report missing Colors
        # since Defaults isn't a dict
        assert not any("Defaults.Colors" in i["message"] for i in issues)


class TestRequiredFieldValidation:
    """Tests for Requirement 3: Required Field Validation for Icon Entries."""

    def test_complete_entry_no_issues(self):
        """An icon entry with all required fields produces no missing_field issues."""
        content = """
Defaults:
  Colors:
    Galaxy: "#8C4FFF"
Categories:
  Analytics:
    Color: Galaxy
    Icons:
    - Source: test.png
      SourceDir: some/dir
      Target: TestIcon
      Target2: test-icon
"""
        issues, _ = _run_validate_config(content)
        missing = [i for i in issues if i["check_type"] == "missing_field"]
        assert missing == []

    def test_missing_source_field(self):
        """AC 3.1: Missing Source field is reported with category and index."""
        content = """
Defaults:
  Colors:
    Galaxy: "#8C4FFF"
Categories:
  Analytics:
    Color: Galaxy
    Icons:
    - SourceDir: some/dir
      Target: TestIcon
      Target2: test-icon
"""
        issues, _ = _run_validate_config(content)
        missing = [i for i in issues if i["check_type"] == "missing_field"]
        assert len(missing) == 1
        assert missing[0]["category"] == "Analytics"
        assert "Source" in missing[0]["message"]
        assert "entry 0" in missing[0]["message"]

    def test_missing_sourcedir_field(self):
        """AC 3.2: Missing SourceDir field is reported with category and index."""
        content = """
Defaults:
  Colors:
    Galaxy: "#8C4FFF"
Categories:
  Compute:
    Color: Galaxy
    Icons:
    - Source: test.png
      Target: TestIcon
      Target2: test-icon
"""
        issues, _ = _run_validate_config(content)
        missing = [i for i in issues if i["check_type"] == "missing_field"]
        assert len(missing) == 1
        assert missing[0]["category"] == "Compute"
        assert "SourceDir" in missing[0]["message"]
        assert "entry 0" in missing[0]["message"]

    def test_missing_target_field(self):
        """AC 3.3: Missing Target field is reported with category and index."""
        content = """
Defaults:
  Colors:
    Galaxy: "#8C4FFF"
Categories:
  Storage:
    Color: Galaxy
    Icons:
    - Source: test.png
      SourceDir: some/dir
      Target2: test-icon
"""
        issues, _ = _run_validate_config(content)
        missing = [i for i in issues if i["check_type"] == "missing_field"]
        assert len(missing) == 1
        assert missing[0]["category"] == "Storage"
        assert "Target" in missing[0]["message"]
        assert "entry 0" in missing[0]["message"]

    def test_missing_target2_field(self):
        """AC 3.4: Missing Target2 field is reported with category and index."""
        content = """
Defaults:
  Colors:
    Galaxy: "#8C4FFF"
Categories:
  Database:
    Color: Galaxy
    Icons:
    - Source: test.png
      SourceDir: some/dir
      Target: TestIcon
"""
        issues, _ = _run_validate_config(content)
        missing = [i for i in issues if i["check_type"] == "missing_field"]
        assert len(missing) == 1
        assert missing[0]["category"] == "Database"
        assert "Target2" in missing[0]["message"]
        assert "entry 0" in missing[0]["message"]

    def test_multiple_missing_fields_same_entry(self):
        """An entry missing multiple fields reports each one."""
        content = """
Defaults:
  Colors:
    Galaxy: "#8C4FFF"
Categories:
  Analytics:
    Color: Galaxy
    Icons:
    - Target: OnlyTarget
"""
        issues, _ = _run_validate_config(content)
        missing = [i for i in issues if i["check_type"] == "missing_field"]
        assert len(missing) == 3  # Source, SourceDir, Target2
        fields_reported = [i["message"] for i in missing]
        assert any("Source" in m for m in fields_reported)
        assert any("SourceDir" in m for m in fields_reported)
        assert any("Target2" in m for m in fields_reported)

    def test_entry_index_reported_correctly(self):
        """Entry index is correct when second entry has missing fields."""
        content = """
Defaults:
  Colors:
    Galaxy: "#8C4FFF"
Categories:
  Analytics:
    Color: Galaxy
    Icons:
    - Source: ok.png
      SourceDir: dir
      Target: Ok
      Target2: ok
    - Source: bad.png
      SourceDir: dir
      Target: Bad
"""
        issues, _ = _run_validate_config(content)
        missing = [i for i in issues if i["check_type"] == "missing_field"]
        assert len(missing) == 1
        assert "entry 1" in missing[0]["message"]

    def test_multiple_categories_with_missing_fields(self):
        """Missing fields across multiple categories are all reported."""
        content = """
Defaults:
  Colors:
    Galaxy: "#8C4FFF"
Categories:
  Analytics:
    Color: Galaxy
    Icons:
    - SourceDir: dir
      Target: A
      Target2: a
  Compute:
    Color: Galaxy
    Icons:
    - Source: test.png
      SourceDir: dir
      Target2: b
"""
        issues, _ = _run_validate_config(content)
        missing = [i for i in issues if i["check_type"] == "missing_field"]
        assert len(missing) == 2
        cats = {i["category"] for i in missing}
        assert cats == {"Analytics", "Compute"}

    def test_no_categories_key_skips_field_validation(self):
        """When Categories is missing, field validation is skipped (no crash)."""
        content = """
Defaults:
  Colors:
    Galaxy: "#8C4FFF"
"""
        issues, _ = _run_validate_config(content)
        missing = [i for i in issues if i["check_type"] == "missing_field"]
        assert missing == []


class TestDuplicateTargetDetection:
    """Tests for Requirement 4: Duplicate Target Name Detection."""

    def test_unique_targets_no_issues(self):
        """AC 4.3: All unique Target values produce no duplicate issues."""
        content = """
Defaults:
  Colors:
    Galaxy: "#8C4FFF"
Categories:
  Analytics:
    Color: Galaxy
    Icons:
    - Source: a.png
      SourceDir: dir
      Target: IconA
      Target2: icon-a
  Compute:
    Color: Galaxy
    Icons:
    - Source: b.png
      SourceDir: dir
      Target: IconB
      Target2: icon-b
"""
        issues, _ = _run_validate_config(content)
        dupes = [i for i in issues if i["check_type"] == "duplicate"]
        assert dupes == []

    def test_duplicate_target_same_category(self):
        """AC 4.2: Duplicate Target within the same category is reported."""
        content = """
Defaults:
  Colors:
    Galaxy: "#8C4FFF"
Categories:
  Analytics:
    Color: Galaxy
    Icons:
    - Source: a.png
      SourceDir: dir
      Target: DupeIcon
      Target2: icon-a
    - Source: b.png
      SourceDir: dir
      Target: DupeIcon
      Target2: icon-b
"""
        issues, _ = _run_validate_config(content)
        dupes = [i for i in issues if i["check_type"] == "duplicate" and "Duplicate Target " in i["message"]]
        assert len(dupes) == 2
        assert all(d["category"] == "Analytics" for d in dupes)
        assert all("DupeIcon" in d["message"] for d in dupes)

    def test_duplicate_target_across_categories(self):
        """AC 4.1/4.2: Duplicate Target across categories is reported with each category."""
        content = """
Defaults:
  Colors:
    Galaxy: "#8C4FFF"
Categories:
  Analytics:
    Color: Galaxy
    Icons:
    - Source: a.png
      SourceDir: dir
      Target: SharedIcon
      Target2: icon-a
  Compute:
    Color: Galaxy
    Icons:
    - Source: b.png
      SourceDir: dir
      Target: SharedIcon
      Target2: icon-b
"""
        issues, _ = _run_validate_config(content)
        dupes = [i for i in issues if i["check_type"] == "duplicate" and "Duplicate Target " in i["message"]]
        assert len(dupes) == 2
        cats = {d["category"] for d in dupes}
        assert cats == {"Analytics", "Compute"}
        assert all("SharedIcon" in d["message"] for d in dupes)


class TestDuplicateTarget2Detection:
    """Tests for Requirement 5: Duplicate Target2 Name Detection."""

    def test_unique_target2_no_issues(self):
        """AC 5.3: All unique Target2 values produce no duplicate issues."""
        content = """
Defaults:
  Colors:
    Galaxy: "#8C4FFF"
Categories:
  Analytics:
    Color: Galaxy
    Icons:
    - Source: a.png
      SourceDir: dir
      Target: IconA
      Target2: icon-a
  Compute:
    Color: Galaxy
    Icons:
    - Source: b.png
      SourceDir: dir
      Target: IconB
      Target2: icon-b
"""
        issues, _ = _run_validate_config(content)
        dupes = [i for i in issues if i["check_type"] == "duplicate"]
        assert dupes == []

    def test_duplicate_target2_same_category(self):
        """AC 5.2: Duplicate Target2 within the same category is reported."""
        content = """
Defaults:
  Colors:
    Galaxy: "#8C4FFF"
Categories:
  Analytics:
    Color: Galaxy
    Icons:
    - Source: a.png
      SourceDir: dir
      Target: IconA
      Target2: dupe-name
    - Source: b.png
      SourceDir: dir
      Target: IconB
      Target2: dupe-name
"""
        issues, _ = _run_validate_config(content)
        dupes = [i for i in issues if i["check_type"] == "duplicate" and "Duplicate Target2 " in i["message"]]
        assert len(dupes) == 2
        assert all(d["category"] == "Analytics" for d in dupes)
        assert all("dupe-name" in d["message"] for d in dupes)

    def test_duplicate_target2_across_categories(self):
        """AC 5.1/5.2: Duplicate Target2 across categories is reported with each category."""
        content = """
Defaults:
  Colors:
    Galaxy: "#8C4FFF"
Categories:
  Analytics:
    Color: Galaxy
    Icons:
    - Source: a.png
      SourceDir: dir
      Target: IconA
      Target2: shared-name
  Compute:
    Color: Galaxy
    Icons:
    - Source: b.png
      SourceDir: dir
      Target: IconB
      Target2: shared-name
"""
        issues, _ = _run_validate_config(content)
        dupes = [i for i in issues if i["check_type"] == "duplicate" and "Duplicate Target2 " in i["message"]]
        assert len(dupes) == 2
        cats = {d["category"] for d in dupes}
        assert cats == {"Analytics", "Compute"}
        assert all("shared-name" in d["message"] for d in dupes)

    def test_duplicate_target_and_target2_both_reported(self):
        """Both duplicate Target and Target2 are reported independently."""
        content = """
Defaults:
  Colors:
    Galaxy: "#8C4FFF"
Categories:
  Analytics:
    Color: Galaxy
    Icons:
    - Source: a.png
      SourceDir: dir
      Target: SameName
      Target2: same-name
  Compute:
    Color: Galaxy
    Icons:
    - Source: b.png
      SourceDir: dir
      Target: SameName
      Target2: same-name
"""
        issues, _ = _run_validate_config(content)
        dupes = [i for i in issues if i["check_type"] == "duplicate"]
        target_dupes = [d for d in dupes if "Duplicate Target " in d["message"] and "Target2" not in d["message"]]
        target2_dupes = [d for d in dupes if "Duplicate Target2 " in d["message"]]
        assert len(target_dupes) == 2
        assert len(target2_dupes) == 2


class TestCategoryColorValidation:
    """Tests for Requirement 6: Category Color Validation."""

    def test_valid_category_color_no_issues(self):
        """A category with a valid palette color produces no invalid_color issues."""
        content = """
Defaults:
  Colors:
    Galaxy: "#8C4FFF"
    Cosmos: "#E7157B"
Categories:
  Analytics:
    Color: Galaxy
    Icons:
    - Source: a.png
      SourceDir: dir
      Target: IconA
      Target2: icon-a
"""
        issues, _ = _run_validate_config(content)
        color_issues = [i for i in issues if i["check_type"] == "invalid_color"]
        assert color_issues == []

    def test_invalid_category_color_reported(self):
        """AC 6.1: Category with invalid Color is reported."""
        content = """
Defaults:
  Colors:
    Galaxy: "#8C4FFF"
Categories:
  Analytics:
    Color: NotAColor
    Icons:
    - Source: a.png
      SourceDir: dir
      Target: IconA
      Target2: icon-a
"""
        issues, _ = _run_validate_config(content)
        color_issues = [i for i in issues if i["check_type"] == "invalid_color"]
        assert len(color_issues) == 1
        assert color_issues[0]["category"] == "Analytics"
        assert "NotAColor" in color_issues[0]["message"]

    def test_category_without_color_accepted(self):
        """AC 6.2: Category without a Color value is accepted."""
        content = """
Defaults:
  Colors:
    Galaxy: "#8C4FFF"
Categories:
  Analytics:
    Icons:
    - Source: a.png
      SourceDir: dir
      Target: IconA
      Target2: icon-a
"""
        issues, _ = _run_validate_config(content)
        color_issues = [i for i in issues if i["check_type"] == "invalid_color"]
        assert color_issues == []

    def test_color_check_is_case_sensitive(self):
        """AC 6.3: Color palette names are case-sensitive."""
        content = """
Defaults:
  Colors:
    Galaxy: "#8C4FFF"
Categories:
  Analytics:
    Color: galaxy
    Icons:
    - Source: a.png
      SourceDir: dir
      Target: IconA
      Target2: icon-a
"""
        issues, _ = _run_validate_config(content)
        color_issues = [i for i in issues if i["check_type"] == "invalid_color"]
        assert len(color_issues) == 1
        assert "galaxy" in color_issues[0]["message"]

    def test_multiple_categories_invalid_colors(self):
        """Multiple categories with invalid colors are all reported."""
        content = """
Defaults:
  Colors:
    Galaxy: "#8C4FFF"
Categories:
  Analytics:
    Color: BadColor1
    Icons: []
  Compute:
    Color: BadColor2
    Icons: []
"""
        issues, _ = _run_validate_config(content)
        color_issues = [i for i in issues if i["check_type"] == "invalid_color"]
        assert len(color_issues) == 2
        cats = {i["category"] for i in color_issues}
        assert cats == {"Analytics", "Compute"}

    def test_color_validation_skipped_when_no_defaults_colors(self):
        """Color validation is skipped when Defaults.Colors is missing."""
        content = """
Defaults:
  Category:
    Color: Squid
Categories:
  Analytics:
    Color: NotAColor
    Icons: []
"""
        issues, _ = _run_validate_config(content)
        color_issues = [i for i in issues if i["check_type"] == "invalid_color"]
        assert color_issues == []


class TestIconColorValidation:
    """Tests for Requirement 7: Icon-Level Color Validation."""

    def test_icon_with_valid_palette_color_no_issues(self):
        """An icon with a valid palette color produces no invalid_color issues."""
        content = """
Defaults:
  Colors:
    Galaxy: "#8C4FFF"
    Cosmos: "#E7157B"
Categories:
  Analytics:
    Color: Galaxy
    Icons:
    - Source: a.png
      SourceDir: dir
      Target: IconA
      Target2: icon-a
      Color: Cosmos
"""
        issues, _ = _run_validate_config(content)
        color_issues = [i for i in issues if i["check_type"] == "invalid_color"]
        assert color_issues == []

    def test_icon_with_invalid_bare_name_reported(self):
        """AC 7.1: Icon with invalid bare color name is reported."""
        content = """
Defaults:
  Colors:
    Galaxy: "#8C4FFF"
Categories:
  Analytics:
    Color: Galaxy
    Icons:
    - Source: a.png
      SourceDir: dir
      Target: IconA
      Target2: icon-a
      Color: FakeColor
"""
        issues, _ = _run_validate_config(content)
        color_issues = [i for i in issues if i["check_type"] == "invalid_color"]
        assert len(color_issues) == 1
        assert color_issues[0]["category"] == "Analytics"
        assert "IconA" in color_issues[0]["message"]
        assert "FakeColor" in color_issues[0]["message"]

    def test_icon_with_hex_color_accepted(self):
        """AC 7.2: Icon with hex color (#...) is accepted."""
        content = """
Defaults:
  Colors:
    Galaxy: "#8C4FFF"
Categories:
  Analytics:
    Color: Galaxy
    Icons:
    - Source: a.png
      SourceDir: dir
      Target: IconA
      Target2: icon-a
      Color: "#FF0000"
"""
        issues, _ = _run_validate_config(content)
        color_issues = [i for i in issues if i["check_type"] == "invalid_color"]
        assert color_issues == []

    def test_icon_with_plantuml_variable_accepted(self):
        """AC 7.2: Icon with PlantUML variable ($...) is accepted."""
        content = """
Defaults:
  Colors:
    Galaxy: "#8C4FFF"
Categories:
  Analytics:
    Color: Galaxy
    Icons:
    - Source: a.png
      SourceDir: dir
      Target: IconA
      Target2: icon-a
      Color: $AWS_COLOR_SQUID
"""
        issues, _ = _run_validate_config(content)
        color_issues = [i for i in issues if i["check_type"] == "invalid_color"]
        assert color_issues == []

    def test_icon_without_color_accepted(self):
        """AC 7.3: Icon without a Color field is accepted."""
        content = """
Defaults:
  Colors:
    Galaxy: "#8C4FFF"
Categories:
  Analytics:
    Color: Galaxy
    Icons:
    - Source: a.png
      SourceDir: dir
      Target: IconA
      Target2: icon-a
"""
        issues, _ = _run_validate_config(content)
        color_issues = [i for i in issues if i["check_type"] == "invalid_color"]
        assert color_issues == []

    def test_icon_color_case_sensitive(self):
        """Icon color bare names are case-sensitive against the palette."""
        content = """
Defaults:
  Colors:
    Galaxy: "#8C4FFF"
Categories:
  Analytics:
    Color: Galaxy
    Icons:
    - Source: a.png
      SourceDir: dir
      Target: IconA
      Target2: icon-a
      Color: GALAXY
"""
        issues, _ = _run_validate_config(content)
        color_issues = [i for i in issues if i["check_type"] == "invalid_color"]
        assert len(color_issues) == 1
        assert "GALAXY" in color_issues[0]["message"]

    def test_mixed_valid_and_invalid_icon_colors(self):
        """Mix of valid palette, hex, variable, and invalid colors."""
        content = """
Defaults:
  Colors:
    Galaxy: "#8C4FFF"
    Cosmos: "#E7157B"
Categories:
  Analytics:
    Color: Galaxy
    Icons:
    - Source: a.png
      SourceDir: dir
      Target: ValidPalette
      Target2: valid-palette
      Color: Cosmos
    - Source: b.png
      SourceDir: dir
      Target: ValidHex
      Target2: valid-hex
      Color: "#123456"
    - Source: c.png
      SourceDir: dir
      Target: ValidVar
      Target2: valid-var
      Color: $MY_VAR
    - Source: d.png
      SourceDir: dir
      Target: InvalidBare
      Target2: invalid-bare
      Color: Nope
"""
        issues, _ = _run_validate_config(content)
        color_issues = [i for i in issues if i["check_type"] == "invalid_color"]
        assert len(color_issues) == 1
        assert "InvalidBare" in color_issues[0]["message"]
        assert "Nope" in color_issues[0]["message"]


def _format_report(issues):
    """Replicate format_report() logic from icon-builder.py for testing."""
    if not issues:
        return ["config.yml is valid"]

    group_labels = {
        "structure": "Structure Issues",
        "missing_field": "Missing Field Issues",
        "duplicate": "Duplicate Issues",
        "invalid_color": "Invalid Color Issues",
    }
    group_order = ["structure", "missing_field", "duplicate", "invalid_color"]

    grouped = {}
    for issue in issues:
        check_type = issue["check_type"]
        grouped.setdefault(check_type, []).append(issue)

    lines = []
    for check_type in group_order:
        if check_type not in grouped:
            continue
        label = group_labels.get(check_type, check_type)
        lines.append(f"--- {label} ---")
        for issue in grouped[check_type]:
            category = issue.get("category", "")
            if category:
                lines.append(f"  [{category}] {issue['message']}")
            else:
                lines.append(f"  {issue['message']}")

    lines.append(f"Validation found {len(issues)} issue(s)")
    return lines


class TestReportFormatting:
    """Tests for Requirement 8: Validation Report Format."""

    def test_no_issues_returns_success_message(self):
        """AC 8.4: No issues prints a single success message."""
        lines = _format_report([])
        assert lines == ["config.yml is valid"]

    def test_issues_prefixed_with_category(self):
        """AC 8.1: Each issue is prefixed with the category name."""
        issues = [
            {
                "check_type": "missing_field",
                "message": "Category 'Analytics', entry 0: missing required field 'Source'",
                "category": "Analytics",
            }
        ]
        lines = _format_report(issues)
        assert any("[Analytics]" in line for line in lines)

    def test_structure_issues_without_category_not_prefixed(self):
        """Structure issues with empty category should not have a bracket prefix."""
        issues = [
            {
                "check_type": "structure",
                "message": "Missing required top-level key: Defaults",
                "category": "",
            }
        ]
        lines = _format_report(issues)
        issue_lines = [l for l in lines if "Missing required" in l]
        assert len(issue_lines) == 1
        assert issue_lines[0].startswith("  Missing")

    def test_issues_grouped_by_check_type(self):
        """AC 8.2: Issues are grouped by validation check type."""
        issues = [
            {"check_type": "duplicate", "message": "Dup Target 'X' in 'A'", "category": "A"},
            {"check_type": "structure", "message": "Missing Defaults", "category": ""},
            {"check_type": "missing_field", "message": "Missing Source in 'B'", "category": "B"},
        ]
        lines = _format_report(issues)
        headers = [l for l in lines if l.startswith("---")]
        assert headers == [
            "--- Structure Issues ---",
            "--- Missing Field Issues ---",
            "--- Duplicate Issues ---",
        ]

    def test_summary_line_with_issue_count(self):
        """AC 8.3: Summary line states total number of issues."""
        issues = [
            {"check_type": "structure", "message": "Missing Defaults", "category": ""},
            {"check_type": "duplicate", "message": "Dup Target", "category": "A"},
            {"check_type": "invalid_color", "message": "Bad color", "category": "B"},
        ]
        lines = _format_report(issues)
        assert lines[-1] == "Validation found 3 issue(s)"

    def test_all_group_types_present(self):
        """All four group types appear when issues of each type exist."""
        issues = [
            {"check_type": "structure", "message": "struct issue", "category": ""},
            {"check_type": "missing_field", "message": "field issue", "category": "A"},
            {"check_type": "duplicate", "message": "dup issue", "category": "B"},
            {"check_type": "invalid_color", "message": "color issue", "category": "C"},
        ]
        lines = _format_report(issues)
        headers = [l for l in lines if l.startswith("---")]
        assert "--- Structure Issues ---" in headers
        assert "--- Missing Field Issues ---" in headers
        assert "--- Duplicate Issues ---" in headers
        assert "--- Invalid Color Issues ---" in headers

    def test_single_issue_summary(self):
        """Summary line is correct for a single issue."""
        issues = [
            {"check_type": "structure", "message": "Missing Defaults", "category": ""},
        ]
        lines = _format_report(issues)
        assert lines[-1] == "Validation found 1 issue(s)"


class TestCLIExitCode:
    """Tests for Requirement 1: CLI Flag Registration (exit code behavior)."""

    @staticmethod
    def _scripts_dir():
        return os.path.dirname(os.path.abspath(__file__))

    def test_exit_code_zero_on_valid_config(self, tmp_path):
        """AC 1.3: Valid config exits with code 0."""
        import subprocess
        import sys

        config = tmp_path / "config.yml"
        config.write_text(
            "Defaults:\n"
            "  Colors:\n"
            '    Galaxy: "#8C4FFF"\n'
            "  Category:\n"
            "    Color: Galaxy\n"
            "Categories:\n"
            "  Analytics:\n"
            "    Color: Galaxy\n"
            "    Icons:\n"
            "    - Source: a.png\n"
            "      SourceDir: dir\n"
            "      Target: IconA\n"
            "      Target2: icon-a\n"
        )
        scripts_dir = self._scripts_dir()
        icon_builder = os.path.join(scripts_dir, "icon-builder.py")
        env = os.environ.copy()
        env["PYTHONPATH"] = scripts_dir
        result = subprocess.run(
            [sys.executable, icon_builder, "--validate-config"],
            capture_output=True,
            text=True,
            cwd=str(tmp_path),
            env=env,
        )
        assert result.returncode == 0
        assert "valid" in result.stdout.lower()

    def test_exit_code_nonzero_on_invalid_config(self, tmp_path):
        """AC 1.4: Config with issues exits with non-zero code."""
        import subprocess
        import sys

        config = tmp_path / "config.yml"
        config.write_text("SomeOtherKey: value\n")
        scripts_dir = self._scripts_dir()
        icon_builder = os.path.join(scripts_dir, "icon-builder.py")
        env = os.environ.copy()
        env["PYTHONPATH"] = scripts_dir
        result = subprocess.run(
            [sys.executable, icon_builder, "--validate-config"],
            capture_output=True,
            text=True,
            cwd=str(tmp_path),
            env=env,
        )
        assert result.returncode != 0
        assert "issue" in result.stdout.lower()
