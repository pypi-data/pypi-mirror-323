# coding: utf-8

import os
import time
from ksupk import singleton_decorator, restore_json, save_json

@singleton_decorator
class SettingsHandler:
    def __init__(self, json_settings_path: str):
        self.path = json_settings_path
        if os.path.isfile(self.path):
            self.d = restore_json(self.path)
            if self.bool_from_str(self.d["IsTemplate"]):
                print(f"Fill file \"{self.path}\" and restart. Dont forget change \"IsTemplate\" to \"False\". Exiting. ")
                time.sleep(5)
                exit()
        else:
            self.create_template()
            print(f"Fill file \"{self.path}\" and restart. Dont forget change \"IsTemplate\" to \"False\". Exiting. ")
            time.sleep(5)
            exit()

    def get_gdv_path(self) -> str:
        return self.d["Global"]["gdv_path"]

    def get_conveyor_working_dir_path(self) -> str:
        return self.d["Global"]["conveyor_working_dir_path"]

    def get_inf_and_port_and_share(self) -> tuple[str, int, bool]:
        return self.d["Global"]["inf"], int(self.d["Global"]["port"]), self.bool_from_str(self.d["Global"]["share"])

    def get_gradio_inner_funcs_password(self) -> str:
        return self.d["Global"]["gradio_inner_funcs_password"]

    def get_excel_forming_log_file_path(self):
        return self.d["Global"]["excel_forming_log_file_path"]

    def get_image_processor_settings(self) -> dict[str: int, ...]:
        return self.d["ImageProcessor"].copy()

    def set_and_save_image_processor_settings(self, d: dict[str: int, ...]):
        for key_i in d:
            self.d["ImageProcessor"][key_i] = d[key_i]
        save_json(self.path, self.d)

    def get_api_settings(self) -> dict:
        return self.d["API"].copy()

    def bool_from_str(self, bool_text: str) -> bool:
        bool_text = bool_text.strip().lower()
        if bool_text in ["true", "t", "1"]:
            return True
        elif bool_text in ["false", "f", "0"]:
            return False
        else:
            raise ValueError(f"{bool_text} is not True or False")

    def create_template(self):
        d = {
            "IsTemplate": "True",
            "Global": {
                "gdv_path": "/path/to/folder/with/pictures/of/GDV/scans",
                "conveyor_working_dir_path": "/path/to/conveyor/working/dir",
                "inf": "127.0.0.1",
                "port": "7860",
                "share": "False",
                "gradio_inner_funcs_password": "{YOUR_PASSWORD}",
                "excel_forming_log_file_path": "/path/to/excel/forming/log/file",
            },
            "ImageProcessor": {
                "Inner circle threshold": 120,
                "Outer circle threshold": 20,
                "Findings petal threshold": 120,
                "Noise threshold": 80,
            },
            "API": {
                "login": "",
                "password": "",
                "info_url": "http://*/epc/rpc.php",
                "data_url": "http://*/epc/expget.php",
                "key_parts": ["0x00", "0x00", "...", "0x00"],
            },
        }
        save_json(self.path, d)
