# coding: utf-8

from ksupk import singleton_decorator, restore_json, save_json
import hashlib
import base64
import hashlib
import random
import requests
from bs4 import BeautifulSoup


@singleton_decorator
class APISettings:

    def __init__(self, settings: dict):
        self.limit = 1000000
        self.d = settings

    def get_login(self) -> str:
        return self.d["login"]

    def get_password(self) -> str:
        return self.d["password"]

    def get_password_md5(self) -> str:
        password = self.d["password"]
        return hashlib.md5(password.encode()).hexdigest()

    def get_info_link(self) -> str:
        return self.d["info_url"]

    def get_data_link(self) -> str:
        return self.d["data_url"]

    def get_limit(self) -> int:
        return self.limit

    def get_key_parts(self) -> list:
        a = self.d["key_parts"]
        a = [int(part_i, 16) for part_i in a]
        return a


def rpc_request(url, method, params) -> dict:
    headers = {"Content-Type": "application/json"}
    payload = {"jsonrpc": "2.0", "id": 1, "method": method, "params": params}
    response = requests.post(url, headers=headers, json=payload)
    return response.json()


def generate_logindata_hight() -> str:
    ss = APISettings()
    return generate_logindata(ss.get_login(), ss.get_password())


def generate_logindata(login, password) -> str:
    ss = APISettings()
    key_parts = ss.get_key_parts()
    s = f"{login}|||{hashlib.md5(password.encode()).hexdigest()}|||biowell"
    text = bytes([random.randint(0, 255)]) + b"AA" + s.encode()
    last_char = 0
    for i in range(len(text)):
        text = text[:i] + bytes([text[i] ^ key_parts[i % 8] ^ last_char]) + text[i+1:]
        last_char = text[i]
    return base64.b64encode(b"\x03\x02" + text).decode()


def api_user_getInfo() -> dict:
    ss = APISettings()
    server_url = ss.get_info_link()
    logindata = generate_logindata(ss.get_login(), ss.get_password())
    d = {
        "environment": {},
        "hash": "",
        "lang": "",
        "logindata": logindata,
        "softversion": ""
    }
    res = rpc_request(server_url, "user_getInfo", d)
    return res


def api_cards_getCards() -> list | None:
    ss = APISettings()
    server_url = ss.get_info_link()
    logindata = generate_logindata(ss.get_login(), ss.get_password())
    limit = ss.get_limit()
    d = {
        "adddata": "",
        "frompos": 0,
        "limit": limit,
        "orderfield": "name|0",
        "logindata": logindata,
        "qfilter": "",
        "qlabelfilter": ""
    }
    res = rpc_request(server_url, "cards_getCards", d)
    if res["result"]["errorcode"] != 0:
        print(f"Error (api_cards_getCards): \n{res}")
        return None
    return res["result"]["cardslist"]


def api_exp_getExpList(card_id: int) -> dict | None:
    ss = APISettings()
    server_url = ss.get_info_link()
    logindata = generate_logindata(ss.get_login(), ss.get_password())
    limit = ss.get_limit()
    params = {
        "logindata": logindata,
        "cardid": card_id,
        "frompos": 0,
        "limit": limit,
        "typefilter": -1,
        "ymdfilter": "",
        "orderfield": "dt|DESC",
        "labelfilter": ""
    }
    exp_list_response = rpc_request(server_url, "exp_getExpList", params)
    if exp_list_response.get("result", {}).get("errorcode") != 0:
        print("Ошибка при получении списка экспериментов:", exp_list_response)
        return None
    else:
        experiments = exp_list_response["result"]["explist"]
        if not experiments:
            print(f"No experiments in card: {card_id}")
            return None
        else:
            return experiments


def download_bdf(ex_id: int) -> bytes | None:
    ss = APISettings()
    server_url_bdf = ss.get_data_link()
    login = ss.get_login()
    pwd = ss.get_password_md5()
    r = requests.get(f"{server_url_bdf}?login={login}&pass={pwd}&expid={ex_id}")
    if r.status_code == 200:
        return r.content
    else:
        return None


def extract_text(comment: str) -> str:
    html_content = comment
    soup = BeautifulSoup(html_content, "html.parser")
    text = ' '.join(p.get_text() for p in soup.find_all('p'))

    return text


def extract_pictures(bdf_contest: str) -> list[bytes]:
    res = []
    soup = BeautifulSoup(bdf_contest, "lxml")
    pics = soup.find_all("picture")
    for pic_i in pics:
        s = pic_i["value"]
        image_data: bytes = base64.b64decode(s)
        res.append(image_data)
    return res


