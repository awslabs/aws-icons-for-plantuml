#!/usr/bin/env python3
# Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT (For details, see https://github.com/awslabs/aws-icons-for-plantuml/blob/main/LICENSE)


"""upgrade.py: Upgrade AWS Icons for PlantUML references"""

import os
import re
from typing import List
import argparse
import glob

# To update for a new version
# 1. add new "vX.Y" version to end of SUPPORTED_VERSIONS
# 2. add a BREAKING_CHANGES["vX.Y"] structure

SUPPORTED_VERSIONS = ["v13.0", "v13.1", "v14.0", "v15.0", "v16.0", "v17.0", "v18.0", "v19.0"]

UPDATES = {
    "AWS_COLOR": "$AWS_COLOR_SQUID",
    "AWS_BG_COLOR": "$AWS_BG_COLOR",
    "AWS_BORDER_COLOR": "$AWS_BORDER_COLOR",
    "AWS_COLOR_BLUE": "$AWS_COLOR_NEBULA",
    "AWS_COLOR_GREEN": "$AWS_COLOR_ENDOR",
    "AWS_COLOR_ORANGE": "$AWS_COLOR_SMILE",
    "AWS_COLOR_PINK": "$AWS_COLOR_COSMOS",
    "AWS_COLOR_PURPLE": "$AWS_COLOR_GALAXY",
    "AWS_COLOR_RED": "$AWS_COLOR_MARS",
    "AWS_COLOR_TURQUOISE": "$AWS_COLOR_ORBIT",
}

FLAT_UPDATES = "|".join(str(item) for item in UPDATES.keys())
update_pattern = fr"\b(?![$])(?P<macro>{FLAT_UPDATES})\b"

BREAKING_CHANGES = {}
"""
Order of operations on BREAKING_CHANGES

1. Process RENAMED category
2. Process REPLACED icon
3. Process REMOVED icon
"""

BREAKING_CHANGES["v13.0"] = {
    "ARVR": {
        "RENAMED": "VRAR"
    },
    "AWSCostManagement": {
        "RENAMED": "CloudFinancialManagement"
    },
    "Compute": {
        "REPLACED": {
            "Outposts1Uand2UServers": "Outpostsservers",
            "Outposts": "Outpostsrack"
        }
    },
    "Storage": {
        "REPLACED": {
            "FSxforWindowsFileServer": "FSxforWFS",
            "SimpleStorageServiceS3Glacier": "SimpleStorageServiceS3GlacierFlexibleRetrieval",
            "S3OnOutpostsStorage": "S3onOutposts",
            "StorageGatewayNonCachedVolume": "StorageGatewayNoncachedVolume",
            "ElasticFileSystem": "EFS"
        }
    }
}
BREAKING_CHANGES["v13.1"] = {
    "GroupIcons": {
        "RENAMED": "Groups"
    },
}

BREAKING_CHANGES["v14.0"] = {
    "Compute": {
        "REPLACED": {
            "ThinkBoxDeadline": "ThinkboxDeadline",
            "ThinkBoxFrost": "ThinkboxFrost",
            "ThinkBoxKrakatoa": "ThinkboxKrakatoa",
            "ThinkBoxSequoia": "ThinkboxSequoia",
            "ThinkBoxStoke": "ThinkboxStoke",
            "ThinkBoxXMesh": "ThinkboxXMesh"
        }
    },
    "EndUserComputing": {
        "REPLACED": {
            "WorkSpacesWorkSpacesWeb": "WorkSpacesWeb"
        }
    },
    "ManagementGovernance": {
        "REPLACED": {
            "ManagedServiceforGrafana": "ManagedGrafana"
        }
    },
    "SecurityIdentityCompliance": {
        "REPLACED": {
            "IdentityAccessManagementAWSIAMAccessAnalyzer": "IdentityAccessManagementIAMAccessAnalyzer",
            "SingleSignOn": "IAMIdentityCenter"
        }
    },
    "Storage": {
        "REPLACED": {
            "BackupAWSBackupSupportforVMwareWorkloads": "BackupAWSBackupsupportforVMwareWorkloads"
        }
    }
}

BREAKING_CHANGES["v15.0"] = {
    "Compute": {
        "REMOVED": [
            "EC2R5dInstance",
            "EC2RdnInstance"
        ]
    },
    "Containers": {
        "REPLACED": {
            "RedHatOpenShift": "RedHatOpenShiftServiceonAWS"
        }
    },
    "Database": {
        "REMOVED": [
            "QuantumLedgerDatabase2"
        ]
    },
    "EndUserComputing": {
        "REPLACED": {
            "WorkSpaces": "WorkSpacesFamilyAmazonWorkSpaces",
            "WorkSpacesWeb": "WorkSpacesFamilyAmazonWorkSpacesWeb"
        }
    },
    "GameTech": {
        "RENAMED": "Games"
    },
    "Storage": {
        "REPLACED": {
            "CloudEndureDisasterRecovery": "ElasticDisasterRecovery"
        }
    }
}

BREAKING_CHANGES["v16.0"] = {
    "Analytics": {
        "REPLACED": {
            "KinesisFirehose": "KinesisDataFirehose"
        }
    },
    "BusinessApplications": {
        "REMOVED": [
            "ChimeVoiceConnector"
        ]
    },
    "Compute": {
        "REMOVED": [
            "ApplicationAutoScaling",
            "Fargate2"
        ]
    },
    "Containers": {
        "REMOVED": [
            "ElasticContainerServiceECSAnywhere"
        ]
    },
    "Games": {
        "REMOVED": [
            "Lumberyard"
        ]
    },
    "General": {
        "REPLACED": {
            "MarketplaceLight": "Marketplace",
            "MarketplaceDark": "Marketplace"
        }
    },
    "ManagementGovernance": {
        "REPLACED": {
            "PersonalHealthDashboard": "HealthDashboard"
        }
    },
    "MigrationTransfer": {
        "REMOVED": [
            "ServerMigrationService"
        ]
    },
    "NetworkingContentDelivery": {
        "REMOVED": [
            "CloudDirectory2",
            "CloudWANVirtualPoP"
        ]
    },
    "VRAR": {
         "RENAMED": None # Deleted
    }

}

BREAKING_CHANGES["v17.0"] = {
    "Analytics": {
        "REPLACED": {
            "KinesisDataAnalytics": "ManagedServiceforApacheFlink"
        }
    },
    "InternetOfThings": {
        "REMOVED": [
            "IoTEduKit"
        ]
    },
    "MachineLearning": {
        "REPLACED": {
            "Omics": "HealthOmics"
        }
    }
}

BREAKING_CHANGES["v18.0"] = {}

BREAKING_CHANGES["v19.0"] = {
    "ApplicationIntegration": {
        "MOVED": {
            "APIGateway": "NetworkingContentDelivery",
            "APIGatewayEndpoint": "NetworkingContentDelivery",
            "ConsoleMobileApplication": "ManagementGovernance"
        }
    },
    "Analytics": {
        "REPLACED": {
            "KinesisDataFirehose": "DataFirehose"
        }
    },
    "BusinessApplications": {
        "REMOVED": [
            "Honeycode"
        ]
    },
    "Compute": {
        "MOVED": {
            "ComputeOptimizer": "ManagementGovernance",
            "ThinkboxDeadline": "MediaServices",
            "ThinkboxFrost": "MediaServices",
            "ThinkboxKrakatoa": "MediaServices",
            "ThinkboxStoke": "MediaServices",
            "ThinkboxXMesh": "MediaServices"
        },
        "REMOVED": [
            "GenomicsCLI",
            "VMwareCloudonAWS",
            "ThinkboxSequoia"
        ]
    },
    "EndUserComputing": {
        "REPLACED": {
            "AppStream": "AppStream2",
            "WorkSpacesFamilyAmazonWorkSpacesWeb": "WorkSpacesFamilyAmazonWorkSpacesSecureBrowser"
        },
        "REMOVED": [
            "WorkLink"
        ]
    },
    "InternetOfThings": {
        "REMOVED": [
            "IoTThingsGraph"
        ]
    },
    "ManagementGovernance": {
        "MOVED": {
            "FaultInjectionSimulator": "DeveloperTools"
        },
        "REPLACED": {
            "FaultInjectionSimulator": "FaultInjectionService"
        }
    },
    "MachineLearning": {
        "RENAMED": "ArtificialIntelligence",
        "REPLACED": {
            "TorchServe": "PyTorchonAWS"
        }
    },
    "MigrationTransfer": {
        "RENAMED": "MigrationModernization"
    },
    "Storage": {
        "REPLACED": {
            "SimpleStorageServiceBucket": "SimpleStorageServiceGeneralpurposebucket",
        },
        "REMOVED": [
            "Snowmobile"
        ]
    }
}

ICON_CHANGES = {}
ICON_CHANGE_SET = set()

def process_icon_changes():
    """
    Process icon renames and removals
    """

    for version in BREAKING_CHANGES:
        tmp = {}
        for category in BREAKING_CHANGES[version]:
            if "REPLACED" in BREAKING_CHANGES[version][category]:
                for key, value in BREAKING_CHANGES[version][category]["REPLACED"].items():
                    tmp[key] = value
                    ICON_CHANGE_SET.add(key)
            if "REMOVED" in BREAKING_CHANGES[version][category]:
                for key in BREAKING_CHANGES[version][category]["REMOVED"]:
                    tmp[key] = None
                    ICON_CHANGE_SET.add(key)

        ICON_CHANGES[version] = tmp

class IncludePatternManager:
    def __init__(self, define: str = "AWSPuml"):
        self.include_define = define
        self.update_include_pattern()

    def update_include_pattern(self):
        self.include_pattern = rf"!include(url)? {self.include_define}/(?P<category>.+)/(?P<icon>.+).puml"

pattern_manager = IncludePatternManager()

def process_include(line: str, upgrade_versions: List[str]) -> str:
    """
    Process lines with !include statements

    :param line: line to process
    :type line: str
    :param upgrade_versions: list of versions to process
    :type upgrade_versions: List[str]
    :return: processed line
    :rtype: str
    """
    processed = False
    processed_line = None
    match = re.search(pattern_manager.include_pattern, line)
    if match:
        category = match.group("category")
        icon = match.group("icon")

        processed = False
        removed = False
        for version in upgrade_versions:
            if category in BREAKING_CHANGES[version]:
                if "RENAMED" in BREAKING_CHANGES[version][category]:
                    new_category = BREAKING_CHANGES[version][category]["RENAMED"]
                    processed = True
                    if new_category is None:
                        removed = True
                    else:
                        category = new_category

            # category may have changed, check again
            if category in BREAKING_CHANGES[version]:
                if "MOVED" in BREAKING_CHANGES[version][category]:
                    if icon in BREAKING_CHANGES[version][category]["MOVED"]:
                        processed = True
                        category = BREAKING_CHANGES[version][category]["MOVED"][icon]

            # category may have changed, check again
            if category in BREAKING_CHANGES[version]:
                if icon == "all":
                    pass
                elif "REPLACED" in BREAKING_CHANGES[version][category]:
                    if icon in BREAKING_CHANGES[version][category]["REPLACED"]:
                        processed = True
                        icon = BREAKING_CHANGES[version][category]["REPLACED"][icon]
                elif "REMOVED" in BREAKING_CHANGES[version][category]:
                    if icon in BREAKING_CHANGES[version][category]["REMOVED"]:
                        processed = True
                        removed = True

            if processed:
                processed_line = f"!include {pattern_manager.include_define}/{category}/{icon}.puml\n"
            if removed:
                # category/icon removed, comment out line
                return "' " + processed_line.replace("\n", f" ' removed in {version}\n")

    return processed_line


process_icon_changes()
FLAT_ICON_CHANGES = "|".join(str(item) for item in ICON_CHANGE_SET)

# For any given ResourceIcon
# Look for:
# - sprite $ResourceIcon
# - image $ResourceIconIMG(
# - macro ResourceIcon(
icon_pattern = fr"\b(?:$)?(?P<icon>{FLAT_ICON_CHANGES})(?:IMG\(|\(|\b)"

def process_line(line: str, upgrade_versions: List[str]) -> str:
    """
    Process lines with ResourceIcon references

    :param line: The line to process
    :type line: str
    :param upgrade_versions: The versions to upgrade
    :type upgrade_versions: List[str]
    :return: The processed line
    :rtype: str
    """
    processed = False
    matches = re.findall(icon_pattern, line)
    if matches:
        for icon in matches:
            for version in upgrade_versions:
                if icon in ICON_CHANGES[version]:
                    replacement = ICON_CHANGES[version][icon]
                    if replacement is not None:
                        if line.find(f"${icon}IMG(") > -1:
                            processed = True
                            line = line.replace(f"${icon}IMG(", f"${replacement}IMG(")
                        elif line.find(f"${icon}") > -1:
                            processed = True
                            line = line.replace(f"${icon}", f"${replacement}")
                        elif line.find(f"{icon}") > -1:
                            processed = True
                            line = line.replace(f"{icon}", f"{replacement}")

    matches = re.findall(update_pattern, line)
    if matches:
        for macro in matches:
            replacement = UPDATES[macro]
            if replacement is not None:
                # TODO - need a better way to avoid matches starting with $
                # otherwise finds a AWS_BG_COLOR match for $AWS_BG_COLOR
                if line.find(f"${macro}") == -1:
                    processed = True
                    line = line.replace(macro, replacement)

    if processed:
        return line
    else:
        return None


def process_file(output_file: str) -> List[str]:
    """
    Process the PlantUML file
    Return the lines to be written to the file
    
    :param output_file: The PlantUML file to process
    :type output_file: str
    :return: The lines to be written to the file
    :rtype: List[str]
    """
    line_number = 0
    overwrite_lines: List[str] = []
    detected_version = None
    detected_define = None
    upgrade_versions = []
    awspuml_pattern = r"!define (.+) https:\/\/raw.githubusercontent.com\/awslabs\/aws-icons-for-plantuml\/(.+)\/dist"

    # Open the file in read mode
    with open(output_file, 'r') as file:
        # Iterate over each line in the file
        for line in file:
            line_number += 1
            # Process the line
            if detected_version:
                if line.startswith("!include"):
                    processed_line = process_include(line, upgrade_versions)
                    if processed_line is not None:
                        print(f"⏹️  {line_number:>3}: {line}", end="")
                        line = processed_line
                        print(f"🔄 {line_number:>3}: {line}", end="")

                else:
                    processed_line = process_line(line, upgrade_versions)
                    if processed_line is not None:
                        print(f"⏹️  {line_number:>3}: {line}", end="")
                        line = processed_line
                        print(f"🔄 {line_number:>3}: {line}", end="")

            elif (line.startswith("!define ")):
                match = re.search(awspuml_pattern, line)
                if match:
                    detected_define = match.group(1)
                    detected_version = match.group(2)
                    if detected_define != "AWSPuml":
                        pattern_manager.include_define = detected_define
                        pattern_manager.update_include_pattern()
                    
                    print(f"⏹️  {line_number:>3}: {line}", end="")
                    line = line.replace(detected_version, SUPPORTED_VERSIONS[-1])
                    print(f"🔄 {line_number:>3}: {line}", end="")
                    if detected_version not in SUPPORTED_VERSIONS:
                        print(f"aws-icons-for-plantuml version {detected_version} not in {SUPPORTED_VERSIONS}")
                        return None
                    
                    version_index = SUPPORTED_VERSIONS.index(detected_version)
                    upgrade_versions = SUPPORTED_VERSIONS[version_index:]

            overwrite_lines.append(line)

    return overwrite_lines


parser = argparse.ArgumentParser(description="Upgrade AWS Icons for PlantUML references")
parser.add_argument(
    "--overwrite",
    action="store_true",
    default=False,
    help="Overwrite PlantUML file",
)
parser.add_argument('filename', help='The PlantUML filename or wildcard in quotes (e.g. "*.puml")')

args = vars(parser.parse_args())

def main():
    overwrite = False
    if args["overwrite"]:
        overwrite = True

    filename_arg = args["filename"]
    puml_files = glob.glob(filename_arg)
    for output_file in puml_files:
        print(f"processing {output_file} ...")
        if not os.path.isfile(output_file):
            print(f"File '{output_file}' not found")
            continue

        updated_lines = process_file(output_file)
        if updated_lines is None:
            print("No changes detected")
        elif overwrite:
            with open(output_file, 'w') as file:
                for line in updated_lines:
                    file.write(line)


if __name__ == "__main__":
    main()
