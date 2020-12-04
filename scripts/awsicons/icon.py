# Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT (For details, see https://github.com/awslabs/aws-icons-for-plantuml/blob/master/LICENSE)
"""
Modules to support creation of PlantUML icon files
"""

import sys
import re
import subprocess
import tempfile
from subprocess import PIPE
from pathlib import Path

PUML_LICENSE_HEADER = """' Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
' SPDX-License-Identifier: CC-BY-ND-2.0 (For details, see https://github.com/awslabs/aws-icons-for-plantuml/blob/master/LICENSE)
"""


class Icon:
    """Reference to source SVG and methods to create the PUML icons"""

    def __init__(self, posix_filename=None, config=None):
        self.filename = posix_filename
        self.config = config
        self.source_name = None
        self.category = None
        self.target = None
        self.color = None

        # If config provided, this contains the tracked categories, and is used set the other values
        # for the object.
        # If no config provided, used to access internal methods only
        if self.filename and self.config:
            # Source name and category to uniquely identify same file names
            # in different categories to apply color or other values

            # Source filename only without directory
            self.source_name = str(posix_filename).split("/")[-1]
            # self.source_name = str(posix_filename).split("/")[-1].split("_")[1]

            # For category, strip leading "Arch_" and then all not alphanumeric
            # examples:
            # Arch_Database -> Database
            # Arch_Developer- Tools -> DeveloperTools (the dash and included space)
            # Arch_End-User-Computing -. EndUserComputing
            self.source_category = re.sub(
                r"\W+", "", str(posix_filename).split("/")[-3].split("_")[1]
            )
            # self.source_category = str(posix_filename).split("/")[-3].split("_")[1]
            # self.source_category = re.sub(
            #     r"\W+", "", str(posix_filename).split("/")[-3].split("_")[1]
            # )
            self._set_values(self.source_name, self.source_category)

    def generate_image(self, path, color=True, max_target_size=64, transparency=False):
        """Create image from SVG file and save full color without transparency to path"""
        temp_name = Path(
            tempfile._get_default_tempdir() + next(tempfile._get_candidate_names())
        )

        # Call batik to generate the PNG from SVG
        try:
            source = self.filename
            color = self.color
            print(str(source))
            result = subprocess.run(
                [
                    "java",
                    "-jar",
                    "batik-1.13/batik-rasterizer-1.13.jar",
                    "-d",
                    f"{str(path)}/{self.target}.png",
                    "-w",
                    str(max_target_size),
                    "-h",
                    str(max_target_size),
                    "-m",
                    "image/png",
                    str(source),
                ],
                shell=False,
                stdout=PIPE,
                stderr=PIPE,
            )
        except Exception as e:
            print(f"Error executing batik-rasterizer jar file, {e}")
            sys.exit(1)
        return

    def generate_puml(self, path):
        """Generate puml file for service"""
        puml_content = PUML_LICENSE_HEADER
        # Start plantuml.jar and encode sprite from main PNG
        try:
            target = self.target
            color = self.color
            result = subprocess.run(
                [
                    "java",
                    "-jar",
                    "./plantuml.jar",
                    "-encodesprite",
                    "16z",
                    f"{path}/{target}.png",
                ],
                shell=False,
                stdout=PIPE,
                stderr=PIPE,
            )
            puml_content += result.stdout.decode("UTF-8")
            puml_content += f"AWSEntityColoring({target})\n"
            puml_content += f"!define {target}(e_alias, e_label, e_techn) AWSEntity(e_alias, e_label, e_techn, {color}, {target}, {target})\n"
            puml_content += f"!define {target}(e_alias, e_label, e_techn, e_descr) AWSEntity(e_alias, e_label, e_techn, e_descr, {color}, {target}, {target})\n"
            puml_content += f"!define {target}Participant(p_alias, p_label, p_techn) AWSParticipant(p_alias, p_label, p_techn, {color}, {target}, {target})\n"
            puml_content += f"!define {target}Participant(p_alias, p_label, p_techn, p_descr) AWSParticipant(p_alias, p_label, p_techn, p_descr, {color}, {target}, {target})\n"

            with open(f"{path}/{target}.puml", "w") as f:
                f.write(puml_content)

        except Exception as e:
            print(f"Error executing plantuml jar file, {e}")
            sys.exit(1)

    # Internal methods
    def _set_values(self, source_name, source_category):
        """Set values if entry found in the config.yml file, otherwise set uncategorized and defaults"""
        for i in self.config["Categories"]:
            for j in self.config["Categories"][i]["Icons"]:
                if j["Source"] == source_name and i == source_category:
                    try:
                        self.category = i
                        self.target = j["Target"]

                        # Set color from service, category, default then black
                        if "Color" in j:
                            self.color = self._color_name(j["Color"])
                        elif "Color" in i:
                            self.color = self._color_name(i["Color"])
                        elif "Color" in self.config["Defaults"]["Category"]:
                            self.color = self._color_name(
                                self.config["Defaults"]["Category"]["Color"]
                            )
                        else:
                            print(
                                f"No color definition found for {source_name}, using black"
                            )
                            self.color = "#000000"
                        return
                    except KeyError as e:
                        print(f"Error: {e}")
                        print(
                            "config.yml requires minimal config section, please see documentation"
                        )
                        sys.exit(1)
                    except TypeError as e:
                        print(f"Error: {e}")
                        print(
                            "config.yml requires Defaults->Color definition, please see documentation"
                        )
                        sys.exit(1)

        # Entry not found, place into uncategorized
        try:
            self.category = "Uncategorized"
            self.target = self._make_name(self.source_name)
            self.color = self.config["Defaults"]["Category"]["Color"]
        except KeyError as e:
            print(f"Error: {e}")
            print(
                "config.yml requires minimal config section, please see documentation"
            )
            sys.exit(1)

    def _make_name(self, name=None):
        """
            Create PUML friendly name short name without directory and strip leading Arch_ or Res_
            and trailing _48.svg, then remove leading AWS or Amazon to reduce length.
            
            Strip non-alphanumeric characters.

            The name input should be a complete filename (e.g., Arch_foo_48.svg)   
        """

        # Source name ex: Arch_AWS-Storage-Gateway_48.svg, we want "Storage-Gateway"
        if name:
            # If a service (starts with Arch_)
            if name.startswith("Arch_"):
                # new_name = name.split("/")[-1].split("_light-bg@")[0]
                new_name = name.split("_")[1]
            elif name.startswith("Res_"):
                # ex: Res_Amazon-Simple-Storage_VPC-Access-Points_48_Light.svg -> SimpleStorageVPCAccessPoints
                # strip Res_ and _48_Light.svg
                new_name = name.split("_", 1)[1].split("_48_Light.svg")[0]
            else:
                # Name already stripped of unneeded text
                new_name = name
            if new_name.startswith(("AWS-", "Amazon-")):
                new_name = new_name.split("-", 1)[1]
            # Replace non-alphanumeric with underscores (1:1 mapping)
            new_name = re.sub(r"[^a-zA-Z0-9]", "", new_name)

        return new_name

    def _color_name(self, color_name):
        """Returns hex color for provided name from config Defaults"""
        try:
            for color in self.config["Defaults"]["Colors"]:
                if color == color_name:
                    return self.config["Defaults"]["Colors"][color]
            print(
                f"ERROR: Color {color_name} not found in default color list, returning Black"
            )
            return "#000000"
        except KeyError as e:
            print(f"Error: {e}")
            print(
                "config.yml requires minimal config section, please see documentation"
            )
            sys.exit(1)

    # def _remove_transparency(self, im, bg_colour=(255, 255, 255)):
    #     """remove transparency from image and background color, default white"""
    #     # Only process if image has transparency (http://stackoverflow.com/a/1963146)
    #     if im.mode in ("RGBA", "LA") or (im.mode == "P" and "transparency" in im.info):
    #         # Need to convert to RGBA if LA format due to a bug in PIL (http://stackoverflow.com/a/1963146)
    #         alpha = im.convert("RGBA").split()[-1]
    #         bg = Image.new("RGBA", im.size, bg_colour + (255,))
    #         bg.paste(im, mask=alpha)
    #         return bg
    #     else:
    #         return im
