# coding: utf-8

import os

from ksupk import restore_json

from GDV_feature_shows.resource_manager import ResourceManager
from GDV_feature_shows.feature_extraction import FeatureExtractor
from GDV_feature_shows.settings_handler import SettingsHandler

from GDV_feature_shows.parsing import get_args
from GDV_feature_shows.interface_gradio import start_gradio_interface
from GDV_feature_shows.api_client import APISettings


# TODO: 2940167 (extra), several peaks. 
# TODO: 2944804, fix noised petals. 
# TODO: except zero pixels, while calculating general parameters.
# TODO: Этот многомасштабный морфологический градиент можно использовать, например, для определения детальности. Если фрагмент высокодетальный, то будет множество переходов/перепадов. Эти перепады можно фиксировать, например, с помощью контурного препарата Собеля (сложить среднюю яркость результата). Но многомасштабный морфологический градиент показывает лучшие результаты в оценке детальности.


def main():
    args = get_args()
    FeatureExtractor()
    ResourceManager()
    sh = SettingsHandler(args.settings_path)

    APISettings(sh.get_api_settings())

    start_gradio_interface()


if __name__ == "__main__":
    main()
