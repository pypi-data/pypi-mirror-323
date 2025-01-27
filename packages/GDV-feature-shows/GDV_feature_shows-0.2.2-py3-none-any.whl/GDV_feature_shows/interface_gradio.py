# coding: utf-8

import os
import os.path
import time

import gradio as gr

from ksupk import save_json, restore_json, singleton_decorator, is_float, mkdir_with_p, gen_random_string

from GDV_feature_shows import __version__

from GDV_feature_shows.name_volume import get_settings, get_visualization
from GDV_feature_shows.process import update_feature_extractor_with_settings, fill_visualizations, define_paths
from GDV_feature_shows.feature_extraction import KImage
from GDV_feature_shows.settings_handler import SettingsHandler
from GDV_feature_shows.excel_forming_logic import build_excel
from GDV_feature_shows.api_client import api_cards_getCards


@singleton_decorator
class GradioGL:
    def __init__(self):
        self.filter_text = ""
        self.gdv_path = None
        self.settings_path = None
        self.settings_input_fields = None
        self.viz_names = None
        self.paths = None
        self.cur_index = None
        self.visualisation_entities = None
        self.working_dir = None
        self.cards = None
        self.password = None


class VisualizationEntity:
    def __init__(self):
        self.kimg = None
        self.features = None

    def set_pic(self, kimg: KImage):
        # self.image_label.config(bg=image_color)
        self.kimg = kimg

    def set_features(self, features):
        self.features = features

    def get_kimg_and_features(self):
        return self.kimg, self.features


def update_setting(name: str, value: str):
    print(name, value)
    if is_float(value):
        value = float(value)
        update_feature_extractor_with_settings({name: value})


def set_filter(text: str):
    text = str(text)
    ggl = GradioGL()
    ggl.filter_text = text.strip().lower()


def update_visualisation(viz_name: str, direction: str):
    ggl = GradioGL()

    if direction != "":
        before = ggl.cur_index
        if direction == "next":
            ggl.cur_index = (ggl.cur_index + 1) % len(ggl.viz_names)
        elif direction == "prev":
            ggl.cur_index = (ggl.cur_index - 1) % len(ggl.viz_names)
        else:
            print("update_visualisation: Failed successfully. ")
            exit(-1)

        filtered_text = ggl.filter_text
        if filtered_text != "":
            while (not (filtered_text in ggl.viz_names[ggl.cur_index].lower())
                   and before != ggl.cur_index):
                if direction == "next":
                    ggl.cur_index = (ggl.cur_index + 1) % len(ggl.viz_names)
                elif direction == "prev":
                    ggl.cur_index = (ggl.cur_index - 1) % len(ggl.viz_names)
                else:
                    print("update_visualisation: Failed successfully. ")
                    exit(-1)

    image_path = ggl.paths[ggl.cur_index]
    if direction != "" or ggl.visualisation_entities is None:
        visualization_options = list(get_visualization())
        visualisations = {viz_name_i: VisualizationEntity() for viz_name_i in visualization_options}
        fill_visualizations(image_path, visualisations, 500)
        ggl.visualisation_entities = visualisations

    img, features = ggl.visualisation_entities[viz_name].get_kimg_and_features()
    img = img.get_as_pillow()
    features_res = []
    for feature_i in features:
        features_res.append([feature_i, features[feature_i]])

    return ggl.viz_names[ggl.cur_index], img, features_res


def form_excel(card: str, password: str):
    ggl = GradioGL()
    time.sleep(5)

    if password == ggl.password:
        needed_card_item = None
        for card_item_i in ggl.cards:
            if card == card_item_i["name"]:
                needed_card_item = card_item_i
                break
        out_file_name, logs = build_excel(needed_card_item, ggl.working_dir)
        return out_file_name, logs
    else:
        incorrect_password_file = os.path.join(ggl.working_dir, "incorrect_password.txt")
        if os.path.isfile(incorrect_password_file):
            return incorrect_password_file, "Password is incorrect"
        else:
            with open(incorrect_password_file, "w", encoding="utf-8") as fd:
                fd.write("Inputted password is incorrect. \n")
                fd.flush()
            return incorrect_password_file, "Password is incorrect"


def conveyor_interface():
    # cards = ["Карточка 1", "Карточка 2", "Карточка 3", "...", "Карточка N"]
    ggl = GradioGL()
    ggl.cards = api_cards_getCards()
    card_names = [card_i["name"] for card_i in ggl.cards]
    with gr.Row():
        gr.Markdown("""
        # Формирование excel-документа
        """)
    with gr.Row():
        password_input = gr.Textbox(label="Пароль", placeholder="")
        file_output = gr.File(label="Сформированный excel-файл")
    with gr.Row():
        cards_dropdown = gr.Dropdown(choices=card_names, value=card_names[0], label="Выбор карточки")
        start_excel_button = gr.Button("Сформировать excel документ")
    with gr.Row():
        gr.Markdown("""
                На весь процесс может уйти много времени (зависит от количество изображений):
                - На скачивания нужных эксперементов из базы данных (если их нет в кэше);
                - На парсинг BDF файлов и извлечение из них изображений (если их нет в кэше);
                - На формирование датасета изображений;
                - На извлечение каждого признака из каждого изображение (если их нет в кэше);
                - Объединение по группам эксперементов и подсчёт средних значений и разбросов;
                - На формирование итогового excel-документа.
                """)
        logs_text = gr.Text(value=f"", label="logs", interactive=False)
    start_excel_button.click(fn=lambda x1, x2: form_excel(x1, x2), inputs=[cards_dropdown, password_input],
                      outputs=[file_output, logs_text])


def settings_interface():
    with gr.Row():
        gr.Markdown("""
        # Настройки
        
        Здесь можно изменить гиперпараметры обработчика.
        """)
    ggl = GradioGL()
    settings = SettingsHandler().get_image_processor_settings()

    ggl.settings_input_fields = {}
    for setting_i in settings:
        with gr.Row():
            gr.Text(value=setting_i, interactive=False)
            ggl.settings_input_fields[setting_i] = gr.Textbox(label="Числовое выражение", placeholder=f"{settings[setting_i]}")
            ggl.settings_input_fields[setting_i].submit(fn=lambda x: update_setting(f"{setting_i}", x),
                                                        inputs=[ggl.settings_input_fields[setting_i]])


def visualisation_interface():
    ggl = GradioGL()

    items, paths = define_paths(ggl.gdv_path)
    ggl.viz_names = items
    ggl.paths = paths
    ggl.cur_index = 0
    visualisation_names = get_visualization()
    with gr.Row():
        gdv_file_name = gr.Text(value="", label="Название", interactive=False)
        filter_input = gr.Textbox(label="Фильтр", placeholder="")
        viz_dropdown = gr.Dropdown(choices=visualisation_names, value=visualisation_names[0], label="Группа параметров")
        prev_button = gr.Button("⬅️")
        next_button = gr.Button("➡️")
    with gr.Row():
        img_output = gr.Image(type="pil", label="Визуализация")
        table_output = gr.Dataframe(headers=["Название признака", "Значение"],
                                    label="Характеристики", wrap=True, column_widths=["70%", "30%"], interactive=False)

    prev_button.click(fn=lambda x: update_visualisation(x, "prev"), inputs=[viz_dropdown], outputs=[gdv_file_name, img_output, table_output])
    next_button.click(fn=lambda x: update_visualisation(x, "next"), inputs=[viz_dropdown], outputs=[gdv_file_name, img_output, table_output])
    viz_dropdown.change(fn=lambda x: update_visualisation(x, ""), inputs=[viz_dropdown], outputs=[gdv_file_name, img_output, table_output])
    filter_input.change(fn=lambda x: set_filter(x), inputs=[filter_input])


def start_gradio_interface():
    ggl = GradioGL()
    sh = SettingsHandler()

    ggl.gdv_path = sh.get_gdv_path()
    ggl.working_dir = sh.get_conveyor_working_dir_path()
    mkdir_with_p(ggl.working_dir)
    ggl.password = sh.get_gradio_inner_funcs_password()

    with gr.Blocks() as demo:
        gr.Text(value=f"Version: V{__version__}", label="", interactive=False)
        with gr.Tabs():
            with gr.Tab("Visualisation"):
                visualisation_interface()
            with gr.Tab("Settings"):
                settings_interface()
            with gr.Tab("Conveyor"):
                conveyor_interface()

    connection_settings = sh.get_inf_and_port_and_share()
    demo.launch(server_name=connection_settings[0], server_port=connection_settings[1], share=connection_settings[2])
