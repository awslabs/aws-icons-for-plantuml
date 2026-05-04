#!/usr/bin/env python3
# Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT (For details, see https://github.com/awslabs/aws-icons-for-plantuml/blob/main/LICENSE)

"""generate_site.py: Generate static icon browser site from config.yml"""

import argparse
import json
import shutil
import sys
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import quote

import yaml
from jinja2 import Environment, FileSystemLoader, TemplateError, TemplateNotFound


def _import_upgrade_data():
    """Import BREAKING_CHANGES and SUPPORTED_VERSIONS from upgrade.py.

    upgrade.py has module-level argparse that runs on import, so we
    temporarily override sys.argv to prevent it from failing when
    generate_site.py is invoked with its own CLI arguments.
    """
    saved_argv = sys.argv
    sys.argv = ["upgrade.py", "dummy"]
    try:
        from upgrade import BREAKING_CHANGES, SUPPORTED_VERSIONS
    finally:
        sys.argv = saved_argv
    return BREAKING_CHANGES, SUPPORTED_VERSIONS


BREAKING_CHANGES, SUPPORTED_VERSIONS = _import_upgrade_data()


@dataclass
class IconEntry:
    """A single icon extracted from config.yml."""

    target: str  # PascalCase name, e.g. "Athena"
    target2: str  # kebab-case name, e.g. "athena"
    category: str  # Parent category, e.g. "Analytics"


@dataclass
class CategoryData:
    """A category with its color and icons."""

    name: str  # e.g. "Analytics"
    color: str  # Hex color, e.g. "#8C4FFF"
    color_name: str  # Named color, e.g. "Galaxy"
    icons: list[IconEntry] = field(default_factory=list)


@dataclass
class IconData:
    """Complete icon catalog for template rendering."""

    categories: dict[str, CategoryData] = field(default_factory=dict)
    defaults: dict = field(default_factory=dict)


@dataclass
class ExampleDiagram:
    """An example PlantUML diagram for the gallery."""

    title: str  # Display title
    description: str  # Brief description
    puml_url: str  # Raw GitHub URL to the .puml file
    proxy_url: str  # PlantUML proxy rendering URL
    source_path: str  # Relative path in repo, e.g. "examples/HelloWorld.puml"


def load_config(path: str) -> dict:
    """Read and parse config.yml using PyYAML.

    Args:
        path: Path to the YAML config file.

    Returns:
        Parsed config dictionary.

    Exits with code 1 on missing file, invalid YAML, or missing required fields.
    """
    config_path = Path(path)
    if not config_path.is_file():
        print(f"Error: Config file not found: {config_path}")
        sys.exit(1)

    try:
        with open(config_path, encoding="utf-8") as f:
            config = yaml.safe_load(f)
    except yaml.YAMLError as e:
        print(f"Error: Invalid YAML in {config_path}: {e}")
        sys.exit(1)

    if not isinstance(config, dict):
        print(f"Error: Config file {config_path} does not contain a YAML mapping")
        sys.exit(1)

    if "Categories" not in config:
        print(f"Error: Missing required field 'Categories' in {config_path}")
        sys.exit(1)

    if "Defaults" not in config:
        print(f"Error: Missing required field 'Defaults' in {config_path}")
        sys.exit(1)

    return config


def extract_icon_data(config: dict) -> IconData:
    """Extract categories, icons, and color mappings from a parsed config dict.

    Resolves color names (e.g. "Galaxy") to hex values (e.g. "#8C4FFF")
    using the Defaults.Colors mapping.

    Args:
        config: Parsed config dictionary from load_config().

    Returns:
        IconData with all categories and their icons.
    """
    defaults = config.get("Defaults", {})
    color_map = defaults.get("Colors", {})
    default_color_name = defaults.get("Category", {}).get("Color", "Squid")

    categories_raw = config.get("Categories", {})
    categories: dict[str, CategoryData] = {}

    for cat_name, cat_data in categories_raw.items():
        # Resolve the category color name to a hex value
        color_name = cat_data.get("Color", default_color_name)
        color_hex = color_map.get(color_name, color_name)

        icons = []
        for icon in cat_data.get("Icons", []):
            target = icon.get("Target", "")
            target2 = icon.get("Target2", "")
            if target:
                # Older config versions may lack Target2; derive from Target
                if not target2:
                    target2 = target.lower()
                icons.append(
                    IconEntry(target=target, target2=target2, category=cat_name)
                )

        categories[cat_name] = CategoryData(
            name=cat_name,
            color=color_hex,
            color_name=color_name,
            icons=icons,
        )

    return IconData(categories=categories, defaults=defaults)


def build_category_mapping() -> dict:
    """Build the cross-version category rename/deletion mapping table.

    Iterates through BREAKING_CHANGES from upgrade.py and extracts
    category-level RENAMED entries. A rename maps an old category name
    to a new one; a deletion maps it to None.

    Returns:
        A JSON-serializable dict keyed by version string, each containing
        "renames" (dict of old→new name) and "deletions" (list of removed
        category names). Only versions with at least one change are included.
    """
    mapping: dict[str, dict] = {}

    for version in SUPPORTED_VERSIONS:
        if version not in BREAKING_CHANGES:
            continue

        version_changes = BREAKING_CHANGES[version]
        renames: dict[str, str] = {}
        deletions: list[str] = []

        for category, changes in version_changes.items():
            if "RENAMED" not in changes:
                continue

            new_name = changes["RENAMED"]
            if new_name is None:
                deletions.append(category)
            else:
                renames[category] = new_name

        if renames or deletions:
            mapping[version] = {
                "renames": renames,
                "deletions": deletions,
            }

    return mapping


# Base URL for raw GitHub content
_GITHUB_RAW_BASE = (
    "https://raw.githubusercontent.com/awslabs/aws-icons-for-plantuml/main"
)

# PlantUML proxy service base URL
_PLANTUML_PROXY_BASE = "http://www.plantuml.com/plantuml/proxy"


def build_example_list() -> list[ExampleDiagram]:
    """Build the curated list of example diagrams for the gallery.

    Each example references a .puml file in the repository's examples/
    directory. The puml_url points to the raw GitHub content for the file,
    and the proxy_url uses the PlantUML proxy service to render it as an
    image.

    Returns:
        A list of ExampleDiagram instances for the gallery section.
    """
    examples_spec = [
        {
            "title": "Hello World",
            "description": "Basic two-service diagram",
            "source_path": "examples/HelloWorld.puml",
        },
        {
            "title": "Basic Usage",
            "description": "IoT Rules Engine workflow",
            "source_path": "examples/Basic Usage.puml",
        },
        {
            "title": "Raw Image Usage",
            "description": "Using icon images directly",
            "source_path": "examples/Raw Image Usage.puml",
        },
        {
            "title": "Sequence - Technical",
            "description": "Sequence diagram with stereotypes",
            "source_path": "examples/Sequence - Technical.puml",
        },
        {
            "title": "Sequence - Images",
            "description": "Sequence diagram with images",
            "source_path": "examples/Sequence - Images.puml",
        },
        {
            "title": "Groups - VPC",
            "description": "VPC with availability zones",
            "source_path": "examples/Groups - VPC.puml",
        },
        {
            "title": "Groups - CodePipeline",
            "description": "CodePipeline approval workflow",
            "source_path": "examples/Groups - CodePipeline.puml",
        },
    ]

    examples: list[ExampleDiagram] = []
    for spec in examples_spec:
        source_path = spec["source_path"]
        puml_url = f"{_GITHUB_RAW_BASE}/{quote(source_path)}"
        proxy_url = (
            f"{_PLANTUML_PROXY_BASE}?idx=0&src={quote(puml_url, safe='')}"
        )
        examples.append(
            ExampleDiagram(
                title=spec["title"],
                description=spec["description"],
                puml_url=puml_url,
                proxy_url=proxy_url,
                source_path=source_path,
            )
        )

    return examples


# GitHub raw content URL for per-version config.yml
_GITHUB_RAW_CONFIG_URL = (
    "https://raw.githubusercontent.com/awslabs/aws-icons-for-plantuml"
    "/{version}/scripts/config.yml"
)


def fetch_version_configs(
    versions: list[str],
) -> dict[str, dict]:
    """Fetch config.yml from GitHub for each supported version tag.

    Downloads the config.yml for each version via the GitHub raw content
    URL, parses it with PyYAML, extracts icon data, and converts to the
    JSON-serializable dict format.

    Args:
        versions: List of version tag strings (e.g. ["v13.0", "v23.0"]).

    Returns:
        A dict mapping version string to its icon_data_dict.
        Versions that fail to fetch are skipped with a warning.
    """
    version_data: dict[str, dict] = {}

    for version in versions:
        url = _GITHUB_RAW_CONFIG_URL.format(version=version)
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "generate_site"})
            with urllib.request.urlopen(req, timeout=30) as resp:  # noqa: S310
                raw = resp.read().decode("utf-8")
            config = yaml.safe_load(raw)
        except Exception as e:  # noqa: BLE001
            print(f"Warning: Failed to fetch config.yml for {version}: {e}")
            continue

        if not isinstance(config, dict):
            print(f"Warning: config.yml for {version} is not a valid mapping")
            continue

        if "Categories" not in config or "Defaults" not in config:
            print(
                f"Warning: config.yml for {version} missing "
                "required Categories/Defaults"
            )
            continue

        icon_data = extract_icon_data(config)
        version_data[version] = icon_data_to_dict(icon_data)
        print(f"  Fetched config for {version}: {len(icon_data.categories)} categories")

    return version_data


# Resolve paths relative to the scripts/ directory
_SCRIPTS_DIR = Path(__file__).parent
_TEMPLATES_DIR = _SCRIPTS_DIR / "site_templates"
_ASSETS_DIR = _SCRIPTS_DIR / "site_assets"


def icon_data_to_dict(icon_data: IconData) -> dict:
    """Convert an IconData dataclass to a JSON-serializable dict.

    Uses camelCase keys for JavaScript consumption:
    - colorName, pumlPath, pngPath

    Args:
        icon_data: The IconData structure to convert.

    Returns:
        A dict matching the embedded JSON format from the design doc.
    """
    categories = {}
    for cat_name, cat_data in icon_data.categories.items():
        icons = []
        for icon in cat_data.icons:
            icons.append(
                {
                    "target": icon.target,
                    "target2": icon.target2,
                    "pumlPath": f"{icon.category}/{icon.target}.puml",
                    "pngPath": f"{icon.category}/{icon.target}.png",
                }
            )
        categories[cat_name] = {
            "color": cat_data.color,
            "colorName": cat_data.color_name,
            "icons": icons,
        }

    # Build a simplified defaults dict with color mappings
    colors = icon_data.defaults.get("Colors", {})
    defaults = {"colors": colors}

    return {"categories": categories, "defaults": defaults}


def render_site(
    output_dir: str,
    icon_data: IconData,
    category_mapping: dict,
    examples: list[ExampleDiagram],
    supported_versions: list[str],
    current_version: str,
    icon_data_by_version: dict | None = None,
) -> None:
    """Render the static site to the output directory.

    Sets up Jinja2 templates, renders index.html with all data,
    and copies static assets (style.css, app.js) to the output.

    Args:
        output_dir: Path to the output directory (relative to project root).
        icon_data: Extracted icon catalog data.
        category_mapping: Cross-version category rename/deletion mapping.
        examples: List of example diagrams for the gallery.
        supported_versions: Ordered list of version strings.
        current_version: The default/latest version string.
        icon_data_by_version: Per-version icon data dicts for version switching.

    Exits with code 1 on template errors, render errors, or permission errors.
    """
    # Create output directory
    out_path = Path(output_dir)
    try:
        out_path.mkdir(parents=True, exist_ok=True)
    except PermissionError as e:
        print(f"Error: Cannot create output directory '{out_path}': {e}")
        sys.exit(1)

    # Set up Jinja2 environment
    if not _TEMPLATES_DIR.is_dir():
        print(f"Error: Templates directory not found: {_TEMPLATES_DIR}")
        sys.exit(1)

    env = Environment(
        loader=FileSystemLoader(str(_TEMPLATES_DIR)),
        autoescape=True,
    )

    # Load and render the main template
    try:
        template = env.get_template("index.html.j2")
    except TemplateNotFound as e:
        print(f"Error: Template not found: {e}")
        sys.exit(1)

    # Convert dataclasses to JSON-serializable dicts
    icon_data_dict = icon_data_to_dict(icon_data)
    examples_list = [
        {
            "title": ex.title,
            "description": ex.description,
            "puml_url": ex.puml_url,
            "proxy_url": ex.proxy_url,
            "source_path": ex.source_path,
        }
        for ex in examples
    ]

    # Build the per-version data, ensuring current version is included
    if icon_data_by_version is None:
        icon_data_by_version = {}
    icon_data_by_version[current_version] = icon_data_dict

    try:
        html = template.render(
            icon_data=icon_data_dict,
            category_mapping=category_mapping,
            examples=examples_list,
            supported_versions=supported_versions,
            current_version=current_version,
            # Pre-serialized JSON for inline <script> blocks
            icon_data_json=json.dumps(icon_data_dict),
            category_mapping_json=json.dumps(category_mapping),
            supported_versions_json=json.dumps(supported_versions),
            icon_data_by_version_json=json.dumps(icon_data_by_version),
        )
    except TemplateError as e:
        print(f"Error: Template rendering failed: {e}")
        sys.exit(1)

    # Write rendered HTML
    try:
        (out_path / "index.html").write_text(html, encoding="utf-8")
    except PermissionError as e:
        print(f"Error: Cannot write to output directory '{out_path}': {e}")
        sys.exit(1)

    # Copy static assets
    for asset_name in ("style.css", "app.js"):
        src = _ASSETS_DIR / asset_name
        if src.is_file():
            shutil.copy2(src, out_path / asset_name)

    print(f"Site generated in {out_path}/")


def main() -> None:
    """Entry point for site generation."""
    parser = argparse.ArgumentParser(
        description="Generate the AWS Icons for PlantUML browser site"
    )
    parser.add_argument(
        "--output-dir",
        default="site",
        help="Output directory for the generated site (default: site)",
    )
    parser.add_argument(
        "--skip-fetch",
        action="store_true",
        default=False,
        help="Skip fetching per-version config.yml from GitHub",
    )
    args = parser.parse_args()

    # Load config from scripts/ directory
    config_path = _SCRIPTS_DIR / "config.yml"
    config = load_config(str(config_path))

    # Extract data
    icon_data = extract_icon_data(config)
    category_mapping = build_category_mapping()
    examples = build_example_list()

    # Fetch per-version icon data from GitHub
    icon_data_by_version: dict[str, dict] = {}
    if not args.skip_fetch:
        print("Fetching per-version config.yml from GitHub...")
        icon_data_by_version = fetch_version_configs(SUPPORTED_VERSIONS)
    else:
        print("Skipping per-version config fetch (--skip-fetch)")

    # Render site
    render_site(
        output_dir=args.output_dir,
        icon_data=icon_data,
        category_mapping=category_mapping,
        examples=examples,
        supported_versions=SUPPORTED_VERSIONS,
        current_version=SUPPORTED_VERSIONS[-1],
        icon_data_by_version=icon_data_by_version,
    )

    total_icons = sum(
        len(cat.icons) for cat in icon_data.categories.values()
    )
    print(
        f"Success: {len(icon_data.categories)} categories, "
        f"{total_icons} icons, {len(examples)} examples"
    )


if __name__ == "__main__":
    main()
