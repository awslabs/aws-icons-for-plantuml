<!--
Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT (For details, see https://github.com/awslabs/aws-icons-for-plantuml/blob/master/LICENSE)
-->
# Generating the PlantUML Icons for AWS

If you would like to have customized builds and/or experiment with *PlantUML Icons for AWS*, you can generate your own distribution of icons and PUML files for local use.

## Prerequisites

To generate the PlantUML files locally, ensure the following is prerequisites have been completed:

* Python 3.6/3.7 and packages from the `requirements.txt` file.
* [Amazon Corretto 8](https://docs.aws.amazon.com/corretto/latest/corretto-8-ug/downloads-list.html) or [OpenJDK 8](https://openjdk.java.net/install/) installed and available from the command line. Newer versions may also be used but have not been tested.
* Download the [AWS Architecture Icons - PNG format](https://d1.awsstatic.com/webteam/architecture-icons/AWS-Architecture-Icons_PNG_20190729.fc1bd3d844ff6ebd198d227d55e3b206fbcc62c2.zip), unzip,  and copy PNG file contents from `AWS-Architecture-Icons_PNG/Light-BG` directory to `source/official` directory.

  the folder structure should look like this:

    ```
    ├── aws-plantuml-icons
          └── source
              ├── AWScommon.puml
              └── official
                  ├── AR & VR
                  ├── AWS Cost Management
                  ├── Analytics
                ...
    ```

Verify all prerequisites are install by running `icon-builder.py --check-env` and correct any errors.


## Configure


### Configuration File: config.yml

The `config.yml` file is used to map specific file names to AWS categories, and set  the name and parameters set for each category or individual file when running the `icon-builder.py` script. The included configuration file is based on the 2019-02-07 release of the [AWS Architecture Icons](https://aws.amazon.com/architecture/icons/) release.

For general categories, the `Color` attribute is set to match as closely as possible the color represented for that category. For example, in the AR-VR category, the color for Amazon Sumerian is `#CC2264`, or approximately Maroon Flush. The color palettes used are in the `Defaults` section and then reference for the category, or can be overridden per-icon.

On top each AWS service is mapped to his primary category.

Next, install the python packages from the `requirements.txt` file. Depending upon your operating system, this may be through `apt`, `yum`, or `pip install` if using a virtual environment. The two requirements are:

- [PyYAML](https://pyyaml.org/)
- [Pillow](https://github.com/python-pillow/Pillow)

For PIP users, simply run `pip3 install -r requirements.txt` in your environment.

## Run

To verify all dependencies are met, run `iocn-builder.py` with the `--check-env` parameter, and if all is good, run the script without any flags..

```bash
$ ./icon-builder.py --check-env
Prerequisites met, exiting

```

### What happens

From a logical point of view, the following happens:

1. The `config.yml` is loaded
2. Cleanup: all files and directories from `dist` folder are deleted.
3. AWSCommon.puml is copied to `dist`.
4. All files ending in `_light-bg.png` are processed in the `source/official` directory:
    * Matching files will have a `Target` name and `Color` setting applied.
    * Non-matching files be set to Uncategorized with default `Target` and `Color` settings.
5. For each file, the source PNG will be resized, preserving transparency if set.
6. A PlantUML sprite is generated.
7. In addition to single AWS services PUML files, also a combined PUML file, nameds `all.puml`, is created for each category.

8. A markdown table with all AWS services,  image/icon, and the PUML name is generated.

## License Summary

The icons provided in this package are made available to you under the terms of the CC-BY-ND 2.0 license, available in the `LICENSE` file. Code is made available under the MIT license in `LICENSE-CODE`.

The compiled [Plant-UML jar](http://plantuml.com/download), `scripts/plantuml.jar`, is licensed under the MIT license in `LICENSE-CODE`.
