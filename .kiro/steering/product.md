# Product Overview

AWS Icons for PlantUML is an open-source project that provides PlantUML images, sprites, macros, and includes for Amazon Web Services (AWS) services and resources. It generates a `dist/` directory of `.puml` and `.png` files from the official AWS Architecture Icons asset package.

The project enables developers and architects to create PlantUML diagrams using AWS service icons, supporting component diagrams, sequence diagrams, C4 model diagrams, and experimental dark mode, Structurizr, and Mermaid output.

Users reference the generated files via `!include` statements pointing to GitHub release URLs or local paths. Each AWS service gets a PUML macro (e.g., `Lambda(alias, "Label", "tech")`) and a corresponding PNG icon.

The project is versioned to align with AWS Architecture Icons releases (e.g., v22.0-2025.07.31). The `dist/` directory is the published artifact; the `scripts/` directory contains the build tooling.
