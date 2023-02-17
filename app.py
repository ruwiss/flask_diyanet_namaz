from flask import Flask, jsonify
from selectolax.lexbor import LexborHTMLParser
import requests
import extensions
import datetime
import time

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False


@app.route("/vakitler/<string:ilce>")
def hello_world(ilce: str):

    output = {
        "vakitler": {},
    }

    gunler = {}

    # Dini Günler Çekimi
    resp = requests.get(f"https://vakithesaplama.diyanet.gov.tr/dinigunler.php?yil={datetime.datetime.now().year}")
    html = LexborHTMLParser(resp.text)

    tablo = html.css_first("table.MsoNormalTable").css("tr")

    for ii, i in enumerate(tablo):
        if ii not in [0, 1, 2]:
            td = i.css("td")
            ay_yil = ''.join(c for c in td[4].css_first("p").text() if not c.isspace()).split("-")
            gun = ''.join(c for c in td[3].css_first("p").text() if not c.isspace())
            ay_split = ay_yil[0].split()
            ay = ''.join(c for c in ay_split if not c.isspace())

            type = ''.join(c for c in td[6].css_first("p").text() if not c.isspace())
            if "..." not in type:
                gunler[f"{gun}/{extensions.aylar.get(ay)}/{ay_yil[1]}"] = type

    # Namaz Vakitleri Çekimi
    resp = requests.get(f"https://namazvakitleri.diyanet.gov.tr/tr-TR/{extensions.getCode(ilce)}")
    html = LexborHTMLParser(resp.text)
    output['resim'] = html.css_first("div.moon-img-parent > img").attrs.get('src')
    tablo = html.css_first("#tab-1 > div > table > tbody").css("tr")

    for ii, i in enumerate(tablo):
        tarih_split = i.css_first("td").text().split(" ")
        str_key = f"{tarih_split[0]}/{extensions.aylar[tarih_split[1].upper()]}/{tarih_split[2]}"

        output['vakitler'][str_key] = {

            "saatler": {}
        }
        for k, v in gunler.items():
            if k == str_key:
                output['vakitler'][str_key]['gun'] = v

        for vv, v in enumerate(i.css("td")):
            if vv != 0:
                output['vakitler'][str_key]['saatler'][extensions.vakitler[vv]] = v.text()

    return jsonify(output)
