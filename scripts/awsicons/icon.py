# Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT (For details, see https://github.com/awslabs/aws-icons-for-plantuml/blob/main/LICENSE)
"""
Modules to support creation of PlantUML icon files
"""

import shutil
import sys
import re
import subprocess
import tempfile
from subprocess import PIPE
from pathlib import Path
from lxml import etree
import base64
from PIL import Image, ImageOps

PUML_LICENSE_HEADER = """' Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
' SPDX-License-Identifier: CC-BY-ND-2.0 (For details, see https://github.com/awslabs/aws-icons-for-plantuml/blob/main/LICENSE)
"""


class Icon:
    """Reference to source SVG or PNG and methods to create the PUML icons"""

    def __init__(
        self,
        posix_filename=None,
        config=None,
        category_regex=None,
        filename_regex=None,
        category_mappings=None,
        filename_mappings=None,
    ):

        # Full path and filename as PosixPath
        self.filename = posix_filename
        self.filename_dark = None
        # Config filename
        self.config = config
        # Full filename without path
        self.source_name = None
        # Skip Icon generation (used for some groups)
        self.skip_icon = False
        # Category for icon to be associated
        self.category = None
        # Name for PUML removing _, -, etc // called by self._set_values()
        self.target = None
        # Color to apply to icon (web hex)
        self.color = None
        # Icon size
        self.target_size = 64
        # Should icon be transparent
        self.transparency = False
        # Group configuration
        self.group = False
        self.group_border_style = None
        self.group_label = ""
        # Regex patterns to extract category and filename from full POSIX path, and category remappings
        # to enforce consistency between source icon directories
        self.category_regex = category_regex
        self.filename_regex = filename_regex
        self.category_mappings = category_mappings
        self.filename_mappings = filename_mappings

        # Regex patterns to use category and _make_name

        # If config provided, this contains the tracked categories, and is used set the other values
        # for the object.
        # If config and name not provided, used to access internal methods only
        if self.filename and self.config:
            # .touch files are special placeholders for iconless groups
            if str(self.filename).endswith('.touch'):
                self.skip_icon = True
            # Source filename only without directory
            self.source_name = str(self.filename).split("/")[-1]
            # temp category to pass through and set (actual value could be Uncategorized)
            self.temp_category = self._make_category(
                regex=self.category_regex,
                filename=str(self.filename),
                mappings=self.category_mappings,
            )
            self._set_values(self.source_name, self.temp_category)

    def crop_category_image(self, image_filename, png_filename):
        img = Image.open(image_filename)

        # should be 72x72
        width, height = img.size
        
        pngimg = img.crop((7, 7, 67, 67))

        ImageOps.expand(pngimg, border=2, fill='#879196').save(png_filename)

    def generate_image(self, path, color=None, max_target_size=64, transparency=False, gradient=True, image_filename=None, dark=False):
        """Create image from SVG file and save full color without transparency to path"""

        if image_filename == None:
            image_filename = self.filename
        png_filename = self.target
        if dark:
            png_filename = png_filename + "_Dark"

        # copy file to another location
        if str(image_filename).endswith(".png"):
            print(f"Copying {image_filename} to {str(path)}/{png_filename}.png")

            if str(self.source_name).startswith("Arch-Category"):
                self.crop_category_image(image_filename, f"{str(path)}/{png_filename}.png")
            else:
                shutil.copyfile(image_filename, f"{str(path)}/{png_filename}.png")
            return

        # PlantUML only supports 16 layers of gray causing banding when applying to the
        # resource and category icons that have a finer gradient applied. This needs to be replaced
        # with a constant background color for the source PNG file before conversion to sprites.

        # Parse for id's that indicate service or category and replace with color fill.
        # If id is for a resource, no changes needed. Save to a temp SVG file.

        ns = {"s": "http://www.w3.org/2000/svg"}
        white_rect = etree.Element("rect", width="100%", height="100%", fill="white")
        color_rect = etree.Element(
            "rect", width="100%", height="100%", fill=f"{self.color}"
        )
        parser = etree.XMLParser(remove_blank_text=True)

            
        root = etree.parse(str(image_filename), parser)

        if gradient == True:
            # Replace any gradient fills with the requisite color
            # This was in effect for 2021.01.31 Category icons
            elements = root.xpath('//*[@fill="url(#linearGradient-1)"]')
            for elem in elements:
                elem.attrib["fill"] = self.color

        if transparency == False:
            # For resource or category icons which are transparent, set fill to white
            # TODO - can we query without namespaces?
            elem = root.xpath(
                '//s:g[starts-with(@id, "Icon-Resource")]',
                namespaces=ns,
            )
            if elem:
                # To set fill, add a rect before any of the paths.
                elem[0].insert(0, white_rect)
            # For category icons, set fill to category color
            elem = root.xpath(
                '//s:g[starts-with(@id, "Icon-Architecture-Category")]',
                namespaces=ns,
            )
            if elem:
                # To set fill, add a rect before any of the paths.
                elem[0].insert(0, color_rect)

        # Call batik to generate the PNG from SVG - replace the fill color with the icon color
        # The SVG files for services use a gradient fill that comes out as gray stepping otherwise
        # https://xmlgraphics.apache.org/batik/tools/rasterizer.html
        try:
            # Create temporary SVG file with etree
            svg_temp = tempfile.NamedTemporaryFile()
            svg_temp.write(etree.tostring(root))
            svg_temp.flush()
            result = subprocess.run(
                [
                    "java",
                    "-jar",
                    "-Djava.awt.headless=true",
                    "batik-1.16/batik-rasterizer-1.16.jar",
                    "-d",
                    f"{str(path)}/{png_filename}.png",
                    "-w",
                    str(max_target_size),
                    "-h",
                    str(max_target_size),
                    "-m",
                    "image/png",
                    svg_temp.name,
                ],
                shell=False,
                stdout=PIPE,
                stderr=PIPE,
            )
            svg_temp.close()
        except Exception as e:
            print(f"Error executing batik-rasterizer jar file, {e}")
            sys.exit(1)
        return

    def generate_images(self, path, color, max_target_size, transparency, gradient):
        self.generate_image(path, color, max_target_size, transparency, gradient, self.filename)
        if self.filename_dark is not None:
            self.generate_image(path, color, max_target_size, transparency, gradient, self.filename_dark, dark=True)

    def generate_puml(self, path, sprite):
        """Generate puml file for service"""
        puml_content = PUML_LICENSE_HEADER
        target = self.target
        color = self.color
        quoted_color = f"\"{color}\"" if color.startswith("#") else color
        group = self.group
        group_border_style = self.group_border_style
        group_label = self.group_label

        puml_content += sprite
        if not self.skip_icon:
            puml_content += f"!function ${target}IMG($scale=1)\n"
            if self.filename_dark != None:
                puml_content += "!if %variable_exists(\"$AWS_DARK\") && ($AWS_DARK == true)\n"
                with open(f"{path}/{target}_Dark.png", "rb") as png_file:
                    encoded_string = base64.b64encode(png_file.read())
                    puml_content += f"!return \"<img data:image/png;base64,{encoded_string.decode()}{{scale=\"+$scale+\"}}>\"\n"
                puml_content += "!else\n"
            with open(f"{path}/{target}.png", "rb") as png_file:
                encoded_string = base64.b64encode(png_file.read())
                puml_content += f"!return \"<img data:image/png;base64,{encoded_string.decode()}{{scale=\"+$scale+\"}}>\"\n"
            if self.filename_dark != None:
                puml_content += "!endif\n"
            puml_content += f"!endfunction\n\n"

        if group:
            puml_content += f"$AWSGroupColoring({target}Group, {quoted_color}, {group_border_style})\n"
            if self.skip_icon:
                # puml_content += f"!define {target}Group(g_alias, g_label=\"{group_label}\") $AWSGroupEntity(g_alias, g_label, {target}Group)\n"
                puml_content += f"!define {target}Group(g_alias, g_label=\"{group_label}\") $AWSDefineGroup(g_alias, g_label, {target}Group)\n"
            else:
                # puml_content += f"!define {target}Group(g_alias, g_label=\"{group_label}\") $AWSGroupEntity(g_alias, g_label, {target}, {target}Group)\n"
                puml_content += f"!define {target}Group(g_alias, g_label=\"{group_label}\") $AWSDefineGroup(g_alias, g_label, {target}, {target}Group)\n"
        else:
            puml_content += f"AWSEntityColoring({target})\n"
            puml_content += f"!define {target}(e_alias, e_label, e_techn) AWSEntity(e_alias, e_label, e_techn, {color}, {target}, {target})\n"
            puml_content += f"!define {target}(e_alias, e_label, e_techn, e_descr) AWSEntity(e_alias, e_label, e_techn, e_descr, {color}, {target}, {target})\n"
            puml_content += f"!define {target}Participant(p_alias, p_label, p_techn) AWSParticipant(p_alias, p_label, p_techn, {color}, {target}, {target})\n"
            puml_content += f"!define {target}Participant(p_alias, p_label, p_techn, p_descr) AWSParticipant(p_alias, p_label, p_techn, p_descr, {color}, {target}, {target})\n"

        with open(f"{path}/{target}.puml", "w") as f:
            f.write(puml_content)

    def generate_puml_sprite(self, path):
        """Generate puml sprite for service"""
        # Start plantuml-mit-1.2023.12.jar and encode sprite from main PNG
        try:
            target = self.target
            result = subprocess.run(
                [
                    "java",
                    "-jar",
                    "-Djava.awt.headless=true",
                    "./plantuml-mit-1.2023.12.jar",
                    "-encodesprite",
                    "16z",
                    f"{path}/{target}.png",
                ],
                shell=False,
                stdout=PIPE,
                stderr=PIPE,
            )
            puml_content = result.stdout.decode("UTF-8")

            return puml_content

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

                        if "SourceDark" in j and "SourceDirDark" in j:
                            self.filename_dark = str(self.filename).replace(j["SourceDir"], j["SourceDirDark"]).replace(j["Source"], j["SourceDark"])

                        if source_name.startswith("Res_"):
                            self.target_size = 48
                            self.transparency = True

                        # Set color from icon, category, default then black
                        if "Color" in j:
                            if j["Color"].startswith( '#' ) or j["Color"].startswith( '$' ):
                                self.color = j["Color"]
                            else:
                                self.color = self._color_name(j["Color"])
                        # check category
                        elif "Color" in self.config["Categories"][i]:
                            self.color = self._color_name(
                                self.config["Categories"][i]["Color"]
                            )
                        elif "Color" in self.config["Defaults"]["Category"]:
                            self.color = self._color_name(
                                self.config["Defaults"]["Category"]["Color"]
                            )
                        else:
                            print(
                                f"No color definition found for {source_name}, using $AWS_FG_COLOR"
                            )
                            self.color = "$AWS_FG_COLOR"

                        if source_category == "Groups":
                            self.group = True

                            group_border_style = self._group_value("BorderStyle", j)

                            if group_border_style != None:
                                self.group_border_style = self._border_style(group_border_style)
                            else:
                                print(
                                    f"No border style definition found for {source_name}, using plain"
                                )
                                self.group_border_style = "plain"

                            group_label = j["Label"]

                            if group_label != None:
                                self.group_label = group_label
                            else:
                                print(
                                    f"No label definition found for {source_name}, using Generic group"
                                )
                                self.group_label = "Generic group"

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
            self.target = self._make_name(
                regex=self.filename_regex,
                filename=str(self.filename),
                mappings=self.filename_mappings,
            )
            self.color = self.config["Defaults"]["Category"]["Color"]
        except KeyError as e:
            print(f"Error: {e}")
            print(
                "config.yml requires minimal config section, please see documentation"
            )
            sys.exit(1)

    def _make_name(self, regex: str, filename: str, mappings: dict):
        """
        Create PUML friendly name short name without directory and strip leading Arch_ or Res_
        and trailing _48.svg, then remove leading AWS or Amazon to reduce length.

        Strip non-alphanumeric characters.

        The name input should be a complete filename (e.g., Arch_foo_48.svg)
        """
        try:
            name = re.search(regex, filename).group(1)
            new_name = re.sub(r"[^a-zA-Z0-9]", "", name)
        except Exception as e:
            print(
                f"Error in extracting icon name from filename. Regex: {regex}, source filename string: {filename}"
            )
            raise SystemExit(1)
        if mappings:
            try:
                new_name = mappings[new_name]
            except KeyError:
                # no match found, existing filename is okay
                pass

        return new_name

    def _make_category(self, regex: str, filename: str, mappings: dict):
        """Create PUML friendly category with any remappings

        :param regex: regular expression to obtain category
        :type regex: str
        :param filename: full filename path
        :type filename: str
        :param mappings: category mapping (incorrect->correct)
        :type mappings: dict
        :return: PUML friendly category name
        :rtype: str
        """
        try:
            category = re.search(regex, filename).group(1)
            friendly_category = re.sub(r"[^a-zA-Z0-9]", "", category)
        except Exception as e:
            print(
                f"Error in extracting category from filename. Regex: {regex}, source filename string: {filename}"
            )
            raise SystemExit(1)
        if mappings:
            try:
                friendly_category = mappings[friendly_category]
            except KeyError:
                # no match found, existing category is okay
                pass
        return friendly_category

    def _color_name(self, color_name):
        """Returns hex color for provided name from config Defaults"""
        try:
            for color in self.config["Defaults"]["Colors"]:
                if color == color_name:
                    return self.config["Defaults"]["Colors"][color]
            print(
                f"ERROR: Color {color_name} not found in default color list, returning $AWS_FG_COLOR"
            )
            return "$AWS_FG_COLOR"
        except KeyError as e:
            print(f"Error: {e}")
            print(
                "config.yml requires minimal config section, please see documentation"
            )
            sys.exit(1)

    def _border_style(self, border_style):
        """Check and Returns valid border style"""

        if border_style.lower() in ['bold', 'dotted', 'dashed', 'plain']:
            return border_style.lower()
        else:
            return 'plain'

    def _group_value(self, key, icon):
        if "Group" in icon and key in icon["Group"]:
            return icon["Group"][key]
        elif "Group" in self.config["Defaults"] and key in self.config["Defaults"]["Group"]:
            return self.config["Defaults"]["Group"][key]
