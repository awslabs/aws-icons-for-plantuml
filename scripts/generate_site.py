#!/usr/bin/env python3
# Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT (For details, see https://github.com/awslabs/aws-icons-for-plantuml/blob/main/LICENSE)

"""generate_site.py: Generate static icon browser site from config.yml"""

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
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


# Resolve paths relative to the scripts/ directory
_SCRIPTS_DIR = Path(__file__).parent
_TEMPLATES_DIR = _SCRIPTS_DIR / "site_templates"
_ASSETS_DIR = _SCRIPTS_DIR / "site_assets"


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
    """An example PlantUML diagram rendered for the examples page.

    Each example corresponds to a single .puml file under examples/. A file
    may render to one or more PNG images (PlantUML emits multiple files when a
    source contains several @startuml..@enduml blocks or newpage directives).
    """

    title: str  # Display title, e.g. "Basic Usage"
    source_path: str  # Relative path in repo, e.g. "examples/Basic Usage.puml"
    puml_url: str  # Raw GitHub URL to the .puml file (current version)
    source_text: str  # Full text of the .puml file
    image_paths: list[str] = field(default_factory=list)
    # Site-relative PNG paths, e.g. ["examples/Basic Usage.png"]


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


# Base URL for raw GitHub content on the main branch
_GITHUB_RAW_BASE = (
    "https://raw.githubusercontent.com/awslabs/aws-icons-for-plantuml/main"
)

# Repository root (parent of scripts/)
_REPO_ROOT = _SCRIPTS_DIR.parent
_EXAMPLES_DIR = _REPO_ROOT / "examples"
_DIST_DIR = _REPO_ROOT / "dist"

# Example subdirectories to exclude from the examples page. The architecture
# blog figures are pinned to older icon releases (renamed/removed icons) and
# cannot render against the current release, so they are archived-only.
_EXCLUDED_EXAMPLE_DIRS = frozenset({"architecture-blog"})

# Bundled PlantUML JAR used to render examples at build time.
_PLANTUML_JAR = next(iter(sorted(_SCRIPTS_DIR.glob("plantuml-mit-*.jar"))), None)

# Matches the "!define AWSPuml <url>/dist" line so it can be redirected at
# render time to the locally built dist/ directory. This guarantees examples
# render against the current release icons regardless of the tag hardcoded in
# the source file.
_AWSPUML_DEFINE_RE = re.compile(
    r"^(!define\s+AWSPuml\s+).*$", re.MULTILINE
)


def _title_from_path(source_path: str) -> str:
    """Derive a human-readable title from an example's relative path.

    The examples/ prefix is stripped and the .puml suffix removed. Files in
    subdirectories are prefixed with the subdirectory name for context, e.g.
    "examples/theme-testing/class.puml" -> "theme-testing / class".

    Args:
        source_path: Repo-relative path, e.g. "examples/Basic Usage.puml".

    Returns:
        A display title string.
    """
    rel = source_path
    rel = rel.removeprefix("examples/")
    rel = rel.removesuffix(".puml")
    return rel.replace("/", " / ")


def discover_examples() -> list[dict]:
    """Discover all .puml files under examples/ (recursively).

    Returns:
        A list of specs sorted by path, each a dict with "source_path"
        (repo-relative, POSIX separators) and "title".
    """
    specs: list[dict] = []
    if not _EXAMPLES_DIR.is_dir():
        print(f"Warning: examples directory not found: {_EXAMPLES_DIR}")
        return specs

    for puml_path in sorted(_EXAMPLES_DIR.rglob("*.puml")):
        # Skip archived example directories (relative to examples/).
        rel_parts = puml_path.relative_to(_EXAMPLES_DIR).parts
        if rel_parts and rel_parts[0] in _EXCLUDED_EXAMPLE_DIRS:
            continue

        source_path = puml_path.relative_to(_REPO_ROOT).as_posix()
        specs.append(
            {
                "source_path": source_path,
                "title": _title_from_path(source_path),
            }
        )

    return specs


def _slugify(source_path: str) -> str:
    """Build a stable, filesystem-safe slug from an example's repo path.

    Example: "examples/theme-testing/class.puml" -> "theme-testing_class".

    Args:
        source_path: Repo-relative POSIX path to the .puml file.

    Returns:
        A slug suitable for use as a PNG filename stem.
    """
    rel = source_path
    rel = rel.removeprefix("examples/")
    rel = rel.removesuffix(".puml")
    slug = re.sub(r"[^A-Za-z0-9._-]+", "_", rel)
    return slug.strip("_") or "example"


def _render_puml(
    source_path: Path,
    rel_source_path: str,
    out_dir: Path,
    dist_dir: Path,
) -> list[Path]:
    """Render a single .puml file to one or more PNG files.

    The source is copied to a temp file with its "!define AWSPuml" line
    rewritten to point at the local dist/ directory, then rendered with the
    bundled PlantUML JAR. PlantUML names output files after the diagram title
    (the text after "@startuml"), which is unpredictable and may collide across
    examples, so we render into an isolated temp directory and then move the
    generated PNG(s) into ``out_dir`` under a slug derived from the source path.
    A file may produce multiple PNGs (one per @startuml block / newpage).

    Args:
        source_path: Absolute path to the .puml source file.
        rel_source_path: Repo-relative POSIX path (used to build the slug).
        out_dir: Directory to write final PNG output into.
        dist_dir: Absolute path to the local dist/ directory used for includes.

    Returns:
        A sorted list of final PNG Paths in out_dir (empty on failure).
    """
    if _PLANTUML_JAR is None or not _PLANTUML_JAR.is_file():
        return []

    out_dir.mkdir(parents=True, exist_ok=True)
    original = source_path.read_text(encoding="utf-8")
    # Redirect AWSPuml includes to the local dist/ so examples render against
    # the current release icons.
    patched = _AWSPUML_DEFINE_RE.sub(rf"\g<1>{dist_dir.as_posix()}", original)

    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        tmp_src = tmp_dir / source_path.name
        tmp_src.write_text(patched, encoding="utf-8")
        render_out = tmp_dir / "out"
        render_out.mkdir()

        cmd = [
            "java",
            "-jar",
            str(_PLANTUML_JAR),
            "-tpng",
            "-nometadata",
            "-o",
            str(render_out),
            str(tmp_src),
        ]
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120,
                check=False,
            )
        except (OSError, subprocess.TimeoutExpired) as e:
            print(f"  Warning: render failed for {rel_source_path}: {e}")
            return []

        # On any non-zero exit, PlantUML may still emit an "error" PNG that
        # just contains the error text. Treat the render as failed and discard
        # such output rather than publishing a broken image.
        if result.returncode != 0:
            msg = (result.stderr or result.stdout or "").strip().splitlines()
            detail = msg[-1] if msg else "unknown error"
            print(f"  Warning: PlantUML error for {rel_source_path}: {detail}")
            return []

        generated = sorted(render_out.glob("*.png"))

        # Move generated PNGs into out_dir under a deterministic slug. Single
        # diagram -> "<slug>.png"; multiple -> "<slug>-1.png", "<slug>-2.png".
        slug = _slugify(rel_source_path)
        final: list[Path] = []
        for i, png in enumerate(generated):
            if len(generated) == 1:
                dest_name = f"{slug}.png"
            else:
                dest_name = f"{slug}-{i + 1}.png"
            dest = out_dir / dest_name
            shutil.move(str(png), str(dest))
            final.append(dest)

    return final


def build_examples(
    output_dir: Path,
    skip_render: bool = False,
) -> list[ExampleDiagram]:
    """Discover, render, and package all example diagrams.

    Renders every examples/*.puml file to PNG(s) under
    ``<output_dir>/examples/`` using the local dist/ icons (current release
    only), reads each file's source text, and builds ExampleDiagram entries
    for the examples page.

    Args:
        output_dir: The site output directory (PNGs go in its examples/ subdir).
        skip_render: When True, skip PlantUML rendering (source text only).

    Returns:
        A list of ExampleDiagram instances sorted by source path.
    """
    specs = discover_examples()
    examples: list[ExampleDiagram] = []

    png_out_dir = output_dir / "examples"
    render_enabled = not skip_render

    if render_enabled and _PLANTUML_JAR is None:
        print("Warning: PlantUML JAR not found in scripts/; skipping render")
        render_enabled = False
    elif render_enabled and not _DIST_DIR.is_dir():
        print(
            f"Warning: dist/ not found at {_DIST_DIR}; "
            "run icon-builder.py first. Skipping render."
        )
        render_enabled = False

    rendered_count = 0
    for spec in specs:
        source_path = spec["source_path"]
        abs_src = _REPO_ROOT / source_path
        try:
            source_text = abs_src.read_text(encoding="utf-8")
        except OSError as e:
            print(f"  Warning: cannot read {source_path}: {e}")
            continue

        image_paths: list[str] = []
        if render_enabled:
            pngs = _render_puml(abs_src, source_path, png_out_dir, _DIST_DIR)
            image_paths = [f"examples/{p.name}" for p in pngs]
            if image_paths:
                rendered_count += 1

        examples.append(
            ExampleDiagram(
                title=spec["title"],
                source_path=source_path,
                puml_url=f"{_GITHUB_RAW_BASE}/{quote(source_path)}",
                source_text=source_text,
                image_paths=image_paths,
            )
        )

    if render_enabled:
        print(
            f"  Rendered {rendered_count} of {len(examples)} examples to "
            f"{png_out_dir}/"
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
            with urllib.request.urlopen(req, timeout=30) as resp:
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

    # Load the templates
    try:
        template = env.get_template("index.html.j2")
        examples_template = env.get_template("examples.html.j2")
    except TemplateNotFound as e:
        print(f"Error: Template not found: {e}")
        sys.exit(1)

    # Convert dataclasses to JSON-serializable dicts
    icon_data_dict = icon_data_to_dict(icon_data)
    examples_list = [
        {
            "title": ex.title,
            "source_path": ex.source_path,
            "puml_url": ex.puml_url,
            "source_text": ex.source_text,
            "image_paths": ex.image_paths,
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
        examples_html = examples_template.render(
            examples=examples_list,
            current_version=current_version,
            examples_json=json.dumps(examples_list),
        )
    except TemplateError as e:
        print(f"Error: Template rendering failed: {e}")
        sys.exit(1)

    # Write rendered HTML
    try:
        (out_path / "index.html").write_text(html, encoding="utf-8")
        (out_path / "examples.html").write_text(examples_html, encoding="utf-8")
    except PermissionError as e:
        print(f"Error: Cannot write to output directory '{out_path}': {e}")
        sys.exit(1)

    # Copy static assets
    for asset_name in ("style.css", "app.js", "examples.js"):
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
    parser.add_argument(
        "--skip-render",
        action="store_true",
        default=False,
        help="Skip rendering example diagrams with PlantUML (source only)",
    )
    args = parser.parse_args()

    # Load config from scripts/ directory
    config_path = _SCRIPTS_DIR / "config.yml"
    config = load_config(str(config_path))

    # Extract data
    icon_data = extract_icon_data(config)
    category_mapping = build_category_mapping()

    # Discover and render example diagrams into the output directory. PNGs are
    # written to <output>/examples/ and are never committed to source; they
    # exist only in the generated GitHub Pages artifact.
    out_path = Path(args.output_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    print("Rendering example diagrams...")
    examples = build_examples(out_path, skip_render=args.skip_render)

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

    total_icons = sum(len(cat.icons) for cat in icon_data.categories.values())
    print(
        f"Success: {len(icon_data.categories)} categories, "
        f"{total_icons} icons, {len(examples)} examples"
    )


if __name__ == "__main__":
    main()
