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
from datetime import datetime, timezone
import multiprocessing
import re
import xml.etree.ElementTree as ET
from multiprocessing import Pool
from pathlib import Path
from subprocess import PIPE
from collections import OrderedDict
from lxml import etree

import yaml

from awsicons.icon import Icon

# TODO - refactor to param file and/or arguments

# used to inject into aws-icons-mermaid.json
release_version = "19.0"
release_date_obj = datetime.strptime("2024-06-07", "%Y-%m-%d")
release_utc_seconds = int(release_date_obj.replace(tzinfo=timezone.utc).timestamp())

# This list are the directories to parse, what type of files they are, and globbing/regex
# to parse and process. This addresses the changing nature of the assets package.

# Source directories for the 19.0-2024.06.07 release

dir_list = [
    {
        "dir": "../source/official",
        # dir structure changed from Category-Icons_04-30-2021/Arch-Category_64/filename
        # to: Category-Icons_04-30-2021/64/filename
        "dir_glob": "Category-Icons_06072024/*48/*.png",
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
        "filename_mappings2": {},
    },
    {
        "dir": "../source/official",
        # "dir_glob": "Architecture-Service-Icons_04282023/**/*64/*.svg",
        "dir_glob": "Architecture-Service-Icons_06072024/**/*48/*.png",
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
         "filename_mappings2": {
            "marketplace-light": "marketplace",
            "application-auto-scaling": "application-auto-scaling2",
        },
    },
    {
        "dir": "../source/official",
        "dir_glob": "Resource-Icons_06072024/*/*.svg",
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
            "AuroraAmazonRDSInstanceAternate": "AuroraAmazonRDSInstanceAlternate",
            "AuroraAmazonAuroraInstancealternate": "AuroraAmazonAuroraInstanceAlternate",
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
            "SimpleStorageServiceDirectorybucket": "SimpleStorageServiceDirectoryBucket",
            "SimpleStorageServiceGeneralpurposebucket": "SimpleStorageServiceBucket",
        },
        "filename_mappings2": {            
            "aurora-amazon-rds-instance-aternate": "aurora-amazon-rds-instance-alternate",
            "elastic-container-service-copiiot-cli": "elastic-container-service-copilot-cli",
            "ec2-auto-scaling": "ec2-auto-scaling-resource",
            "route-53-route-53-application-recovery-controller":"route-53-application-recovery-controller",
            "database-migration-service-database-migration-workflow-or-job": "database-migration-service-database-migration-workflow-job",
            "elastic-file-system-efs-intelligent-tiering": "elastic-file-system-intelligent-tiering",
            "elastic-file-system-efs-one-zone": "elastic-file-system-one-zone",
            "elastic-file-system-efs-one-zone-infrequent-access": "elastic-file-system-one-zone-infrequent-access",
            "elastic-file-system-efs-standard": "elastic-file-system-standard",
            "elastic-file-system-efs-standard-infrequent-access": "elastic-file-system-standard-infrequent-access",
            "simple-storage-service-general-purpose-bucket": "simple-storage-service-bucket"
        },
    },
    {
        "dir": "../source/official",
        "dir_glob": "Resource-Icons_06072024/Res_General-Icons/Res_48_Light/*.svg",
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
        "filename_mappings2": {
            "database": "generic-database",
            "management-console": "aws-management-console",
            "shield": "shield2",
            "server": "traditional-server",
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
        "filename_mappings2": {},
    },
    {
        "dir": "../source/unofficial",
        "dir_glob": "Groups_04282023/*.touch",
        "category_regex": "[^.]*\/(Groups).*\/",
        "filename_regex": "[^.]*\/(.*)\.(?:png|touch)",
        "category_mappings": {},
        "filename_mappings": {},
        "filename_mappings2": {},
    },
]

CATEGORY_COLORS = {
    "Analytics": "Galaxy",
    "ArtificialIntelligence": "Orbit",
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
    "MigrationModernization": "Orbit",
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
# Curated config file for Release 19.0-2024.06.07 AWS Architecture Icons release (https://aws.amazon.com/architecture/icons/)
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
    Alignment: left
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
        Alignment: center
      Label: "Availability Zone"
      Source: Availability-Zone.touch
      SourceDir: Groups_04282023
      Target: AvailabilityZone
      Target2: availability-zone
    - Color: "#E7157B"
      Label: "AWS account"
      Source: AWS-Account.png
      SourceDir: Groups_04282023
      Target: AWSAccount
      Target2: aws-account
    - Color: $AWS_FG_COLOR
      Label: "AWS Cloud"
      Source: AWS-Cloud-alt.png
      SourceDir: Groups_04282023
      SourceDark: AWS-Cloud-alt_Dark.png
      SourceDirDark: Groups_04282023/Dark
      Target: AWSCloudAlt
      Target2: aws-cloud-alt
    - Color: $AWS_FG_COLOR
      Label: "AWS Cloud"
      Source: AWS-Cloud.png
      SourceDir: Groups_04282023
      SourceDark: AWS-Cloud_Dark.png
      SourceDirDark: Groups_04282023/Dark
      Target: AWSCloud
      Target2: aws-cloud
    - Color: "#7AA116"
      Label: "AWS IoT Greengrass Deployment"
      Source: AWS-IoT-Greengrass-Deployment.png
      SourceDir: Groups_04282023
      Target: IoTGreengrassDeployment
      Target2: iot-greengrass-deployment
    - Color: "#7AA116"
      Label: "AWS IoT Greengrass"
      Source: AWS-IoT-Greengrass.png
      SourceDir: Groups_04282023
      Target: IoTGreengrass
      Target2: iot-greengrass
    - Color: "#E7157B"
      Label: "AWS Step Functions workflow"
      Source: AWS-Step-Functions-workflow.png
      SourceDir: Groups_04282023
      Target: StepFunctionsWorkflow
      Target2: step-functions-workflow
    - Color: "#ED7100"
      Group:
        BorderStyle: dashed
        Alignment: center
      Label: "Auto Scaling group"
      Source: Auto-Scaling-group.png
      SourceDir: Groups_04282023
      Target: AutoScalingGroup
      Target2: auto-scaling-group
    - Color: "#7D8998"
      Label: "Corporate data center"
      Source: Corporate-data-center.png
      SourceDir: Groups_04282023
      Target: CorporateDataCenter
      Target2: corporate-data-center
    - Color: "#ED7100"
      Label: "EC2 instance contents"
      Source: EC2-instance-contents.png
      SourceDir: Groups_04282023
      Target: EC2InstanceContents
      Target2: ec2-instance-contents
    - Color: "#ED7100"
      Label: "Elastic Beanstalk container"
      Source: Elastic-Beanstalk-container.png
      SourceDir: Groups_04282023
      Target: ElasticBeanstalkContainer
      Target2: elastic-beanstalk-container
    - Color: "#7D8998"
      Group:
        BorderStyle: dashed
        Alignment: center
      Label: "Generic group"
      Source: Generic-group.touch
      SourceDir: Groups_04282023
      Target: Generic
      Target2: generic
    - Color: "#7D8998"
      Group:
        Alignment: center
      Label: "Generic group"
      Source: Generic-group-alt.touch
      SourceDir: Groups_04282023
      Target: GenericAlt
      Target2: generic-alt
    - Color: "#C925D1"
      Label: "Generic Blue group"
      Source: Placeholder_Blue.png
      SourceDir: Groups_04282023
      Target: GenericBlue
      Target2: generic-blue
    - Color: "#7AA116"
      Label: "Generic Green group"
      Source: Placeholder_Green.png
      SourceDir: Groups_04282023
      Target: GenericGreen
      Target2: generic-green
    - Color: "#ED7100"
      Label: "Generic Orange group"
      Source: Placeholder_Orange.png
      SourceDir: Groups_04282023
      Target: GenericOrange
      Target2: generic-orange
    - Color: "#E7157B"
      Label: "Generic Pink group"
      Source: Placeholder_Pink.png
      SourceDir: Groups_04282023
      Target: GenericPink
      Target2: generic-pink
    - Color: "#8C4FFF"
      Label: "Generic Purple group"
      Source: Placeholder_Purple.png
      SourceDir: Groups_04282023
      Target: GenericPurple
      Target2: generic-purple
    - Color: "#DD344C"
      Label: "Generic Red group"
      Source: Placeholder_Red.png
      SourceDir: Groups_04282023
      Target: GenericRed
      Target2: generic-red
    - Color: "#01A88D"
      Label: "Generic Turquoise group"
      Source: Placeholder_Turquoise.png
      SourceDir: Groups_04282023
      Target: GenericTurquoise
      Target2: generic-turquoise
    - Color: "#00A4A6"
      Label: "Private subnet"
      Source: Private-subnet.png
      SourceDir: Groups_04282023
      Target: PrivateSubnet
      Target2: private-subnet
    - Color: "#7AA116"
      Label: "Public subnet"
      Source: Public-subnet.png
      SourceDir: Groups_04282023
      Target: PublicSubnet
      Target2: public-subnet
    - Color: "#00A4A6"
      Group:
        BorderStyle: dotted
      Label: "Region"
      Source: Region.png
      SourceDir: Groups_04282023
      Target: Region
      Target2: region
    - Color: "#DD344C"
      Label: "Security group"
      Group:
        Alignment: center
      Source: Security-group.touch
      SourceDir: Groups_04282023
      Target: SecurityGroup
      Target2: security-group
    - Color: "#7D8998"
      Label: "Server contents"
      Source: Server-contents.png
      SourceDir: Groups_04282023
      Target: ServerContents
      Target2: server-contents
    - Color: "#ED7100"
      Label: "Spot Fleet"
      Source: Spot-Fleet.png
      SourceDir: Groups_04282023
      Target: SpotFleet
      Target2: spot-fleet
    - Color: "#8C4FFF"
      Label: "Virtual private cloud (VPC)"
      Source: Virtual-Private-Network-VPC.png
      SourceDir: Groups_04282023
      Target: VPC
      Target2: vpc
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

PUML Macro (Name) | Color | | Categories
  ---  |  ---  |  ---  |  ---
$AWS_BG_COLOR | #FFFFFF | |
$AWS_FG_COLOR | #000000 | |
$AWS_ARROW_COLOR | #000000 | |
$AWS_COLOR_SQUID | #232F3E | |
$AWS_COLOR_GRAY | #7D8998 (borders) | |
$AWS_COLOR_NEBULA | #C925D1 (blue replacement) | ![Nebula](dist/Groups/GenericBlue.png?raw=true) | Customer Enablement; Database; Developer Tools; Satellite
$AWS_COLOR_ENDOR | #7AA116 (green) | ![Endor](dist/Groups/GenericGreen.png?raw=true) | Cloud Financial Management; Internet of Things; Storage
$AWS_COLOR_SMILE | #ED7100 (orange) | ![Smile](dist/Groups/GenericOrange.png?raw=true) | Blockchain; Compute; Containers; Media Services; Quantum Technologies
$AWS_COLOR_COSMOS | #E7157B (pink) | ![Cosmos](dist/Groups/GenericPink.png?raw=true) | Application Integration; Management & Governance
$AWS_COLOR_GALAXY | #8C4FFF (purple) | ![Galaxy](dist/Groups/GenericPurple.png?raw=true) | Analytics; Games; Networking & Content Delivery; Serverless
$AWS_COLOR_MARS | #DD344C (red) | ![Mars](dist/Groups/GenericRed.png?raw=true) | Business Applications; Contact Center; Front-End Web & Mobile; Robotics; Security, Identity & Compliance
$AWS_COLOR_ORBIT | #01A88D (turquoise) | ![Orbit](dist/Groups/GenericTurquoise.png?raw=true) | Artificial Intelligence; End User Computing; Migration & Modernization

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
        "Creates a YAML config template based on official source for customization"
    ),
)
parser.add_argument(
    "--symbols-only",
    action="store_true",
    default=False,
    help="Only generates the AWSSymbols.md. Structuriz theme, and Mermaid JSON files",
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
    except Exception as e: # pylint: disable=broad-except
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
    # Start plantuml-mit-1.2024.6.jar and verify java
    try:
        subprocess.run(
            ["java", "-jar", "./plantuml-mit-1.2024.6.jar", "-version"],
            shell=True,
            stdout=PIPE,
            stderr=PIPE,
        )
    except Exception as e: # pylint: disable=broad-except
        print(f"Error executing plantuml jar file, {e}")
        sys.exit(1)

    # Checks complete, return if not doing a pre-flight
    if args["check_env"]:
        # dry run only
        print("Prerequisites met, exiting")
        sys.exit(0)
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
    dupe_check2 = []

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

            (target, target2) = Icon()._make_name(
                regex=dir["filename_regex"],
                filename=i,
                mappings=dir["filename_mappings"],
                mappings2=dir["filename_mappings2"],
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
                "Target2": target2,
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
            if target2 not in dupe_check2:
                dupe_check2.append(target2)
            else:
                icon_entry["ZComment2"] = "******* Duplicate target2 name, must be made unique for aws-icons-mermaid.json ********"

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

def build_mermaid_icon(mermaid, svg_filename, cat, mermaid_target):
    """add an icon to the mermaid object"""
    svg_parser = etree.XMLParser(remove_blank_text=True)
    svg_tree = etree.parse(svg_filename, svg_parser)
    svg_root = svg_tree.getroot()
    svg_width = svg_root.get("width").strip("px")
    svg_height = svg_root.get("height").strip("px")
    # Register the SVG namespace to avoid automatic namespace additions
    ET.register_namespace('', "http://www.w3.org/2000/svg")
    ET.register_namespace('xlink', "http://www.w3.org/1999/xlink")
    svg_body = ''.join((ET.tostring(child, encoding='unicode', method='xml') for child in svg_root if child.tag != '{http://www.w3.org/2000/svg}title'))
    # Remove any remaining xmlns declrations
    svg_body = re.sub(r'\sxmlns[^"]*"[^"]*"', '', svg_body)

    mermaid["info"]["total"] = mermaid["info"]["total"] + 1
    if (mermaid["categories"].get(cat) is None):
        mermaid["categories"][cat] = []
    mermaid["categories"][cat].append(mermaid_target)
    mermaid["icons"][mermaid_target] = {
        "body": svg_body,
    }
    if mermaid["width"] != int(svg_width):
        mermaid["icons"][mermaid_target]["width"] = int(svg_width)
    if mermaid["height"] != int(svg_height):
        mermaid["icons"][mermaid_target]["height"] = int(svg_height)


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
    markdown = [MARKDOWN_PREFIX_TEMPLATE]
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
    mermaid = {
        "prefix": "aws",
        "info": {
            "name": "AWS Icons",
            "total": 0,
            "version": release_version,
            "author": {
                "name": "AWS",
                "url": "https://github.com/awslabs/aws-icons-for-plantuml",
            },
            "license": {
                "title": "Creative Commons Attribution No Derivatives 2.0",
                "spdx": "CC-BY-ND-2.0",
                "url": "https://github.com/awslabs/aws-icons-for-plantuml/blob/main/LICENSE",
            },
            "samples": [
                "ec2",
                "simple-storage-service",
                "lambda",
            ],
            "palette": True
        },
        "lastModified": release_utc_seconds,
        "width": 48,
        "height": 48,
        "icons": {
        },
        "categories": {
        },
    }

    for i in categories:
        category = i
        if category == "GroupIcons" or category == "Uncategorized":
            pass
        else:
            if category == "Groups":
                markdown.append(f"**{category}** | | | **{category}/all.puml**\n")
            else:
                markdown.append(f"**{category}** | $AWSColor({category}) / {COLOR_MACROS[CATEGORY_COLORS[category]]} | | **{category}/all.puml**\n")
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
                        markdown.append(f"{cat} | {tgt}Group  | - | {cat}/{tgt}.puml\n")
                    else:
                        markdown.append((
                            f"{cat} | {tgt}Group / ${tgt}IMG()  | {img} |"
                            f"{cat}/{tgt}.puml\n"
                        ))
                else:
                    markdown.append((
                        f"{cat} | {tgt} / {tgt}Participant / ${tgt}IMG()  | {img} |"
                        f"{cat}/{tgt}.puml\n"
                    ))

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

                # Add element to Mermaid
                try:
                    svg_filename = re.sub(r'\.png$','.svg', str(j.filename))
                    if svg_filename.endswith(".svg"):
                        build_mermaid_icon(mermaid, svg_filename, cat, j.target2)

                    if j.filename_dark is not None:
                        svg_filename_dark = re.sub(r'\.png$','.svg', str(j.filename_dark))
                        if svg_filename_dark.endswith(".svg"):
                            build_mermaid_icon(mermaid, svg_filename_dark, cat, f"{j.target2}-dark")

                except Exception as e: # pylint: disable=broad-except
                    print(f"Error: {e} adding {j.target2} to aws-icons-mermaid.json")

    with open(Path("../AWSSymbols.md"), "w") as f:
        f.write(''.join(markdown))
    with open(Path("../dist/aws-icons-structurizr-theme.json"), "w") as f:
        f.write(json.dumps(structerizr, indent=2))
    with open(Path("../dist/aws-icons-mermaid.json"), "w") as f:
        f.write(json.dumps(mermaid, indent=2))

if __name__ == "__main__":
    main()
