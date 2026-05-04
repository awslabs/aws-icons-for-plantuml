# Implementation Plan: GitHub Pages Icon Browser

## Overview

Build a static site generator and client-side icon browser for the AWS Icons for PlantUML catalog. The implementation follows a bottom-up approach: add the Jinja2 dependency, build the Python data extraction and site generation layer, create the HTML/CSS/JS templates and assets, wire everything together, add the GitHub Actions deployment workflow, and validate with tests.

## Tasks

- [x] 1. Add Jinja2 dependency and set up project structure
  - [x] 1.1 Add Jinja2 to pyproject.toml dependencies
    - Add `jinja2>=3.1.0` to the `dependencies` list in `pyproject.toml`
    - Run `uv sync` to install the new dependency
    - _Requirements: 1.3, 1.6_

  - [x] 1.2 Create directory structure for site templates and assets
    - Create `scripts/site_templates/` directory
    - Create `scripts/site_assets/` directory
    - Create empty placeholder files: `scripts/site_templates/index.html.j2`, `scripts/site_templates/_icon_card.html.j2`, `scripts/site_templates/_example_card.html.j2`
    - _Requirements: 1.2, 1.3_

- [x] 2. Implement site generator data extraction (`scripts/generate_site.py`)
  - [x] 2.1 Implement `load_config` and `extract_icon_data` functions
    - Create `scripts/generate_site.py` with the shebang and license header matching existing scripts
    - Implement `load_config(path)` to read and parse `config.yml` using PyYAML
    - Implement `extract_icon_data(config)` to extract categories, icons (Target, Target2), and color mappings into an `IconData` dataclass structure
    - Define dataclasses: `IconEntry`, `CategoryData`, `IconData` as specified in the design
    - Handle error cases: missing file, invalid YAML, missing required fields (Categories, Defaults) — print error and `sys.exit(1)`
    - _Requirements: 1.1, 1.4, 1.5_

  - [ ]* 2.2 Write property test for config extraction (Property 1)
    - **Property 1: Config extraction preserves all icons and categories**
    - Use Hypothesis to generate valid config dicts with categories, icons, and color mappings
    - Assert every input category appears as a key in the output, every icon's Target/Target2 is present, and colors are correctly resolved
    - **Validates: Requirements 1.1, 1.4**

  - [x] 2.3 Implement `build_category_mapping` function
    - Import `BREAKING_CHANGES` and `SUPPORTED_VERSIONS` from `upgrade.py`
    - Build the category mapping table by iterating through `BREAKING_CHANGES` and extracting `RENAMED` entries (both renames and deletions where `RENAMED: None`)
    - Output the JSON-serializable dict structure as specified in the design data model
    - _Requirements: 11.1, 11.2, 11.3, 11.4_

  - [x] 2.4 Implement `build_example_list` function
    - Define the curated list of example diagrams with title, description, source path, and URLs
    - Construct `puml_url` using the raw GitHub content URL pattern
    - Construct `proxy_url` using the PlantUML proxy service URL pattern
    - Include at minimum: HelloWorld, Basic Usage, Raw Image Usage, Sequence - Technical, Sequence - Images, Groups - VPC, Groups - CodePipeline
    - _Requirements: 7.1, 7.2, 7.3, 7.4_

  - [x] 2.5 Implement `render_site` function and `main` entry point
    - Set up Jinja2 `FileSystemLoader` pointing to `scripts/site_templates/`
    - Render `index.html.j2` with icon_data, category_mapping, examples, supported_versions, and current_version as template context
    - Embed `ICON_DATA`, `CATEGORY_MAPPING`, and `SUPPORTED_VERSIONS` as inline `<script>` JSON blocks
    - Copy static assets (`style.css`, `app.js`) from `scripts/site_assets/` to the output directory
    - Create the output `site/` directory, handle permission errors with `sys.exit(1)`
    - Wire up `main()` with argparse or simple CLI, make script executable via `uv run scripts/generate_site.py`
    - _Requirements: 1.2, 1.3, 1.5, 1.6_

  - [ ]* 2.6 Write unit tests for `load_config` and `build_category_mapping`
    - Test `load_config` with valid YAML, missing file, and invalid YAML
    - Test `build_category_mapping` produces correct rename/deletion entries for all version transitions (v13.0 ARVR→VRAR, v16.0 VRAR→deleted, v19.0 MachineLearning→ArtificialIntelligence, etc.)
    - Test `build_example_list` returns expected examples with correct URLs
    - _Requirements: 1.1, 1.5, 11.1, 11.3, 11.4_

- [x] 3. Checkpoint
  - Ensure all tests pass, ask the user if questions arise.

- [x] 4. Create Jinja2 templates (`scripts/site_templates/`)
  - [x] 4.1 Create the main page template `index.html.j2`
    - Use semantic HTML5 elements: `<nav>`, `<main>`, `<section>`, `<header>`, `<footer>`
    - Include top navigation bar with project title "AWS Icons for PlantUML" and GitHub repo link
    - Add version selector dropdown populated from `supported_versions`
    - Add search bar input with ARIA label
    - Add category filter checkbox area
    - Add icon count display (total and visible)
    - Add icon grid area with category sections, each containing icon cards via the `_icon_card.html.j2` partial
    - Add example gallery section using the `_example_card.html.j2` partial
    - Embed three `<script>` JSON blocks: `window.ICON_DATA`, `window.CATEGORY_MAPPING`, `window.SUPPORTED_VERSIONS`
    - Include `<link>` to `style.css` and `<script src="app.js">`
    - _Requirements: 1.3, 2.1, 2.5, 3.1, 3.2, 5.1, 8.3, 10.1, 10.4, 10.5_

  - [x] 4.2 Create the icon card partial `_icon_card.html.j2`
    - Render each icon as a card with: PNG `<img>` (with `alt` text containing Target name and category), Target name text, PUML include path, and a copy button
    - Set `data-target`, `data-target2`, `data-category` attributes on the card element for JS filtering
    - Construct image `src` using the GitHub raw content URL pattern with the current version
    - Add `onerror` handler attribute for broken image fallback
    - _Requirements: 2.2, 2.3, 6.1, 10.2_

  - [ ]* 4.3 Write property test for rendered HTML completeness (Property 2)
    - **Property 2: Rendered HTML contains complete icon cards**
    - Use Hypothesis to generate `IconData` with varying categories and icons
    - Render the templates and assert: a category section heading exists for every category, an icon card exists for every icon, each card contains the Target name, PNG URL, and PUML path
    - **Validates: Requirements 2.1, 2.2**

  - [ ]* 4.4 Write property test for alt text presence (Property 5)
    - **Property 5: All icon images have descriptive alt text**
    - Use Hypothesis to generate `IconData` structures
    - Parse the rendered HTML and assert every `<img>` element for icon cards has a non-empty `alt` attribute containing the icon's Target name
    - **Validates: Requirements 10.2**

  - [x] 4.5 Create the example card partial `_example_card.html.j2`
    - Render each example with: title, description, rendered diagram image via PlantUML proxy URL, and a link to the source `.puml` file
    - Add `onerror` handler on the diagram `<img>` to show "Diagram unavailable" placeholder with link to source file
    - _Requirements: 7.2, 7.3, 7.5_

- [x] 5. Create CSS with CloudScape design tokens (`scripts/site_assets/style.css`)
  - [x] 5.1 Implement the stylesheet
    - Define CSS custom properties (`:root`) for CloudScape design tokens: colors, typography, spacing, border radii as specified in the design
    - Style the navigation bar, version selector, search bar, category filter area
    - Style the icon grid using CSS Grid or Flexbox for responsive layout (320px to 1920px)
    - Style icon cards with category color accents on section headers
    - Style the example gallery cards
    - Style copy button and confirmation feedback animation
    - Implement responsive breakpoints for mobile (320px), tablet (768px), desktop (1024px+)
    - Ensure WCAG 2.1 AA color contrast for all text elements
    - Add focus indicator styles for keyboard navigation
    - Add broken-image placeholder CSS fallback
    - _Requirements: 2.4, 8.1, 8.2, 8.3, 8.4, 8.5, 10.3_

- [x] 6. Create client-side JavaScript (`scripts/site_assets/app.js`)
  - [x] 6.1 Implement version switching logic
    - Implement `initVersionSelector()` to populate the dropdown from `window.SUPPORTED_VERSIONS` and set default to latest version
    - Implement `switchVersion(version)` to update all icon image `src` URLs and PUML include paths to the selected version
    - Implement `updateCategoryList(version)` to rebuild the category filter checkboxes when version changes
    - Preserve active search term and attempt to map active category filter through the category mapping table on version switch
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 4.6_

  - [x] 6.2 Implement category filtering logic
    - Implement `initCategoryFilter()` to render category checkboxes from `window.ICON_DATA`
    - Implement `filterByCategory(categories)` to show/hide category sections via DOM `display` toggling
    - When no categories selected, show all categories
    - Update visible icon count on filter change
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_

  - [x] 6.3 Implement search functionality
    - Implement `initSearch()` to attach input listener to the search bar
    - Implement `filterBySearch(query)` for case-insensitive matching against `data-target` and `data-target2` attributes
    - Implement `applyFilters()` to combine active category filter + search query for final visibility
    - Update visible icon count on search input
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6_

  - [x] 6.4 Implement clipboard copy and icon count display
    - Implement `copyToClipboard(text, button)` using `navigator.clipboard.writeText()` with fallback to `document.execCommand('copy')` via temporary textarea
    - Show brief visual confirmation on successful copy
    - If both methods fail, select the text for manual copying
    - Implement `updateIconCounts()` to display total and visible icon counts
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 2.5_

  - [x] 6.5 Implement cross-version category resolution
    - Implement `resolveCategoryMapping(category, fromVersion, toVersion)` that walks the `window.CATEGORY_MAPPING` table
    - Handle forward resolution (lower → higher version): apply renames sequentially, detect deletions
    - Handle reverse resolution (higher → lower version): reverse renames sequentially
    - Return renamed category name, `null` for deleted categories, or original name if unchanged
    - When a mapped category is deleted, clear the active filter and show all categories
    - _Requirements: 11.5, 11.6, 11.7, 11.8, 11.9_

  - [ ]* 6.6 Write property test for URL construction (Property 3)
    - **Property 3: Icon URL construction follows the canonical pattern**
    - Use fast-check to generate valid version strings, category names, and Target names
    - Assert PNG URL equals `https://raw.githubusercontent.com/awslabs/aws-icons-for-plantuml/{version}/dist/{category}/{target}.png`
    - Assert PUML URL equals `https://raw.githubusercontent.com/awslabs/aws-icons-for-plantuml/{version}/dist/{category}/{target}.puml`
    - Create a Node.js test file (e.g., `scripts/tests/test_app_properties.mjs`) that imports the pure functions from `app.js`
    - **Validates: Requirements 2.3, 6.1**

  - [ ]* 6.7 Write property test for combined filter (Property 4)
    - **Property 4: Combined search and category filter intersection**
    - Use fast-check to generate lists of icons, search queries, and sets of selected categories
    - Assert the filter returns exactly icons where: category is in selected set (or all selected) AND Target or Target2 contains the query as case-insensitive substring (or query is empty)
    - **Validates: Requirements 5.2, 5.3, 5.5**

  - [ ]* 6.8 Write property test for category resolution (Property 6)
    - **Property 6: Cross-version category resolution correctness**
    - Use fast-check to generate category names and version pairs from SUPPORTED_VERSIONS
    - Assert: renamed categories resolve to the new name, deleted categories return null, unchanged categories return the original name, and reverse resolution correctly inverts renames
    - **Validates: Requirements 11.5, 11.6, 11.7, 11.8, 11.9**

- [x] 7. Checkpoint
  - Ensure all tests pass, ask the user if questions arise.

- [x] 8. Create GitHub Actions workflow
  - [x] 8.1 Create `.github/workflows/deploy-pages.yml`
    - Define triggers: push to `main` branch and release creation
    - Set permissions: `contents: read`, `pages: write`, `id-token: write`
    - Set concurrency group `"pages"` with `cancel-in-progress: false`
    - Build job: checkout, setup-uv via `astral-sh/setup-uv@v6`, `uv sync`, `uv run scripts/generate_site.py`, upload pages artifact from `site/`
    - Deploy job: depends on build, uses `actions/deploy-pages@v4`, outputs the page URL
    - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5, 9.6_

- [x] 9. Integration testing and final wiring
  - [x] 9.1 Run full site generation and verify output
    - Execute `uv run scripts/generate_site.py` against the real `config.yml`
    - Verify `site/` directory contains `index.html`, `style.css`, `app.js`
    - Verify the generated HTML contains all expected category sections and icon cards
    - Verify embedded JSON data blocks are valid JSON and contain expected keys
    - Add `site/` to `.gitignore` if not already present
    - _Requirements: 1.2, 1.5, 2.1_

  - [ ]* 9.2 Write integration test for full site generation
    - Create a pytest test that runs `generate_site.py` end-to-end
    - Assert output directory structure is correct
    - Assert HTML contains expected category headings and icon card count matches config.yml
    - Assert CSS and JS files are copied to output
    - _Requirements: 1.2, 1.4, 1.5_

- [x] 10. Final checkpoint
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation
- Property tests validate universal correctness properties from the design document (Properties 1–6)
- Python tests use pytest + Hypothesis; JavaScript tests use fast-check in Node.js
- The site generator follows existing project conventions: runs via `uv run`, lives in `scripts/`, uses `sys.exit(1)` for errors
