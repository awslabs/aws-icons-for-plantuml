<!--
Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT (For details, see https://github.com/awslabs/aws-icons-for-plantuml/blob/main/LICENSE)
-->

<!-- markdownlint-disable MD014 -->

# Generating the PlantUML Icons for AWS

If you would like to have customized builds and/or experiment with _PlantUML Icons for AWS_, you can generate your own distribution of icons and PUML files for local use.

## Prerequisites

To generate the PlantUML files locally, ensure the following is prerequisites have been completed:

- Install Python 3 and packages from the `requirements.txt` file.
- [Amazon Corretto 11](https://docs.aws.amazon.com/corretto/latest/corretto-11-ug/downloads-list.html) or [OpenJDK 11](https://openjdk.java.net/install/) installed and available from the command line. Newer versions may also be used but have not been tested.
- Download the [Asset Package](https://aws.amazon.com/architecture/icons/) which contains both PNG and SVG file formats, unzip, and copy or move the `Architecture-Service-Icons_06072024`, `Category-Icons_06072024`, and `Resource-Icons_06072024` directories to the `source/official` directory of this repository. The date may be different depending upon the version of the AWS Architecture Icons being downloaded.

  The folder structure should look like this once the directories have been copied over:

  ```text
  aws-icons-for-plantuml/source
  ├── AWSC4Integration.puml
  ├── AWSCommon.puml
  ├── AWSExperimental.puml
  ├── AWSRaw.puml
  ├── AWSSimplified.puml
  └── official
    ├── Architecture-Service-Icons_06072024
    │   ├── Arch_Analytics
    │   ├── Arch_App-Integration
    │   ├── Arch_Blockchain
        ...
    ├── Category-Icons_06072024
    │   ├── Arch-Category_16
    │   ├── Arch-Category_32
    │   ├── Arch-Category_48
    │   └── Arch-Category_64
    └── Resource-Icons_06072024
        ├── Res_Analytics
        ├── Res_Application-Integration
        ├── Res_Blockchain
        ...
  ```

- There is now a `Architecture-Group-Icons_06072024`, but the group icons (in the `source/unofficial/Groups_04282023` directory) were extracted from the Microsoft PowerPoint found on the [AWS Architecture Icons](https://aws.amazon.com/architecture/icons/).  If you see a change looking at the `.pptx` file, `unzip` it from the command line and look in the `ppt/media` for the images.  These are named `image#.svg` and `image#.png` where `#` and since group icons are early in the deck, they are usually in the first 100 images.  Copy and rename the `.svg` file, and copy, rename, and resize (to 64x64) the `.png` file.

## Configure to Build Icon Set

### Configuration File: config.yml

The included `config.yml` file is a curated file that maps specific file names to AWS categories and then sets the name and parameters for each category or individual file when running the `icon-builder.py` script. The included configuration file is specific for the release of the [AWS Architecture Icons](https://aws.amazon.com/architecture/icons/) and the referenced release tag.

If you are using the `config.yml` file as the basis to incorporate a newer version of the AWS Architecture Icons, you may see an _Uncategorized_ category of mismatched entries.

For general categories, the `Color` attribute is set to match the color represented for that category. For example, in the NetworkingContentDelivery category, the color for Amazon API Gateway is `#8C4FFF`, or Galaxy. The color palettes used are in the `Defaults` section and then reference for the category, or can be overridden per-sprite.

In the curated `config.yml` file, each AWS service is mapped to it's primary category. This then maps to the specific PUML file referenced by _Category/Filename.puml_, or are included in the _Category/all.puml_ file.

Next, install the python packages from the `requirements.txt` file. Depending upon your operating system, this may be through `apt`, `yum`, or `pip install` if using a virtual environment. The requirements are:

- [PyYAML](https://pyyaml.org/)
- [lxml](https://lxml.de/)
- [Pillow](https://python-pillow.org/)
- [pytest](https://docs.pytest.org/en/stable/)

For PIP users, simply run `pip3 install -r requirements.txt` in your environment.

## Verify Dependencies and Process

To verify all dependencies are met, run `icon-builder.py` with the `--check-env` parameter, and if all is good, run the script without any flags.

```bash
$ ./icon-builder.py --check-env
Prerequisites met, exiting
```

### _Optional_ Create New `config.yml`

If you would like to start from scratch, rename the existing `config.yml` file and run the `icon-builder.py` script to build the `config-template.yml` file with only the default color and size set. Then rename to `config.yml`. You can use the renamed original file to get colors and configuration settings if desired.

```bash
$ ./icon-builder.py --create-config-template
../source/AWSCommon.puml
Successfully created config-template.yml
$ mv config-template.yml config.yml
```

To process all the files, run the command with no parameters. NOTE: This will take at least a few minutes to complete, and the script with launch multiple Java processes to generate the icons.

```bash
$ ./icon-builder.py --check-env
Prerequisites met, exiting
```

Next, run the same command without `--check-env` to create all new icons and update the `config.yml` file.

### Other commands

After icons have been created, you can just regenerate the `AWSSymbols.md`, Structurizr theme, and Mermaid icons files by running the command with the `--symbols-only` parameter.

```bash
$ ./icon-builder.py --symbols-only
```

The `$AWSColor($service)` relies on a JSON mapping of category to color (`$AWS_CATEGORY_COLORS` in `AWSCommon.puml`).  When a new category is added (or colors change), you can generate this JSON structure by running the command with the `--create-color-json` parameter.  You will then need to copy this and replace the version in `AWSCommon.puml`.

```bash
$ ./icon-builder.py --create-color-json
```

### What Happens

From a logical point of view, the following happens:

1. The `config.yml` is loaded
1. Cleanup: all files and directories from `dist` folder are deleted.
1. AWSCommon.puml and supporting PUML files are copied to `dist`.
1. In the `dir_list` variable in `icon-builder.py`, the directories are processed from the `source/official` directory:
   - Matching files will have a `Target` name, `Category`, and `Color` setting applied.
   - Non-matching files be set to Uncategorized with default `Target` and `Color` settings.
1. For each file, the source SVG will be used to generate the `TargetMaxSize` in pixels as a .png, preserving transparency if set.
1. A PlantUML sprite is generated.
1. A `<img>` tag with a data URL (data:image/png;base64) is generated.
1. In addition to single AWS services PUML files, a combined PUML file, named `all.puml`, is created for each category.
1. A markdown table with all AWS services, image/icon, and the PUML name is generated.

### Local Testing

You can used the included PlantUML .jar to run a local server for rendering or download the latest [plantuml release](https://github.com/plantuml/plantuml/releases) from GitHub.  This project uses the MIT licensed distribution.

To check the version and license of PlantUML, create a diagram with the following syntax:

```
@startuml
version
@enduml
```

Or execute the jar with the `-version` parameter:

```bash
$ java -jar scripts/plantuml-mit-1.2024.6.jar -version
PlantUML version 1.2024.6 (Sat Jul 06 04:14:38 CDT 2024)
(MIT source distribution)
```

To start the local render server.  You may need `-DPLANTUML_SECURITY_PROFILE=ALLOWLIST -Dplantuml.allowlist.url="http://localhost:8000/;https://raw.githubusercontent.com/awslabs/aws-icons-for-plantuml/"`, but consult [Deploy PlantUML safely](https://plantuml.com/security):

```bash
java -jar scripts/plantuml-mit-1.2024.6.jar -picoweb
```

If you use Visual Studio Code and the jebbs [PlantUML](https://marketplace.visualstudio.com/items?itemName=jebbs.plantuml) extension, update your `.vscode\settings.json` as below to use that local server.

```json
  "plantuml.render": "PlantUMLServer",
  "plantuml.server": "http://localhost:8080/plantuml/",
```

 To `!include` the local `.puml` files via URL: `cd dist` and `python3 -m http.server 8000` to run a local web server. Then, in your `.puml` file, redefine `AWSPuml` to use localhost.  Alternatively, you can `cd dist` and `python3 ../scripts/http_server_cors.py` for a server with CORS support (needed to test Structurizr theme or Mermaid icons).

```
!define AWSPuml http://localhost:8000
```

If you use Visual Studio Code, `.vscode\tasks.json` has tasks defined for running "PlantUML picoweb 8080" (using `ALLOWLIST`), "http.server 8000", and "http.server CORS 8000".

## Build Notes

### Release 19.0-2024.06.07

This release switched to using `plantuml-mit-1.2024.6.jar` which had no noticeable changes.  Experimental `upgrade.py` that will replace renamed categories and icons in .puml files based on release notes **Breaking Changes** since Release 13.0.  Default is read-only mode (`python upgrade.py file.puml`) but supports `--overwrite` and filename wildcards (`python upgrade.py --overwrite "*.puml"`).  This upgrade script was used to update `examples` directory from `v18.0` to `v19.0` and tested via `pytest test_upgrade.py`.

Experimental [Mermaid](https://mermaid.js.org/) support via [iconifyJSON](https://iconify.design/docs/types/iconify-json.html) formatted `aws-icons-mermaid.json` and example added to "s3-upload-workflow" folder.  These icon filenames are required to be lower kebob case, so a `Target2` field was added to `config.yml`

### Release 18.0-2024.02.06

This release switched to using `plantuml-mit-1.2024.3.jar` which had no noticeable changes.

### Release 17.0-2023.10.23

This release switched to using `plantuml-mit-1.2023.12.jar` which had no noticeable changes.

### Release 16.0-2023.04.28

This is major release due to all icons changing to a new color palette supporting both light and dark backgrounds.  Since service icons no longer have gradients, optimized build to just copy the existing `*_48.png` (64x64) files instead of re-rendering from the `.svg`.  For category `.png` files which were expanded to 74x74 and included a gray border, used the Pillow library to crop out the center and then add the border back.  Added new command line arguments (`--symbols-only` and `--create-color-json`).  Added about 10 more `filename_mappings` to avoid breaking changes for low value name changes. This release switched to using `plantuml-mit-1.2023.7.jar` which had no noticeable changes.

Experimental "dark mode" support. Support for `$AWS_DARK` was embedded into `AWSCommon.md` (vs. using PlantUML [themes format](https://github.com/plantuml/plantuml/blob/master/themes/)) to support swapping Light/Dark images and match contrast/accessibility guidelines. Markdown images references in `AWSSymbols.md` are generated using [GitHub image theme](https://github.blog/changelog/2021-11-24-specify-theme-context-for-images-in-markdown/) values of `#gh-dark-mode-only` or `#gh-light-mode-only`.

Experimental [Structurizr](https://structurizr.com/) support via `aws-icons-structurizr-theme.json` and example added to "s3-upload-workflow" folder.

### Release 15.0-2023.01.31

This release switched to using `plantuml-mit-1.2023.1.jar` and `batik-rasterizer-1.16.jar` which had no noticeable changes.  Documented color definitions in generated `AWSSymbols.md`.

### Release 14.0-2022.07.31

This release switched to using `plantuml-mit-1.2022.7.jar` which had no noticeable changes.

### Release 13.1-2022.04.30

This release added Groups support via a custom styled `rectangle` using the corresponding AWS Icon and a default label.  Since `icon-builder.py` is file driven, and groups like Availability Zone or Security Group do not have associated icon files, a convention using a zero-length file with the `.touch` extension was implemented.  The generation logic uses this file to trigger `.puml` creation, but will not generate a Sprite / PNG image or have an image reference in the AWS Symbols table. Groups deprecates the GroupIcons category whose macros no longer appear in AWS Symbols table, but the .puml files are still generated for backward compatibility.

### Release 13.0-2022.04.30

This release switched to using `plantuml-mit-1.2022.5.jar` which had changes to default styling and slightly different sprite generation.  Because PlantUML native sprites are grayscale and have color is applied to them, the default is now to use PNG files for icons. The included `.png` icon files were added to the `.puml` files via a `!function` (e.g. `$APIGatewayIMG($scale="1")` which returns a creole `<img>` tag with a data URL (data:image/png;base64).  The definitions of `AWSEntity` and `AWSParticipant` were updated to use these images instead of the colorized sprites.

### Release 9.0-2021.1.31

This is major release for a couple of reasons. First the 8.0 release was bypassed due to a significant change in directory structure and upcoming re:Invent focus. This required major changes to the build process that previously had embedded parsing of files. Also, the continued changes on `.png` files sizes and the `@2x`, `@4x`, and `@5x` sizes lead to researching a license compatible SVG conversion library, [Apache Batik](https://xmlgraphics.apache.org/batik/).

The end result should be a cleaner method to determine directory structure changes and add additional attributes to icons in the future. Hopefully. As this release is one day before the expected April 30th, 2021, release of the icon set, we'll be able to test quickly.

Due a lot of new icons, moved icons, and in some cases deprecated ones, the previous curation approach is being changed. We found that the naming of the PUML files to be shorter, such as `SimpleNotificationService` to `SNS`, was not as impactful as first thought. Once included once into a PlantUML diagram, most people aliased these icons. If you feel strongly about this, you can use the 7.0 release. But also let us know in the Issues section!

Here are the significant changes to this release:

- Minimal curation of icon or category names, with the exception that the `GeneralIcons` category has been mapped to `General` as in previous releases.
- Apache Batik is now use to general all icons from the source SVG. Resource icons which are transparent by default have a white background set to increase the fidelity of the PlantUML sprites.
- The builder script and supporting class have been changed to extract the parsing logic from different points in the code and placed in a global variable. This will move to a configuration file and command line argument in later releases.
- Category names with _and_ (or & such as _Management and Governance_ -> `ManagementAndGovernance` in the older releases) have been renamed without them (e.g, `ManagementGovernance`). The `InternetOfThings` category case (`Of`) has been kept instead of the default`InternetofThings`.
- The `GroupIcons` have been removed from the source assets. If there is demand to have these restored, we can look and creating a local set of persistent source files.
- The `icon-builder.py` process now uses `-Djava.awt.headless=true` when creating the PUML and PNG files. It will no longer will have the subprocesses take mouse focus.

### Release 7.0-2020.04.30

This is a makeover release where all items have moved. Of note:

- Separate directories for Service icons and Service resource icons
- Resource icons only have 48x48 pixel icons (Res_48), while Service icons have 16, 32, 48, and 64 sizes. To accommodate 64x64 icons, Apache Batik is used to generate the icons directly from the SVG format files.

## License Summary

The icons provided in this package are made available to you under the terms of the CC-BY-ND 2.0 license, available in the `LICENSE` file. Code is made available under the MIT license in `LICENSE-CODE`.

The compiled [Plant-UML jar](http://plantuml.com/download), `scripts/plantuml-mit-1.2022.5.jar`, is licensed under the MIT license in `LICENSE-CODE`.
