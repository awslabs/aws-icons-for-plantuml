<!--
Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT (For details, see https://github.com/awslabs/aws-icons-for-plantuml/blob/main/LICENSE)
-->

# Generating the PlantUML Icons for AWS

If you would like to have customized builds and/or experiment with _PlantUML Icons for AWS_, you can generate your own distribution of icons and PUML files for local use.

## Prerequisites

To generate the PlantUML files locally, ensure the following is prerequisites have been completed:

- Install Python 3 and packages from the `requirements.txt` file.
- [Amazon Corretto 11](https://docs.aws.amazon.com/corretto/latest/corretto-11-ug/downloads-list.html) or [OpenJDK 11](https://openjdk.java.net/install/) installed and available from the command line. Newer versions may also be used but have not been tested.
- Download the [Asset Package](https://aws.amazon.com/architecture/icons/) which contains both PNG and SVG file formats, unzip, and copy or move the `Architecture-Service-Icons_01-31-2021`, `Category-Icons_01-31-2021`, and `Resource-Icons_01-31-2021` directories to the `source/official` directory of this repository. The date may be different depending upon the version of the AWS Architecture Icons being downloaded.

  The folder structure should look like this once the directories have been copied over:

  ```
  aws-icons-for-plantuml/source
  ├── AWSC4Integration.puml
  ├── AWSCommon.puml
  ├── AWSRaw.puml
  ├── AWSSimplified.puml
  └── official
    ├── Architecture-Service-Icons_01-31-2021
    │   ├── Arch_AR-VR
    │   ├── Arch_AWS-Cost-Management
    │   ├── Arch_Analytics
        ...
    ├── Category-Icons_01-31-2021
    │   ├── Arch-Category_16
    │   ├── Arch-Category_32
    │   ├── Arch-Category_48
    │   └── Arch-Category_64
    └── Resource-Icons_01-31-2021
        ├── Res_Analytics
        ├── Res_Application-Integration
        ├── Res_Blockchain
        ...
  ```

## Configure to Build Icon Set

### Configuration File: config.yml

The included `config.yml` file is a curated file that maps specific file names to AWS categories and then sets the name and parameters for each category or individual file when running the `icon-builder.py` script. The included configuration file is specific for the release of the [AWS Architecture Icons](https://aws.amazon.com/architecture/icons/) and the referenced release tag.

If you are using the `config.yml` file as the basis to incorporate a newer version of the AWS Architecture Icons, you may see an _Uncategorized_ category of mismatched entries.

For general categories, the `Color` attribute is set to match as closely as possible the color represented for that category. For example, in the AR-VR category, the color for Amazon Sumerian is `#CC2264`, or approximately Maroon Flush. The color palettes used are in the `Defaults` section and then reference for the category, or can be overridden per-icon.

In the curated `config.yml` file, each AWS service is mapped to it's primary category. This then maps to the specific PUML file referenced by _Category/Filename.puml_, or are included in the _Category/all.puml_ file.

Next, install the python packages from the `requirements.txt` file. Depending upon your operating system, this may be through `apt`, `yum`, or `pip install` if using a virtual environment. The two requirements are:

- [PyYAML](https://pyyaml.org/)

For PIP users, simply run `pip3 install -r requirements.txt` in your environment.

## Verify Dependencies and Process

To verify all dependencies are met, run `icon-builder.py` with the `--check-env` parameter, and if all is good, run the script without any flags..

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
$ ./icon-builder.py
../source/AWSCommon.puml
Successfully created config-template.yml
```

Next, run the same command without `--check-env` to create all new icons and update the `config.yml` file.

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
1. In addition to single AWS services PUML files, a combined PUML file, named `all.puml`, is created for each category.
1. A markdown table with all AWS services, image/icon, and the PUML name is generated.

## Build Notes

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

The compiled [Plant-UML jar](http://plantuml.com/download), `scripts/plantuml.jar`, is licensed under the MIT license in `LICENSE-CODE`.
