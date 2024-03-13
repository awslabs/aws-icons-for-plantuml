#!/usr/bin/env python3
# Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT (For details, see https://github.com/awslabs/aws-icons-for-plantuml/blob/main/LICENSE)


"""icon-builder.py: Build AWS Icons for PlantUML"""

import json
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


# Source directories for the 17-2023.10.23 release
dir_list = [
    {
        "dir": "../source/official",
        # dir structure changed from Category-Icons_04-30-2021/Arch-Category_64/filename
        # to: Category-Icons_04-30-2021/64/filename
        "dir_glob": "Category-Icons_01312024/*48/*.png",
        "category_regex": "[^.]*\/Arch-Category_(.*)_\d*\.png$",
        "filename_regex": "[^.]*\/Arch-Category_(.*)_\d*\.png$",
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
        # "dir_glob": "Architecture-Service-Icons_04282023/**/*64/*.svg",
        "dir_glob": "Architecture-Service-Icons_01312024/**/*48/*.png",
        "category_regex": "[^.]*\/(?:Arch_)(.*)\/(?:.*)\/(?:.*$)",
        "filename_regex": "[^.]*Arch_(?:Amazon.|AWS.)?(.*)_\d*\.png$",
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
            "MarketplaceLight": "Marketplace",
            "ApplicationAutoScaling": "ApplicationAutoScaling2",
        },
    },
    {
        "dir": "../source/official",
        "dir_glob": "Resource-Icons_01312024/*/*.svg",
        "category_regex": "[^.]*\/(?:Res_)(.*)\/(?:.*$)",
        "filename_regex": "[^.]*Res_(?:Amazon.|AWS.)?(.*)_\d*\.svg$",
        "category_mappings": {
            "GeneralIcons": "General",
            "InternetofThings": "InternetOfThings",
            "loT": "InternetOfThings",
            "IoT": "InternetOfThings",
            "MigrationandTransfer": "MigrationTransfer",
            "NetworkingandContentDelivery": "NetworkingContentDelivery",
            "SecurityIdentityandCompliance": "SecurityIdentityCompliance",
        },
        "filename_mappings": {
            "ElasticContainerServiceCopiIoTCLI": "ElasticContainerServiceCopilotCLI",
            "EC2AutoScaling": "EC2AutoScalingResource",
            "Route53Route53ApplicationRecoveryController": "Route53ApplicationRecoveryController",
            "DatabaseMigrationServiceDatabasemigrationworkfloworjob": "DatabaseMigrationServiceDatabasemigrationworkflowjob",
            "BackupAWSBackupSupportforVMwareWorkloads": "BackupAWSBackupsupportforVMwareWorkloads",
            "ElasticFileSystemEFSIntelligentTiering": "ElasticFileSystemIntelligentTiering",
            "ElasticFileSystemEFSOneZone": "ElasticFileSystemOneZone",
            "ElasticFileSystemEFSOneZoneInfrequentAccess": "ElasticFileSystemOneZoneInfrequentAccess",
            "ElasticFileSystemEFSStandard": "ElasticFileSystemStandard",
            "ElasticFileSystemEFSStandardInfrequentAccess": "ElasticFileSystemStandardInfrequentAccess",
        },
    },
    {
        "dir": "../source/official",
        "dir_glob": "Resource-Icons_01312024/Res_General-Icons/Res_48_Light/*.svg",
        "category_regex": "[^.]*\/(?:Res_)(.*)\/(?:.*)\/(?:.*$)",
        "filename_regex": "[^.]*Res_General-Icons\/Res_48_Light\/*Res_(?:Amazon.|AWS.)?(.*)_\d*_Light\.svg$",
        "category_mappings": {
            "GeneralIcons": "General",
        },
        "filename_mappings": {
            "Database": "Genericdatabase",
            "ManagementConsole": "AWSManagementConsole",
            "Shield": "Shield2",
            "Server": "Traditionalserver",
        },
    },
    # {
    #     "dir": "../source/unofficial",
    #     "dir_glob": "AWS-Architecture-Icons_SVG_20200430/SVG Light/_Group Icons/*.svg",
    #     "category_regex": "[^.]*\/_(.*)\/",
    #     "filename_regex": "[^.]*\/(.*)_light-bg\.svg",
    #     "category_mappings": {},
    #     "filename_mappings": {
    #         "AWSCloud": "Cloud",
    #         "AWSCloudalt": "Cloudalt",
    #         "AWSStepFunction": "StepFunction",
    #         "AutoScaling": "AutoScalingGroup",
    #         "Corporatedatacenter": "CorporateDataCenter",
    #         "EC2instancecontainer": "EC2InstanceContainer",
    #         "ElasticBeanstalkcontainer": "ElasticBeanstalkContainer",
    #         "Servercontents": "ServerContents",
    #         "Spotfleet": "SpotFleet",
    #         "VPCsubnetprivate": "VPCSubnetPrivate",
    #         "VPCsubnetpublic": "VPCSubnetPublic",
    #         "VirtualprivatecloudVPC": "VirtualPrivateCloudVPC",
    #     },
    # },
    {
        "dir": "../source/unofficial",
        "dir_glob": "Groups_04282023/*.png",
        "category_regex": "[^.]*\/(Groups).*\/",
        "filename_regex": "[^.]*\/(.*)\.(?:png|touch)",
        "category_mappings": {},
        "filename_mappings": {},
    },
    {
        "dir": "../source/unofficial",
        "dir_glob": "Groups_04282023/*.touch",
        "category_regex": "[^.]*\/(Groups).*\/",
        "filename_regex": "[^.]*\/(.*)\.(?:png|touch)",
        "category_mappings": {},
        "filename_mappings": {},
    },
]

CATEGORY_COLORS = {
    "Analytics": "Galaxy",
    "ApplicationIntegration": "Cosmos",
    "Blockchain": "Smile",
    "BusinessApplications": "Mars",
    "CloudFinancialManagement": "Endor",
    "Compute": "Smile",
    "ContactCenter": "Mars",
    "Containers": "Smile",
    "CustomerEnablement": "Nebula",
    "Database": "Nebula",
    "DeveloperTools": "Nebula",
    "EndUserComputing": "Orbit",
    "FrontEndWebMobile": "Mars",
    "Games": "Galaxy",
    "General": "Squid",
    "InternetOfThings": "Endor",
    "MachineLearning": "Orbit",
    "ManagementGovernance": "Cosmos",
    "MediaServices": "Smile",
    "MigrationTransfer": "Orbit",
    "NetworkingContentDelivery": "Galaxy",
    "QuantumTechnologies": "Smile",
    "Robotics": "Mars",
    "Satellite": "Nebula",
    "SecurityIdentityCompliance": "Mars",
    "Serverless": "Galaxy",
    "Storage": "Endor",
    "VRAR": "Cosmos",
}

GROUPICONS_COLORS = {
    "AutoScalingGroup": "Smile",
    "Cloud": "Squid",
    "Cloudalt": "Squid",
    "CorporateDataCenter": "Squid",
    "EC2InstanceContainer": "Smile",
    "ElasticBeanstalkContainer": "Smile",
    "Region": "Nebula",
    "ServerContents": "Squid",
    "SpotFleet": "Smile",
    "StepFunction": "Cosmos",
    "VPCSubnetPrivate": "Nebula",
    "VPCSubnetPublic": "Endor",
    "VirtualPrivateCloudVPC": "Endor",
}

COLOR_MACROS = {
    "Nebula": "$AWS_COLOR_NEBULA",
    "Mars": "$AWS_COLOR_MARS",
    "Orbit": "$AWS_COLOR_ORBIT",
    "Endor": "$AWS_COLOR_ENDOR",
    "Cosmos": "$AWS_COLOR_COSMOS",
    "Smile": "$AWS_COLOR_SMILE",
    "Galaxy": "$AWS_COLOR_GALAXY",
    "Squid": "$AWS_COLOR_SQUID",
    "White": "$AWS_BG_COLOR",
}
COLOR_VALUES = {
    "Nebula": "#C925D1",
    "Mars": "#DD344C",
    "Orbit": "#01A88D",
    "Endor": "#7AA116",
    "Cosmos": "#E7157B",
    "Smile": "#ED7100",
    "Galaxy": "#8C4FFF",
    'Squid': "#232F3E",
    "White": "#FFFFFF",
}

TEMPLATE_DEFAULT = """
# Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT (For details, see https://github.com/awslabs/aws-icons-for-plantuml/blob/main/LICENSE)
#
# Curated config file for Release 18.0-2024.02.06 AWS Architecture Icons release (https://aws.amazon.com/architecture/icons/)
# cSpell: disable
Defaults:
  Colors:
    Nebula: "#C925D1"
    Mars: "#DD344C"
    Orbit: "#01A88D"
    Endor: "#7AA116"
    Cosmos: "#E7157B"
    Smile: "#ED7100"
    Galaxy: "#8C4FFF"
    Squid: "#232F3E"
    White: "#FFFFFF"
  # Defaults for services not found
  Category:
    Color: Squid
  Group:
    BorderStyle: plain
    Label: "Generic group"
  # Maximum in either height or width in pixels
  TargetMaxSize: 64
"""

# \\\\n in Python needed to generate \\n in YAML for \n in output .puml
CATEGORY_GROUPS = """
  Groups:
    Icons:
    - Color: "#00A4A6"
      Group:
        BorderStyle: dashed
      Label: "\\\\n  Availability Zone"
      Source: Availability-Zone.touch
      SourceDir: Groups_04282023
      Target: AvailabilityZone
    - Color: "#E7157B"
      Label: "AWS account"
      Source: AWS-Account.png
      SourceDir: Groups_04282023
      Target: AWSAccount
    - Color: $AWS_FG_COLOR
      Label: "AWS Cloud"
      Source: AWS-Cloud-alt.png
      SourceDir: Groups_04282023
      SourceDark: AWS-Cloud-alt_Dark.png
      SourceDirDark: Groups_04282023/Dark
      Target: AWSCloudAlt
    - Color: $AWS_FG_COLOR
      Label: "AWS Cloud"
      Source: AWS-Cloud.png
      SourceDir: Groups_04282023
      SourceDark: AWS-Cloud_Dark.png
      SourceDirDark: Groups_04282023/Dark
      Target: AWSCloud
    - Color: "#7AA116"
      Label: "AWS IoT Greengrass Deployment"
      Source: AWS-IoT-Greengrass-Deployment.png
      SourceDir: Groups_04282023
      Target: IoTGreengrassDeployment
    - Color: "#7AA116"
      Label: "AWS IoT Greengrass"
      Source: AWS-IoT-Greengrass.png
      SourceDir: Groups_04282023
      Target: IoTGreengrass
    - Color: "#E7157B"
      Label: "AWS Step Functions workflow"
      Source: AWS-Step-Functions-workflow.png
      SourceDir: Groups_04282023
      Target: StepFunctionsWorkflow
    - Color: "#ED7100"
      Group:
        BorderStyle: dashed
      Label: "\\\\n  Auto Scaling group"
      Source: Auto-Scaling-group.png
      SourceDir: Groups_04282023
      Target: AutoScalingGroup
    - Color: "#7D8998"
      Label: "Corporate data center"
      Source: Corporate-data-center.png
      SourceDir: Groups_04282023
      Target: CorporateDataCenter
    - Color: "#ED7100"
      Label: "EC2 instance contents"
      Source: EC2-instance-contents.png
      SourceDir: Groups_04282023
      Target: EC2InstanceContents
    - Color: "#ED7100"
      Label: "Elastic Beanstalk container"
      Source: Elastic-Beanstalk-container.png
      SourceDir: Groups_04282023
      Target: ElasticBeanstalkContainer
    - Color: "#7D8998"
      Group:
        BorderStyle: dashed
      Label: "\\\\n  Generic group"
      Source: Generic-group.touch
      SourceDir: Groups_04282023
      Target: Generic
    - Color: "#7D8998"
      Label: "\\\\n  Generic group"
      Source: Generic-group-alt.touch
      SourceDir: Groups_04282023
      Target: GenericAlt
    - Color: "#C925D1"
      Label: "Generic Blue group"
      Source: Placeholder_Blue.png
      SourceDir: Groups_04282023
      Target: GenericBlue
    - Color: "#7AA116"
      Label: "Generic Green group"
      Source: Placeholder_Green.png
      SourceDir: Groups_04282023
      Target: GenericGreen
    - Color: "#ED7100"
      Label: "Generic Orange group"
      Source: Placeholder_Orange.png
      SourceDir: Groups_04282023
      Target: GenericOrange
    - Color: "#E7157B"
      Label: "Generic Pink group"
      Source: Placeholder_Pink.png
      SourceDir: Groups_04282023
      Target: GenericPink
    - Color: "#8C4FFF"
      Label: "Generic Purple group"
      Source: Placeholder_Purple.png
      SourceDir: Groups_04282023
      Target: GenericPurple
    - Color: "#DD344C"
      Label: "Generic Red group"
      Source: Placeholder_Red.png
      SourceDir: Groups_04282023
      Target: GenericRed
    - Color: "#01A88D"
      Label: "Generic Turquoise group"
      Source: Placeholder_Turquoise.png
      SourceDir: Groups_04282023
      Target: GenericTurquoise
    - Color: "#00A4A6"
      Label: "Private subnet"
      Source: Private-subnet.png
      SourceDir: Groups_04282023
      Target: PrivateSubnet
    - Color: "#7AA116"
      Label: "Public subnet"
      Source: Public-subnet.png
      SourceDir: Groups_04282023
      Target: PublicSubnet
    - Color: "#00A4A6"
      Group:
        BorderStyle: dotted
      Label: "Region"
      Source: Region.png
      SourceDir: Groups_04282023
      Target: Region
    - Color: "#DD344C"
      Label: "\\\\n  Security group"
      Source: Security-group.touch
      SourceDir: Groups_04282023
      Target: SecurityGroup
    - Color: "#7D8998"
      Label: "Server contents"
      Source: Server-contents.png
      SourceDir: Groups_04282023
      Target: ServerContents
    - Color: "#ED7100"
      Label: "Spot Fleet"
      Source: Spot-Fleet.png
      SourceDir: Groups_04282023
      Target: SpotFleet
    - Color: "#8C4FFF"
      Label: "Virtual private cloud (VPC)"
      Source: Virtual-Private-Network-VPC.png
      SourceDir: Groups_04282023
      Target: VPC
"""

MARKDOWN_PREFIX_TEMPLATE = """
<!--
Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT (For details, see https://github.com/awslabs/aws-icons-for-plantuml/blob/main/LICENSE)
-->
# AWS Symbols

The main table lists all AWS symbols in the `dist/` directory, sorted by category.

If you want to reference and use these files without Internet connectivity, you can also download the whole [*PlantUML Icons for AWS* dist](dist/) directory and reference it locally with PlantUML.

## Colors

These colors are defined in `AWSCommon.puml`

PUML Macro (Name) | Color | Categories
  ---  |  ---  | ---
$AWS_BG_COLOR | #FFFFFF |
$AWS_FG_COLOR | #000000 |
$AWS_ARROW_COLOR | #000000 |
$AWS_COLOR_SQUID | #232F3E |
$AWS_COLOR_GRAY | #7D8998 (borders) |
$AWS_COLOR_NEBULA | #C925D1 (blue replacement) | Customer Enablement; Database; Developer Tools; Satellite
$AWS_COLOR_ENDOR | #7AA116 (green) | Cloud Financial Management; Internet of Things; Storage
$AWS_COLOR_SMILE | #ED7100 (orange) | Blockchain; Compute; Containers; Media Services; Quantum Technologies
$AWS_COLOR_COSMOS | #E7157B (pink) | Application Integration; Management & Governance
$AWS_COLOR_GALAXY | #8C4FFF (purple) | Analytics; Games; Networking & Content Delivery; Serverless
$AWS_COLOR_MARS | #DD344C (red) | Business Applications; Contact Center; Front-End Web & Mobile; Robotics; Security, Identity & Compliance
$AWS_COLOR_ORBIT | #01A88D (turquoise) | End User Computing; Machine Learning; Migration & Transfer

An alternative and recommended way to find a category color is the `$AWSColor($category)` function, where the `$category` is the normalized name of the category in the table below.  For example, to get the color for the "Application Integration" category, call `$AWSColor(ApplicationIntegration)` or for "Management & Governance" for call `$AWSColor(ManagementGovernance)`.

When `!$AWS_DARK = true` precedes the `!include` of `AWSCommon.puml`, some colors are alternately defined:

PUML Macro (Name) | Color
  ---  |  --- 
$AWS_BG_COLOR | #000000
$AWS_FG_COLOR | #FFFFFF
$AWS_ARROW_COLOR | #9BA7B6

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
parser.add_argument(
    "--symbols-only",
    action="store_true",
    default=False,
    help="Only generates the AWSSymbols.md and Structuriz theme files",
)
parser.add_argument(
    "--create-color-json",
    action="store_true",
    default=False,
    help="Prints AWS Colors JSON to stdout",
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
    # Start plantuml-mit-1.2024.3.jar and verify java
    try:
        subprocess.run(
            ["java", "-jar", "./plantuml-mit-1.2024.3.jar", "-version"],
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
            if category == "General":
                if target == "MarketplaceDark":
                    continue # not needed as standalone, combined with MarketplaceLight
                else:
                    icon_entry["SourceDark"] = source_name.replace("Light", "Dark")
                    icon_entry["SourceDirDark"] = file_source_dir.replace("Light", "Dark")

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
        icon.generate_images(
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

    # Build icons from files
    icons = []
    for dir in dir_list:
        for filename in build_file_list(dir["dir"], dir["dir_glob"]):
            icon = Icon(
                    posix_filename=filename,
                    config=config,
                    category_regex=dir["category_regex"],
                    filename_regex=dir["filename_regex"],
                    category_mappings=dir["category_mappings"],
                    filename_mappings=dir["filename_mappings"],
                   )
            if icon.category == "Uncategorized":
                print(f"skipping Uncategorized {icon.source_name}")
            else:
                icons.append(icon)

    categories = sorted(set([icon.category for icon in icons]))

    if not (args["symbols_only"] or args["create_color_json"]):
        # clear out dist/ directory
        clean_dist()

        # Copy source/*.puml files to dist/
        copy_puml()

        # Create category directories
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

    if args["create_color_json"]:
        color_map = {}
        for category in categories:
            if category in ["GroupIcons", "Uncategorized", "Groups"]:
                pass
            else:
                color_map[str(category).lower()] = COLOR_VALUES[CATEGORY_COLORS[category]]
        print("!$AWS_CATEGORY_COLORS = " + json.dumps(color_map, indent=2))
        sys.exit(0)

    # Create markdown sheet and place in dist
    sorted_icons = sorted(icons, key=lambda x: (x.category, x.target, x.skip_icon))
    markdown = MARKDOWN_PREFIX_TEMPLATE
    structerizr = {
        "name": "AWS Icons for PlantUML Structurizr theme",
        "description": "This theme includes element styles with icons for each of the AWS services, based upon the AWS Architecture Icons (https://aws.amazon.com/architecture/icons/) and using tag names from AWS Icons for PlantUML (https://github.com/awslabs/aws-icons-for-plantuml).",
        "elements": [
            {
                "tag": "Element",
                "shape": "Box",
                "color": "#000000",
                "stroke": "#000000",
                "strokeWidth": 2,
                "background": "#ffffff",
            }
        ]
    }
    for i in categories:
        category = i
        if category == "GroupIcons" or category == "Uncategorized":
            pass
        else:
            if category == "Groups":
                markdown += f"**{category}** | | | **{category}/all.puml**\n"
            else:
                markdown += f"**{category}** | $AWSColor({category}) / {COLOR_MACROS[CATEGORY_COLORS[category]]} | | **{category}/all.puml**\n"
        for j in sorted_icons:
            if j.category == i:
                cat = j.category
                tgt = j.target
                skip_icon = j.skip_icon
                if j.filename_dark is not None:
                    img = f"![{tgt}](dist/{cat}/{tgt}.png?raw=true#gh-light-mode-only)"
                    img = img + f" ![{tgt}](dist/{cat}/{tgt}_Dark.png?raw=true#gh-dark-mode-only)"
                else:
                    img = f"![{tgt}](dist/{cat}/{tgt}.png?raw=true)"
                if cat == "GroupIcons":
                    pass
                elif cat == "Groups":
                    if skip_icon:
                        markdown += f"{cat} | {tgt}Group  | - | {cat}/{tgt}.puml\n"
                    else:
                        markdown += (
                            f"{cat} | {tgt}Group / ${tgt}IMG()  | {img} |"
                            f"{cat}/{tgt}.puml\n"
                        )
                else:
                    markdown += (
                        f"{cat} | {tgt} / {tgt}Participant / ${tgt}IMG()  | {img} |"
                        f"{cat}/{tgt}.puml\n"
                    )

                # Add element to Structurizr theme
                element = {
                    "tag": tgt,
                    "stroke": j.color
                }
                if j.color == "$AWS_FG_COLOR":
                     element["stroke"] = "#000000"
                if j.group_border_style == "dashed" or j.group_border_style == "dotted":
                    # solid|dashed|dotted
                    element["border"] = j.group_border_style

                if not skip_icon:
                    element["icon"] = f"{cat}/{tgt}.png"
                structerizr["elements"].append(element)

    with open(Path("../AWSSymbols.md"), "w") as f:
        f.write(markdown)
    with open(Path("../dist/aws-icons-structurizr-theme.json"), "w") as f:
        f.write(json.dumps(structerizr, indent=2))


if __name__ == "__main__":
    main()
