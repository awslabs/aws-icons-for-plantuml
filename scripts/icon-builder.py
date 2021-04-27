#!/usr/bin/env python3
# Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT (For details, see https://github.com/awslabs/aws-icons-for-plantuml/blob/master/LICENSE)


"""icon-builder.py: Build AWS Icons for PlantUML"""

import os
import argparse
import sys
import subprocess
import shutil
import multiprocessing
import re
from multiprocessing import Pool
from pathlib import Path
from subprocess import PIPE
from collections import OrderedDict

import yaml

from awsicons.icon import Icon

TEMPLATE_DEFAULT = """
Defaults:
  Colors:
    SquidInk: "#232F3E"
  # Defaults for all categories
  Category:
    Color: SquidInk
  # Maximum in either height or width in pixels
  TargetMaxSize: 64
"""

MARKDOWN_PREFIX_TEMPLATE = """
<!--
Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT (For details, see https://github.com/awslabs/aws-icons-for-plantuml/blob/master/LICENSE)
-->
# AWS Symbols

The table below lists all AWS symbols in the `dist/` directory, sorted by category.

If you want to reference and use these files without Internet connectivity, you can also download the whole [*PlantUML Icons for AWS* dist](dist/) directory and reference it locally with PlantUML.

## PNG images

For each symbol, there is a resized icon in PNG format generated from the source file. Where the original icons had transparency set, this has been kept in the generated icons. You can also use the images outside of PlantUML, e.g. for documents or presentations, but the official [AWS Architecture Icons](https://aws.amazon.com/architecture/icons/) are available in all popular formats.

## All PNG generated AWS symbols

Category | PUML Macro (Name) | Image (PNG) | PUML Url
  ---    |  ---  | :---:  | ---
"""

PUML_COPYRIGHT = """'Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
'SPDX-License-Identifier: MIT (For details, see https://github.com/awslabs/aws-icons-for-plantuml/blob/master/LICENSE)

"""

parser = argparse.ArgumentParser(description="Generates AWS icons for PlantUML")
parser.add_argument(
    "--check-env",
    action="store_true",
    default=False,
    help="Verifies all dependencies met to process icons",
)
parser.add_argument(
    "--create-config-template",
    action="store_true",
    default=False,
    help=(
        "Creates a YAML config template based on official source for " "customization"
    ),
)
args = vars(parser.parse_args())
config = {}


def verify_environment():
    """Test all dependencies to verify that builder can run correctly"""
    global config

    # Check execution from scripts working directory
    cur_dir = Path(".")
    if str(cur_dir.absolute()).split("/")[-2:] != ["aws-icons-for-plantuml", "scripts"]:
        print(
            f"Working directory for icon-builder.py must be aws-icons-for-plantuml/scripts, not {cur_dir}"
        )
        sys.exit(1)
    # Read config file
    try:
        with open("config.yml") as f:
            config = yaml.safe_load(f)
    except Exception as e:
        print(f"Error: {e}\ncheck config.yml file")
        sys.exit(1)
    # Verify other files and folders exist
    dir = Path("../source")
    required_files = [
        "AWSC4Integration.puml",
        "AWSCommon.puml",
        "AWSRaw.puml",
        "AWSSimplified.puml",
    ]
    for file in required_files:
        q = dir / file
        if not q.exists():
            print(f"File {file} not found is source/ directory")
            sys.exit(1)
    q = dir / "official"
    if not q.exists() or len([x for x in q.iterdir() if q.is_dir()]) == 0:
        print(
            "source/official must contain folders of AWS  icons to process. Please see README file for details."
        )
        sys.exit(1)
    # Start plantuml.jar and verify java
    try:
        subprocess.run(
            ["java", "-jar", "./plantuml.jar", "-version"],
            shell=True,
            stdout=PIPE,
            stderr=PIPE,
        )
    except Exception as e:
        print(f"Error executing plantuml jar file, {e}")
        sys.exit(1)

    # Checks complete, return if not doing a pre-flight
    if args["check_env"]:
        # dry run only
        print("Prerequisites met, exiting")
        exit(0)
    return


def clean_dist():
    """Removes all files from the dist/ directory"""
    path = Path("../dist")
    if path.exists():
        shutil.rmtree(path)
    os.mkdir(path)


def copy_puml():
    """Copy source/*.puml files to dist"""
    for file in Path(".").glob("../source/*.puml"):
        shutil.copy(file, Path("../dist"))


def build_file_list():
    """Enumerate AWS Icons directory.

    Format for files since current Release 7.0-2020.09.11 Asset package:
       source/official/AWS-Architecture-Resource-Icons_*/CATEGORY/Res_48_Light/Res_SERVICE-RESOURCE_48_Light.svg
    and:
       source/official/AWS-Architecture-Service-Icons_*/CATEGORY48/Arch_SERVICE_48.svg

    Since the 7.0-2020.09.11 release, process from source SVG files, use the "48" directories for consistency

    where:

    CATEGORY = grouping of similar services or general icons
    SERVICE = Specific AWS named service (.e.g, Amazon Simple Queue Service)
    RESOURCE = Resource of product (e.g., "Queue" for Amazon SQS)

    Returns list of files
    """

    service_files = sorted(
        Path("../source/official").glob("AWS-Architecture-Service-Icons_*/**/*48/*.svg")
    )
    resource_files = sorted(
        Path("../source/official").glob(
            "AWS-Architecture-Resource-Icons_*/**/*48_Light/*.svg"
        )
    )

    return sorted(
        resource_files + service_files,
        key=lambda path: str(path).lower(),
    )


def create_config_template():
    """Create config_template.yml file from source icons"""
    source_files = build_file_list()
    files_sorted = sorted(str(i) for i in source_files)

    # Prep to compile categories and icon entries for each
    category_dict = {}
    dupe_check = []  # checking for duplicate names that need to be resolved

    for i in files_sorted:
        # Get elements needed for YAML file
        category = re.sub(r"\W+", "", i.split("/")[-3].split("_")[1])
        target = Icon()._make_name(i.split("/")[-1])
        source_name = i.split("/")[-1]
        # For source directory, use only relative from this script ./source/official/AWS...
        file_source_dir = "/".join(i.split("/", 3)[-1].split("/")[:-1])

        # Process each file and populate entries for creating YAML file
        # If new category, create new one
        try:
            if category not in category_dict:
                category_dict[category] = {"Icons": []}
        except KeyError:
            # Initial entry into dict
            category_dict = {category: {"Icons": []}}

        # Check for duplicate entries then append to
        if target not in dupe_check:
            category_dict[category]["Icons"].append(
                {
                    "Source": source_name,
                    "Target": target,
                    "SourceDir": file_source_dir,
                }
            )
            dupe_check.append(target)
        else:
            category_dict[category]["Icons"].append(
                {
                    "Source": source_name,
                    "Target": target,
                    "SourceDir": file_source_dir,
                    "ZComment": "******* Duplicate target name, must be made unique for All.puml ********",
                }
            )

    # With the completed dictionary of entries, convert to an OrderedDict and sort by Category -> Target
    # The sorted template file makes it easier to review changes between new icon releases
    sorted_categories = OrderedDict()
    for category in sorted(category_dict):
        sorted_categories[category] = {"Icons": []}
        sorted_categories[category]["Icons"] = sorted(
            category_dict[category]["Icons"], key=lambda i: i["Target"]
        )
    yaml_content = yaml.safe_load(TEMPLATE_DEFAULT)
    yaml_content["Categories"] = dict(sorted_categories)

    with open("config-template.yml", "w") as f:
        yaml.dump(yaml_content, f, default_flow_style=False)
    print("Successfully created config-template.yml")
    sys.exit(0)


def create_category_all_file(path):
    """Create an 'all.puml' file with contents of files in path"""
    data = ""
    for f in sorted(path.glob("*.puml")):
        with open(f, "r") as read_file:
            data += read_file.read() + "\n"
    # Filter out individual copyright statements and add single copyright to top of file
    content = ""
    for line in data.splitlines():
        if not line.startswith("'"):
            content += line + "\n"
    content = PUML_COPYRIGHT + content

    with open(f"{path}/all.puml", "w") as all_file:
        all_file.write(content)
    return


def worker(icon):
    """multiprocess resource intensive operations (java subprocess)"""
    # create images without transparency for use with PlantUML sprites
    icon.generate_image(
        Path(f"../dist/{icon.category}"),
        color=True,
        max_target_size=64,
        transparency=False,
    )
    print(f"generating PUML for {icon.source_name}")
    icon.generate_puml(Path(f"../dist/{icon.category}"))
    # Recreate the images with transparency
    icon.generate_image(
        Path(f"../dist/{icon.category}"),
        color=True,
        max_target_size=64,
        transparency=True,
    )
    return


def main():

    if args["create_config_template"]:
        create_config_template()

    verify_environment()

    # clear out dist/ directory
    clean_dist()

    # Copy source/*.puml files to dist/
    copy_puml()

    # Build and validate each entry as icon object
    source_files = build_file_list()
    icons = [Icon(filename, config) for filename in source_files]

    for icon in icons:
        if icon.category == "Uncategorized":
            print(icon.source_name)

    # Create category directories
    categories = sorted(set([icon.category for icon in icons]))
    for i in categories:
        Path(f"../dist/{i}").mkdir(exist_ok=True)

    # Create PlantUML sprites
    pool = Pool(processes=multiprocessing.cpu_count())
    for i in icons:
        pool.apply_async(worker, args=(i,))
    pool.close()
    pool.join()

    # Generate "all.puml" files for each category
    for i in categories:
        create_category_all_file(Path(f"../dist/{i}"))

    # Create markdown sheet and place in dist
    sorted_icons = sorted(icons, key=lambda x: (x.category, x.target))
    markdown = MARKDOWN_PREFIX_TEMPLATE
    for i in categories:
        category = i
        markdown += f"**{category}** | | | **{category}/all.puml**\n"
        for j in sorted_icons:
            if j.category == i:
                cat = j.category
                tgt = j.target
                markdown += (
                    f"{cat} | {tgt}  | ![{tgt}](dist/{cat}/{tgt}.png?raw=true) |"
                    f"{cat}/{tgt}.puml\n"
                )
    with open(Path("../AWSSymbols.md"), "w") as f:
        f.write(markdown)


if __name__ == "__main__":
    main()
