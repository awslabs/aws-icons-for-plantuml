#!/usr/bin/env python3
# Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT (For details, see https://github.com/awslabs/aws-icons-for-plantuml/blob/main/LICENSE)


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

# TODO - refactor to param file and/or arguments

# This list are the directories to parse, what type of files they are, and globbing/regex
# to parse and process. This addresses the changing nature of the assets package.


# Source directories for the 14.0-2022.07.31 release
dir_list = [
    {
        "dir": "../source/official",
        # dir structure changed from Category-Icons_04-30-2021/Arch-Category_64/filename
        # to: Category-Icons_04-30-2021/64/filename
        "dir_glob": "Category-Icons_01312023/*64/*.svg",
        "category_regex": "[^.]*\/Arch-Category_(.*)_\d*\.svg$",
        "filename_regex": "[^.]*\/Arch-Category_(.*)_\d*\.svg$",
        "category_mappings": {
            "BusinessApplication": "BusinessApplications",
            # "CostManagement": "AWSCostManagement",
            "DevTools": "DeveloperTools",
            "GeneralIcons": "General",
            "InternetofThings": "InternetOfThings",
        },
        "filename_mappings": {
            "BusinessApplication": "BusinessApplications",
            "CostManagement": "AWSCostManagement",
            "DevTools": "DeveloperTools",
            "InternetofThings": "InternetOfThings",
        },
    },
    {
        "dir": "../source/official",
        "dir_glob": "Architecture-Service-Icons_01312023/**/*64/*.svg",
        "category_regex": "[^.]*\/(?:Arch_)(.*)\/(?:.*)\/(?:.*$)",
        "filename_regex": "[^.]*Arch_(?:Amazon.|AWS.)?(.*)_\d*\.svg$",
        "category_mappings": {
            "AppIntegration": "ApplicationIntegration",
            "BusinessApplication": "BusinessApplications",
            "CustomerEnagagement": "CustomerEngagement",
            "GeneralIcons": "General",
            "InternetofThings": "InternetOfThings",
            "NetworkingContent": "NetworkingContentDelivery",
        },
        "filename_mappings": {
            "S3onOutpostsStorage": "S3OnOutpostsStorage",
        },
    },
    {
        "dir": "../source/official",
        "dir_glob": "Resource-Icons_01312023/**/*48_Light/*.svg",
        "category_regex": "[^.]*\/(?:Res_)(.*)\/(?:.*)\/(?:.*$)",
        "filename_regex": "[^.]*Res_(?:Amazon.|AWS.)?(.*)_\d*_Light\.svg$",
        "category_mappings": {
            "GeneralIcons": "General",
            "InternetofThings": "InternetOfThings",
            "loT": "InternetOfThings",
            "MigrationandTransfer": "MigrationTransfer",
            "NetworkingandContentDelivery": "NetworkingContentDelivery",
            "SecurityIdentityandCompliance": "SecurityIdentityCompliance",
        },
        "filename_mappings": {},
    },
    {
        "dir": "../source/unofficial",
        "dir_glob": "AWS-Architecture-Icons_SVG_20200430/SVG Light/_Group Icons/*.svg",
        "category_regex": "[^.]*\/_(.*)\/",
        "filename_regex": "[^.]*\/(.*)_light-bg\.svg",
        "category_mappings": {},
        "filename_mappings": {
            "AWSCloud": "Cloud",
            "AWSCloudalt": "Cloudalt",
            "AWSStepFunction": "StepFunction",
            "AutoScaling": "AutoScalingGroup",
            "Corporatedatacenter": "CorporateDataCenter",
            "EC2instancecontainer": "EC2InstanceContainer",
            "ElasticBeanstalkcontainer": "ElasticBeanstalkContainer",
            "Servercontents": "ServerContents",
            "Spotfleet": "SpotFleet",
            "VPCsubnetprivate": "VPCSubnetPrivate",
            "VPCsubnetpublic": "VPCSubnetPublic",
            "VirtualprivatecloudVPC": "VirtualPrivateCloudVPC",
        },
    },
    {
        "dir": "../source/unofficial",
        "dir_glob": "Groups_04302022/*.*",
        "category_regex": "[^.]*\/(Groups).*\/",
        "filename_regex": "[^.]*\/(.*)\.(?:svg|touch)",
        "category_mappings": {},
        "filename_mappings": {},
    },
]

CATEGORY_COLORS = {
    "Analytics": "PurpleHeart",
    "ApplicationIntegration": "MaroonFlush",
    "Blockchain": "Meteor",
    "BusinessApplications": "Crimson",
    "CloudFinancialManagement": "ForestGreen",
    "Compute": "Meteor",
    "Containers": "Meteor",
    "CustomerEnablement": "CeruleanBlue",
    "Database": "CeruleanBlue",
    "DeveloperTools": "CeruleanBlue",
    "EndUserComputing": "Elm",
    "FrontEndWebMobile": "Crimson",
    "Games": "PurpleHeart",
    "General": "SquidInk",
    "InternetOfThings": "ForestGreen",
    "MachineLearning": "Elm",
    "ManagementGovernance": "MaroonFlush",
    "MediaServices": "Meteor",
    "MigrationTransfer": "Elm",
    "NetworkingContentDelivery": "PurpleHeart",
    "QuantumTechnologies": "Meteor",
    "Robotics": "Crimson",
    "Satellite": "CeruleanBlue",
    "SecurityIdentityCompliance": "Crimson",
    "Serverless": "PurpleHeart",
    "Storage": "ForestGreen",
    "VRAR": "MaroonFlush",
}

GROUPICONS_COLORS = {
    "AutoScalingGroup": "Meteor",
    "Cloud": "SquidInk",
    "Cloudalt": "SquidInk",
    "CorporateDataCenter": "SquidInk",
    "EC2InstanceContainer": "Meteor",
    "ElasticBeanstalkContainer": "Meteor",
    "Region": "CeruleanBlue",
    "ServerContents": "SquidInk",
    "SpotFleet": "Meteor",
    "StepFunction": "MaroonFlush",
    "VPCSubnetPrivate": "CeruleanBlue",
    "VPCSubnetPublic": "ForestGreen",
    "VirtualPrivateCloudVPC": "ForestGreen",
}

COLOR_MACROS = {
    "CeruleanBlue": "AWS_COLOR_BLUE",
    "Crimson": "AWS_COLOR_RED",
    "Elm": "AWS_COLOR_TURQUOISE",
    "ForestGreen": "AWS_COLOR_GREEN",
    "MaroonFlush": "AWS_COLOR_PINK",
    "Meteor": "AWS_COLOR_ORANGE",
    "PurpleHeart": "AWS_COLOR_PURPLE",
    "SquidInk": "AWS_COLOR",
    "White": "AWS_BG_COLOR",
}

TEMPLATE_DEFAULT = """
# Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT (For details, see https://github.com/awslabs/aws-icons-for-plantuml/blob/main/LICENSE)
#
# Curated config file for Release 15.0-2023.01.31 AWS Architecture Icons release (https://aws.amazon.com/architecture/icons/)
# cSpell: disable
Defaults:
  Colors:
    CeruleanBlue: "#3B48CC"
    Crimson: "#D6242D"
    Elm: "#1C7B68"
    ForestGreen: "#3F8624"
    MaroonFlush: "#CC2264"
    Meteor: "#D86613"
    PurpleHeart: "#693CC5"
    SquidInk: "#232F3E"
    White: "#FFFFFF"
  # Defaults for services not found
  Category:
    Color: SquidInk
  Group:
    BorderStyle: plain
    BackgroundColor: "#FFFFFF"
    Label: "Generic group"
  # Maximum in either height or width in pixels
  TargetMaxSize: 64
"""

# \\\\n in Python needed to generate \\n in YAML for \n in output .puml
CATEGORY_GROUPS = """
  Groups:
    Icons:
    - Color: "#5B9CD5"
      Group:
        BorderStyle: dashed
      Label: "\\\\n  Availability Zone"
      Source: Availability-Zone.touch
      SourceDir: Groups_04302020
      Target: AvailabilityZone
    - Color: "#CD2264"
      Label: "AWS account"
      Source: AWS-Account.svg
      SourceDir: Groups_04302020
      Target: AWSAccount
    - Color: "#000000"
      Label: "AWS Cloud"
      Source: AWS-Cloud-alt.svg
      SourceDir: Groups_04302020
      Target: AWSCloudAlt
    - Color: "#000000"
      Label: "AWS Cloud"
      Source: AWS-Cloud.svg
      SourceDir: Groups_04302020
      Target: AWSCloud
    - Color: "#3F8624"
      Label: "AWS IoT Greengrass Deployment"
      Source: AWS-IoT-Greengrass-Deployment.svg
      SourceDir: Groups_04302020
      Target: IoTGreengrassDeployment
    - Color: "#3F8624"
      Label: "AWS IoT Greengrass"
      Source: AWS-IoT-Greengrass.svg
      SourceDir: Groups_04302020
      Target: IoTGreengrass
    - Color: "#CD2264"
      Label: "AWS Step Functions workflow"
      Source: AWS-Step-Functions-workflow.svg
      SourceDir: Groups_04302020
      Target: StepFunctionsWorkflow
    - Color: "#D86613"
      Group:
        BorderStyle: dashed
      Label: "\\\\nAuto Scaling group"
      Source: Auto-Scaling-group.svg
      SourceDir: Groups_04302020
      Target: AutoScalingGroup
    - Color: "#5A6B86"
      Label: "Corporate data center"
      Source: Corporate-data-center.svg
      SourceDir: Groups_04302020
      Target: CorporateDataCenter
    - Color: "#D86613"
      Label: "EC2 instance contents"
      Source: EC2-instance-contents.svg
      SourceDir: Groups_04302020
      Target: EC2InstanceContents
    - Color: "#D86613"
      Label: "Elastic Beanstalk container"
      Source: Elastic-Beanstalk-container.svg
      SourceDir: Groups_04302020
      Target: ElasticBeanstalkContainer
    - Color: "#5A6B86"
      Group:
        BorderStyle: dashed
      Label: "\\\\n  Generic group"
      Source: Generic-group.touch
      SourceDir: Groups_04302020
      Target: Generic
    - Color: "#000000"
      Group:
        BackgroundColor: "#EFF0F3"
        BorderColor: "#Transparent"
      Label: "\\\\n  Generic group"
      Source: Generic-group-alt.touch
      SourceDir: Groups_04302020
      Target: GenericAlt
    - Color: "#3A47CB"
      Label: "Generic Blue group"
      Source: Placeholder_Blue.svg
      SourceDir: Groups_04302020
      Target: GenericBlue
    - Color: "#3F8624"
      Label: "Generic Green group"
      Source: Placeholder_Green.svg
      SourceDir: Groups_04302020
      Target: GenericGreen
    - Color: "#D86613"
      Label: "Generic Orange group"
      Source: Placeholder_Orange.svg
      SourceDir: Groups_04302020
      Target: GenericOrange
    - Color: "#CD2264"
      Label: "Generic Pink group"
      Source: Placeholder_Pink.svg
      SourceDir: Groups_04302020
      Target: GenericPink
    - Color: "#693BC5"
      Label: "Generic Purple group"
      Source: Placeholder_Purple.svg
      SourceDir: Groups_04302020
      Target: GenericPurple
    - Color: "#D6232C"
      Label: "Generic Red group"
      Source: Placeholder_Red.svg
      SourceDir: Groups_04302020
      Target: GenericRed
    - Color: "#1B7B67"
      Label: "Generic Turquoise group"
      Source: Placeholder_Turquoise.svg
      SourceDir: Groups_04302020
      Target: GenericTurquoise
    - Color: "#5B9CD5"
      Group:
        BackgroundColor: "#E6F2F8"
        BorderColor: "#Transparent"
      Label: "Private subnet"
      Source: Private-subnet.svg
      SourceDir: Groups_04302020
      Target: PrivateSubnet
    - Color: "#1E8900"
      Group:
        BackgroundColor: "#E9F3E6"
        BorderColor: "#Transparent"
      Label: "Public subnet"
      Source: Public-subnet.svg
      SourceDir: Groups_04302020
      Target: PublicSubnet
    - Color: "#5B9CD5"
      Group:
        BorderStyle: dotted
      Label: "Region"
      Source: Region.svg
      SourceDir: Groups_04302020
      Target: Region
    - Color: "#DF3312"
      Label: "\\\\n  Security group"
      Source: Security-group.touch
      SourceDir: Groups_04302020
      Target: SecurityGroup
    - Color: "#5A6B86"
      Label: "Server contents"
      Source: Server-contents.svg
      SourceDir: Groups_04302020
      Target: ServerContents
    - Color: "#D86613"
      Label: "Spot Fleet"
      Source: Spot-Fleet.svg
      SourceDir: Groups_04302020
      Target: SpotFleet
    - Color: "#693BC5"
      Label: "Virtual private cloud (VPC)"
      Source: Virtual-Private-Network-VPC.svg
      SourceDir: Groups_04302020
      Target: VPC
"""

MARKDOWN_PREFIX_TEMPLATE = """
<!--
Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT (For details, see https://github.com/awslabs/aws-icons-for-plantuml/blob/main/LICENSE)
-->
# AWS Symbols

The table below lists all AWS symbols in the `dist/` directory, sorted by category.

If you want to reference and use these files without Internet connectivity, you can also download the whole [*PlantUML Icons for AWS* dist](dist/) directory and reference it locally with PlantUML.

## Colors

These colors are defined in `AWSCommon.puml`

PUML Macro (Name) | Color | Categories
  ---  |  ---  | ---
AWS_COLOR | #232F3E |
AWS_BG_COLOR | #FFFFFF |
AWS_BORDER_COLOR | #FF9900 |
AWS_COLOR_BLUE | #3A47CB | Customer Enablement; Database; Developer Tools; Satellite
AWS_COLOR_GREEN | #3F8624 | Cloud Financial Management; Internet of Things; Storage
AWS_COLOR_ORANGE | #D86613 | Blockchain; Compute; Containers; Media Services; Quantum Technologies
AWS_COLOR_PINK | #CD2264 | Application Integration; Management & Governance; VR & AR
AWS_COLOR_PURPLE | #693BC5 | Analytics; Games; Networking & Content Delivery; Serverless
AWS_COLOR_RED | #D6232C | Business Applications; Contact Center; Front-End Web & Mobile; Robotics; Security, Identity & Compliance
AWS_COLOR_TURQUOISE | #1B7B67 | End User Computing; Machine Learning; Migration & Transfer

## PNG images

For each symbol, there is a resized icon in PNG format generated from the source file. Where the original icons had transparency set, this has been kept in the generated icons. You can also use the images outside of PlantUML, e.g. for documents or presentations, but the official [AWS Architecture Icons](https://aws.amazon.com/architecture/icons/) are available in all popular formats.

### All generated AWS symbols and PNGs

Category | PUML Macros (Name) | Image (PNG) | PUML Url
  ---    |  ---  | :---:  | ---
"""

PUML_COPYRIGHT = """'Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
'SPDX-License-Identifier: MIT (For details, see https://github.com/awslabs/aws-icons-for-plantuml/blob/main/LICENSE)

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
            "source/official must contain folders of AWS icons to process. Please see README file for details."
        )
        sys.exit(1)
    # Start plantuml-mit-1.2023.1.jar and verify java
    try:
        subprocess.run(
            ["java", "-jar", "./plantuml-mit-1.2023.1.jar", "-version"],
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


def build_file_list(dir: str, glob: str):
    """Returns POSIX list of files

    :param dir: Starting directory to evaluate
    :type dir: str
    :param glob: glob pattern for file names
    :type glob: str
    :return: list of files
    :rtype: list
    """
    return sorted(
        Path(dir).glob(glob),
        key=lambda path: str(path).lower(),
    )


def create_config_template():
    """Create config_template.yml file from source icons"""

    source_files = []
    category_dict = {}
    dupe_check = []  # checking for duplicate names that need to be resolved

    for dir in dir_list:
        source_files = [str(i) for i in build_file_list(dir["dir"], dir["dir_glob"])]
        for i in source_files:
            # Get elements needed for YAML file
            # Exception is if the files originate from the "Category" directory
            category = Icon()._make_category(
                regex=dir["category_regex"],
                filename=i,
                mappings=dir["category_mappings"],
            )
            if category == "Groups":
                continue  # Groups will be added en-masse at the end

            target = Icon()._make_name(
                regex=dir["filename_regex"],
                filename=i,
                mappings=dir["filename_mappings"],
            )
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

            icon_entry = {
                "Source": source_name,
                "Target": target,
                "SourceDir": file_source_dir,
            }

            # Check for duplicate entries then append to
            if target not in dupe_check:
                dupe_check.append(target)
            else:
                icon_entry["ZComment"] = "******* Duplicate target name, must be made unique for All.puml ********"

            # Note: GroupIcons are deprecated, replaced by Groups
            if category == "GroupIcons" and target in GROUPICONS_COLORS:
                icon_entry["Color"] = GROUPICONS_COLORS[target]

            category_dict[category]["Icons"].append(icon_entry)

    # With the completed dictionary of entries, convert to an OrderedDict and sort by Category -> Target
    # The sorted template file makes it easier to review changes between new icon releases
    sorted_categories = OrderedDict()
    for category in sorted(category_dict):
        sorted_categories[category] = {"Icons": []}
        sorted_categories[category]["Icons"] = sorted(
            category_dict[category]["Icons"], key=lambda i: i["Target"]
        )
        if category in CATEGORY_COLORS:
            sorted_categories[category]["Color"] = CATEGORY_COLORS[category]
    yaml_content = {}
    yaml_content["Categories"] = dict(sorted_categories)

    with open("config-template.yml", "w") as f:
        f.write(TEMPLATE_DEFAULT)
        yaml.dump(yaml_content, f, default_flow_style=False)
        f.write(CATEGORY_GROUPS)
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
    if icon.skip_icon:
        sprite = ""
        print(f"skipping icon for {icon.source_name}")
    else:
        # create images without transparency for use with PlantUML sprites
        icon.generate_image(
            Path(f"../dist/{icon.category}"),
            color=True,
            max_target_size=64, # override to 64x64
            #max_target_size=icon.target_size, # use for mix of 64x64 and 48x48
            transparency=False,
            gradient=True,
        )
        sprite = icon.generate_puml_sprite(Path(f"../dist/{icon.category}"))
        # Recreate the images with transparency
        icon.generate_image(
            Path(f"../dist/{icon.category}"),
            color=True,
            max_target_size=64, # override to 64x64
            #max_target_size=icon.target_size, # use for mix of 64x64 and 48x48
            transparency=icon.transparency, # was True
            gradient=False,
        )
    print(f"generating PUML for {icon.source_name}")
    icon.generate_puml(Path(f"../dist/{icon.category}"), sprite)
    return


def main():

    if args["create_config_template"]:
        create_config_template()

    verify_environment()

    # clear out dist/ directory
    clean_dist()

    # Copy source/*.puml files to dist/
    copy_puml()

    # Build icons from files
    icons = []
    for dir in dir_list:
        for filename in build_file_list(dir["dir"], dir["dir_glob"]):
            icons.append(
                Icon(
                    posix_filename=filename,
                    config=config,
                    category_regex=dir["category_regex"],
                    filename_regex=dir["filename_regex"],
                    category_mappings=dir["category_mappings"],
                    filename_mappings=dir["filename_mappings"],
                )
            )

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
        #pass
        pool.apply_async(worker, args=(i,)) 
    pool.close()
    pool.join()

    # Generate "all.puml" files for each category
    for i in categories:
        create_category_all_file(Path(f"../dist/{i}"))

    # Create markdown sheet and place in dist
    sorted_icons = sorted(icons, key=lambda x: (x.category, x.target, x.skip_icon))
    markdown = MARKDOWN_PREFIX_TEMPLATE
    for i in categories:
        category = i
        if category == "GroupIcons":
            pass
        else:
            if category == "Groups":
                markdown += f"**{category}** | | | **{category}/all.puml**\n"
            else:
                markdown += f"**{category}** | {COLOR_MACROS[CATEGORY_COLORS[category]]} | | **{category}/all.puml**\n"
        for j in sorted_icons:
            if j.category == i:
                cat = j.category
                tgt = j.target
                skip_icon = j.skip_icon
                if cat == "GroupIcons":
                    pass
                elif cat == "Groups":
                    if skip_icon:
                        markdown += f"{cat} | {tgt}Group  | - | {cat}/{tgt}.puml\n"
                    else:
                        markdown += (
                            f"{cat} | {tgt}Group / ${tgt}IMG()  | ![{tgt}](dist/{cat}/{tgt}.png?raw=true) |"
                            f"{cat}/{tgt}.puml\n"
                        )
                else:
                    markdown += (
                        f"{cat} | {tgt} / {tgt}Participant / ${tgt}IMG()  | ![{tgt}](dist/{cat}/{tgt}.png?raw=true) |"
                        f"{cat}/{tgt}.puml\n"
                    )
    with open(Path("../AWSSymbols.md"), "w") as f:
        f.write(markdown)


if __name__ == "__main__":
    main()
