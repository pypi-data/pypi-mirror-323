# coding: utf-8

import argparse
from GDV_feature_shows import __version__


def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="GDV_feature_shows helps to visualize GDV scans. ")

    parser.add_argument("--version", action="version", version=f"V{__version__}", help="Check version. ")

    parser.add_argument("settings_path", type=str, help="Path to json file with settings. "
                                                        "It creates new if does not exists. ")

    return parser.parse_args()
