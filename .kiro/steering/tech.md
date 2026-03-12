# Tech Stack & Build System

## Language & Runtime
- Python 3.12+ (see `.python-version`)
- Package management via `uv` (not pip)
- Virtual environment: `.venv/` managed by `uv venv` and `uv sync`

## Dependencies (pyproject.toml)
- PyYAML: YAML config parsing
- lxml: SVG/XML processing
- Pillow: PNG image manipulation (cropping, borders)
- pytest: Testing

## External Tools
- Java 11+ (Corretto or OpenJDK): Required for PlantUML and Batik
- PlantUML MIT JAR (`scripts/plantuml-mit-1.2026.2.jar`): Sprite generation and rendering
- Apache Batik (`scripts/batik-1.16/`): SVG to PNG rasterization

## Linting
- Ruff (configured in `pyproject.toml`, with isort via `extend-select = ["I"]`)
- Pylint (`.pylintrc` disables C0301 line-length and W0212 protected-access)
- Bandit for security scanning

## Common Commands

All commands run from the `scripts/` directory:

```bash
# Install dependencies
uv venv
uv sync

# Verify build prerequisites (Java, source icons, config)
uv run icon-builder.py --check-env

# Full build: generate all dist/ icons, sprites, and PUML files
uv run icon-builder.py

# Regenerate only AWSSymbols.md, Structurizr theme, and Mermaid JSON
uv run icon-builder.py --symbols-only

# Create a fresh config-template.yml from source icons
uv run icon-builder.py --create-config-template

# Print AWS category color JSON for AWSCommon.puml
uv run icon-builder.py --create-color-json

# Run tests
uv run pytest test_upgrade.py

# Upgrade .puml files to latest icon version
uv run upgrade.py "*.puml"              # dry run
uv run upgrade.py --overwrite "*.puml"  # apply changes

# Local PlantUML render server
java -jar plantuml-mit-1.2026.2.jar -picoweb

# Local HTTP server for dist/ files
cd ../dist && python3 -m http.server 8000

# Local HTTP server with CORS (for Structurizr/Mermaid testing)
cd ../dist && python3 ../scripts/http_server_cors.py
```
