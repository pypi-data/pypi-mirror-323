#!/usr/bin/env python

import json
import os

from PIL import Image

THEME_SUFFIX = "-color-theme.json"
THEME_SNAPSHOT_SUFFIX = "-snapshot.jpg"

def write_json_file(json_file_path, content):
    """
    write the content to the json file
    """
    with open(json_file_path, 'w', encoding='utf-8') as f:
        json.dump(content, f, ensure_ascii=False, indent=4)

def save_image(img, output_dir, name):
    """
    Saves the image to a specified directory with a given name.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    img.save(os.path.join(output_dir, f"{name}{THEME_SNAPSHOT_SUFFIX}"))


def load_json_file(json_file_path):
    """
    Loads the JSON file at the specified path.
    """
    with open(json_file_path, "r", encoding="utf-8") as file:
        json_data = json.load(file)
        return json_data


def dump_json_file(json_file_path, json_data, indent=2):
    """
    Writes the given JSON data to a file at the specified path.
    """
    with open(json_file_path, "w", encoding="utf-8") as f:
        json.dump(json_data, f, indent=indent)


def load_theme_data(theme_name):
    """Load theme data from the theme json file."""
    assert not theme_name.endswith(
        THEME_SUFFIX
    ), f"Invalid theme name: {theme_name}. It should not end with {THEME_SUFFIX}. Valid theme name example: viiv-dark."
    theme_name = theme_name.lower()
    root_path = os.getcwd() + os.sep
    theme_path = root_path + "themes" + os.sep + theme_name + THEME_SUFFIX
    theme_data = load_json_file(theme_path)
    return theme_data


def load_theme_snapshot(theme_name):
    """Load theme snapshot Image from the theme snapshot jpg file.

    Returns:
        Image: The theme snapshot Image
    """
    root_path = os.getcwd() + os.sep
    theme_snapshot_path = (
        root_path + "images" + os.sep + theme_name + THEME_SNAPSHOT_SUFFIX
    )
    theme_snapshot = Image.open(theme_snapshot_path)
    return theme_snapshot


def save_theme_snapshot(theme_name, theme_snapshot: Image):
    """Save theme snapshot Image to the theme snapshot jpg file.

    Args:
        theme_name (str): The theme name.
        theme_snapshot (Image): The theme snapshot Image.
    """
    root_path = os.getcwd() + os.sep
    theme_snapshot_path = (
        root_path + "images" + os.sep + theme_name + THEME_SNAPSHOT_SUFFIX
    )
    theme_snapshot.save(theme_snapshot_path)
    return theme_snapshot_path
