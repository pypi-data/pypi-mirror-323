# coding: utf-8

import os

from ksupk import mkdir_with_p, get_time_str, gen_random_string, get_files_list
from tqdm import tqdm
import pandas as pd

from GDV_feature_shows.api_client import api_exp_getExpList, extract_text, download_bdf, extract_pictures
from GDV_feature_shows.name_volume import get_feature_names
from GDV_feature_shows.process import fill_all_features
from GDV_feature_shows.feature_extraction import KImage, FeatureExtractor
from GDV_feature_shows import __version__


def get_if_error_file(working_dir: str, logs: list) -> str:
    error_file = os.path.join(working_dir, "error_file.txt")
    with open(error_file, "w", encoding="utf-8") as fd:
        fd.write("Error occurred while processing. Try again or report about it. \n\nLogs:\n")
        fd.write("\n".join(logs))
        fd.flush()
    return error_file


def build_excel(card_item: dict, working_dir: str) -> tuple[str, str]:
    logs = []
    fe = FeatureExtractor()

    card_id, card_name = card_item["id"], card_item["name"]

    # cur_time = get_time_str(template="%y-%m-%d-%H-%M-%S")
    # dir_name = f"{card_id}_{cur_time}_{gen_random_string()}"
    dir_name = f"{card_id}"
    dir_path = os.path.join(working_dir, dir_name)
    mkdir_with_p(dir_path)
    logs += [f"Created directory \"{dir_path}\". "]

    logs += [f"Getting experiments from card \"{card_name}\" ({card_id})... "]
    exps = api_exp_getExpList(int(card_id))
    logs += [f"Getted {len(exps)} experiments"]

    needed_exps, no_needed_exps = [], []
    for i, exp_i in enumerate(exps):
        if exp_i["exptype"] == 8:
            exp_i_id, exp_i_comment = exp_i["id"], extract_text(exp_i["comments"])
            cur_needed_exp = (exp_i_id, exp_i_comment)
            needed_exps.append(cur_needed_exp)
        else:
            no_needed_exps.append(exp_i)
    if len(no_needed_exps) > 0:
        logs += [f"WARNING: There are experiments with exptype != 8 (series). Total count {len(no_needed_exps)} items. "]

    logs += [f"Start downloading bdf files and extracting gdv-pictures from it. "]
    try:
        received_count, cache_count = 0, 0
        gdvs_d: dict[str: tuple] = {}
        gdv_same_exps: dict[int: list[str]] = {}
        # c = 0
        for exp_i in tqdm(needed_exps):
            # c += 1
            # if c > 10:
            #     break
            exp_id = int(exp_i[0])
            exp_comment = exp_i[1]
            if exp_id not in gdv_same_exps:
                gdv_same_exps[exp_id] = []

            exp_parent_dir = os.path.join(dir_path, f"{exp_id}")
            if not os.path.isdir(exp_parent_dir):
                bs = download_bdf(exp_id)
                pics = extract_pictures(bs.decode("utf-8"))
                mkdir_with_p(exp_parent_dir)
                for i, pic_i in enumerate(pics):
                    gdv_name = f"{exp_id}_{i+1}"
                    gdv_path = f"{gdv_name}.png"
                    pic_out_path = os.path.join(exp_parent_dir, gdv_path)
                    with open(pic_out_path, "wb") as fd:
                        fd.write(pic_i)
                        fd.flush()
                    gdvs_d[gdv_name] = (pic_out_path, exp_id, exp_comment, i+1)
                    gdv_same_exps[exp_id].append(gdv_name)
                    cache_count += 1
            else:
                pics = get_files_list(exp_parent_dir)
                for pic_i in pics:
                    pic_out_path = pic_i
                    name = os.path.basename(pic_i)
                    gdv_name, _ = os.path.splitext(name)
                    pic_ex_id, pic_num = name.split("_")
                    gdvs_d[gdv_name] = (pic_out_path, exp_id, exp_comment, pic_num)
                    gdv_same_exps[exp_id].append(gdv_name)
                    received_count += 1
        logs += [f"Total {len(gdvs_d)} gdv-pictures to process ({received_count} received and {cache_count} were in cache). "]
    except Exception as e:
        logs += [f"Error: {e}"]
        return get_if_error_file(working_dir, logs), "\n".join(logs)

    logs += [f"Startings processing images. "]
    problems_pics = []
    try:
        for gdvs_i in tqdm(gdvs_d):
            kimg_i = KImage(gdvs_d[gdvs_i][0]).to_gray()
            kimg_i = kimg_i.crop(*fe.find_crops(kimg_i))
            features_i, feature_filling_errors = fill_all_features(kimg_i)
            gdvs_d[gdvs_i] = gdvs_d[gdvs_i] + (features_i, )  # features_i is 4th
            if len(feature_filling_errors) != 0:
                problems_pics.append(gdvs_i)
    except Exception as e:
        logs += [f"Error: {e}"]
        return get_if_error_file(working_dir, logs), "\n".join(logs)
    logs += [f"ERRORS: while processing some error occurred with gdvs: {problems_pics}"]

    logs += [f"Building sheet/tab 2 in excel document..."]
    data2 = {}
    features_name_map = get_feature_names()
    columns2 = []
    for feature_i in features_name_map:
        if feature_i > 0:
            columns2.append(features_name_map[feature_i])
    for gdvs_i in gdvs_d:
        row_i = []
        features_i = gdvs_d[gdvs_i][4]
        for feature_i in features_name_map:
            if feature_i > 0:
                row_i.append(features_i[feature_i])
        obj_name_i = f"{gdvs_d[gdvs_i][1]}_{gdvs_d[gdvs_i][2]}_{gdvs_d[gdvs_i][3]}"  # {id}_{com}_{num}
        data2[obj_name_i] = row_i
    # data = {'row_1': [3, 2, 1, 0], 'row_2': ['a', 'b', 'c', 'd']}
    # columns = ['A', 'B', 'C', 'D']
    df2 = pd.DataFrame.from_dict(data2, orient="index", columns=columns2)

    logs += [f"Built sheet/tab 2 in excel document -- OK"]

    logs += [f"Building sheet/tab 1 in excel document..."]
    data1 = {}
    for gdv_same_exps_i in gdv_same_exps:
        sames = gdv_same_exps[gdv_same_exps_i]
        row_i = []
        obj_name_i = f"{gdv_same_exps_i}_{gdvs_d[sames[0]][2]}_{len(sames)}"  # {id}_{com}_{num}
        data1[f"{obj_name_i}"] = row_i
    columns1 = []
    for feature_i in features_name_map:
        if feature_i > 0:
            columns1.append(f"{features_name_map[feature_i]} MEAN")
            columns1.append(f"{features_name_map[feature_i]} STD")
            for gdv_same_exps_i in gdv_same_exps:
                sames = gdv_same_exps[gdv_same_exps_i]
                obj_name_i = f"{gdv_same_exps_i}_{gdvs_d[sames[0]][2]}_{len(sames)}"

                values = [gdvs_d[same_i][4][feature_i] for same_i in sames]  # =(
                needed_mean, needed_std  = fe.cal_mean_and_std(values)

                data1[f"{obj_name_i}"].append(needed_mean)
                data1[f"{obj_name_i}"].append(needed_std)

    df1 = pd.DataFrame.from_dict(data1, orient="index", columns=columns1)

    logs += [f"Built sheet/tab 1 in excel document -- OK"]

    cur_time = get_time_str(template="%d-%m-%y_%H-%M")
    out_excel_file_name = f"{cur_time}_{card_name}_V{__version__}.xlsx"
    out_file_name = os.path.join(working_dir, out_excel_file_name)
    logs += [f"Output file name will be: \"{out_excel_file_name}\". "]

    logs += [f"Saving to \"{out_file_name}\". "]
    with pd.ExcelWriter(out_file_name) as writer:
        df1.to_excel(writer, sheet_name="Series combined")
        df2.to_excel(writer, sheet_name="All objects")

    logs_str = "\n".join(logs)
    print(logs_str)
    return out_file_name, logs_str
