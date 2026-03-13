# Project Structure

```
aws-icons-for-plantuml/
├── dist/                          # Generated output (committed to repo)
│   ├── AWSCommon.puml             # Base styles, colors, macros (copied from source/)
│   ├── AWSSimplified.puml         # Simplified view overrides
│   ├── AWSExperimental.puml       # Callout sprites, icon notes
│   ├── AWSRaw.puml                # Raw sprite usage support
│   ├── AWSC4Integration.puml      # C4 model integration
│   ├── aws-icons-mermaid.json     # Experimental Mermaid icon set
│   ├── aws-icons-structurizr-theme.json  # Experimental Structurizr theme
│   └── <Category>/               # One folder per AWS service category
│       ├── all.puml              # Combined includes for the category
│       ├── <Service>.puml        # Individual service PUML (sprite + macros + base64 PNG)
│       └── <Service>.png         # Individual service icon (64x64 or 48x48)
├── source/                        # Source PUML templates and official AWS icons (not in tree)
│   ├── *.puml                     # Template PUML files copied to dist/
│   └── official/                  # Unzipped AWS Architecture Icons asset package
├── scripts/                       # Build tooling (run from this directory)
│   ├── icon-builder.py            # Main build script
│   ├── awsicons/icon.py           # Icon class: SVG→PNG, sprite generation, PUML creation
│   ├── config.yml                 # Curated mapping of source icons → categories/targets/colors
│   ├── upgrade.py                 # Upgrades .puml files between release versions
│   ├── test_upgrade.py            # Tests for upgrade.py
│   ├── plantuml-mit-1.2026.2.jar  # PlantUML MIT-licensed JAR
│   └── batik-1.16/                # Apache Batik SVG rasterizer
├── examples/                      # Example .puml diagrams
├── AWSSymbols.md                  # Generated markdown table of all icons
├── pyproject.toml                 # Python project config (deps, ruff, bandit)
└── README.md                      # User-facing documentation
```

## Key Conventions

- `dist/` is fully generated — never hand-edit files there. The build deletes and recreates it.
- `config.yml` is the curated mapping file. Each icon entry has `Source`, `SourceDir`, `Target` (PascalCase PUML name), and `Target2` (kebab-case Mermaid name).
- Categories map to AWS color palette names (Galaxy, Cosmos, Smile, etc.) defined in `Defaults.Colors`.
- Groups (VPC, subnets, etc.) use `.touch` files as placeholders for iconless group PUML generation.
- `icon-builder.py` must be run from the `scripts/` directory.
- The `source/official/` directory is not committed — users download the AWS Architecture Icons asset package and extract it there.
- Dark mode icons use `_Dark` suffix variants (e.g., `AWS-Cloud_Dark.png`).
