# coding: utf-8

import os

from ksupk import restore_json

from GDV_feature_shows.resource_manager import ResourceManager
from GDV_feature_shows.feature_extraction import FeatureExtractor

from GDV_feature_shows.parsing import get_args

# TODO: 2940167 (extra), several peaks. 
# TODO: 2944804, fix noised petals. 
# TODO: except zero pixels, while calculating general parameters.
# TODO: Этот многомасштабный морфологический градиент можно использовать, например, для определения детальности. Если фрагмент высокодетальный, то будет множество переходов/перепадов. Эти перепады можно фиксировать, например, с помощью контурного препарата Собеля (сложить среднюю яркость результата). Но многомасштабный морфологический градиент показывает лучшие результаты в оценке детальности.
# TODO: move all settings to one json file

def main():
    args = get_args()
    FeatureExtractor()
    ResourceManager()
    if args.command == "tk":
        from GDV_feature_shows.interface_tk import App
        app = App(args.gdv_path, args.settings_path)
        app.mainloop()
    elif args.command == "gradio":
        from GDV_feature_shows.interface_gradio import start_gradio_interface
        from GDV_feature_shows.api_client import APISettings, create_api_settings_json, get_setting_name
        client_api_settings = get_setting_name()
        if not os.path.isfile(client_api_settings):
            create_api_settings_json(client_api_settings)
            print(f"Please fill the file \"{client_api_settings}\". And run again. ")
            exit()
        APISettings(client_api_settings)
        start_gradio_interface(args.gdv_path, args.settings_path, args.working_dir, args.inf, args.port, args.share,
                               password=restore_json(client_api_settings)["gradio_inner_funcs_password"])
    else:
        print(f"main: Failed successfully. ")
        exit(-1)


if __name__ == "__main__":
    main()
