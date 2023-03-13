# flask API, Swagger UI

from flask import request, Flask, jsonify

from flasgger import Swagger, LazyString, LazyJSONEncoder
from flasgger import swag_from

import pandas as pd
import numpy as np
import re

import sqlite3


def sensor_abusive(abusive_old_text):

    # memasukan data kata abusive
    abusive_data = pd.read_csv('abusive.csv')

    # masukan kalimat abusive ke variable y
    y = abusive_old_text.lower()
    # inisialisasi nomor pada data kata abusive
    number_of_abusive_data = 0

    # lakukan perulangan untuk setiap data di abusive_data['ABUSIVE']
    for j in abusive_data['ABUSIVE']:
        # ubah kata abusive menjadi ****
        z = re.sub(abusive_data['ABUSIVE']
                   [number_of_abusive_data], "***SENSOR***", y)
        # masukan data abusive yang sudah di ubah ke variable y
        y = z
        # tambahkan 1 pada variable number_of_abusive_data
        number_of_abusive_data += 1

    # kembalikan nilai y
    return y


app = Flask(__name__)

###############################################################################################################
app.json_encoder = LazyJSONEncoder

swagger_template = dict(
    info={
        'title': LazyString(lambda: 'API Documentation for Data Processing and Modeling'),
        'version': LazyString(lambda: '1.0.0'),
        'description': LazyString(lambda: 'Dokumentasi API untuk Data Processing dan Modeling')
    }, host=LazyString(lambda: request.host)
)

swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": 'docs',
            "route": '/docs.json'
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/docs/"
}

swagger = Swagger(app, template=swagger_template, config=swagger_config)
###############################################################################################################

# GET


@swag_from("docs/get.yml", methods=['GET'])
@app.route('/', methods=['GET'])
def hard_code_text_abusive():

    # koneksi ke database dengan nama sql
    conn = sqlite3.connect('sql.db')

    # query untuk mengambil seluruh data di table_tweet
    df = pd.read_sql_query('SELECT * FROM table_tweet', conn)

    conn.commit()
    # tutup koneksi
    conn.close()

    # masukan kalimat abusive
    dict_text = df.to_dict()

    # ubah variable dict_text ke json
    response_data = jsonify(dict_text)
    # kembalikan variable response_data
    return response_data
###############################################################################################################

# POST


@swag_from("docs/input.yml", methods=['POST'])
@app.route('/input', methods=['POST'])
def input_text_abusive():

    # masukan kalimat abusive dengan key tweet
    tweet = request.get_json(force=True)

    # masukan data tweet ke variable text
    text = tweet['tweet']

    # masukan inputan variable text ke dalam function sesor_abusive dan masukan hasil return ke variabel value_sensor_abusive
    value_sensor_abusive = sensor_abusive(text)

    # buat dict untuk list text
    list_text = {'old_text': [], 'censored_text': []}

    # masukan inputan variable text ke list_text['old_text']
    list_text['old_text'].append(text.lower())
    # masukan variable value_sensor_abusive ke list_text['censored_text']
    list_text['censored_text'].append(value_sensor_abusive)

    # koneksi ke database dengan nama sql
    conn = sqlite3.connect('sql.db')

    # query untuk memasukan data ke table_tweet
    query = '''insert into table_tweet
                (old_text, censored_text)
                values ('{}', '{}')'''.format(list_text['old_text'][0], list_text['censored_text'][0])

    # eksekusi syntax query
    conn.execute(query)

    conn.commit()
    # tutup koneksi
    conn.close()

    # ubah variable list_text ke json
    # response_data = jsonify(list_text)
    # kembalikan variable response_data
    return "SUKSES INPUT"
###############################################################################################################

# UPLOAD


@swag_from("docs/upload.yml", methods=['POST'])
@app.route('/upload', methods=['POST'])
def upload_text_abusive():

    # masukan file csv
    file = request.files['file']

    try:
        df1 = pd.read_csv(file, encoding='iso-8859-1', error_bad_lines=False)
    except:
        df1 = pd.read_csv(file, encoding='utf-8', error_bad_lines=False)

    # masukan variable abusive_instagram_text pada kolom ['Instagram Comment Text'] ke dataframe
    df = pd.DataFrame(df1, columns=['Instagram Comment Text'])
    # Untuk setiap data di Instagram Comment Text, lakukan pengolahan pada sensor_abusive dan masukan hasilnya ke df['censored_text']
    df['censored_text'] = df['Instagram Comment Text'].apply(
        lambda x: sensor_abusive(x))

    # ubah variable df ke dictionary
    json_data = df.to_dict()

    # koneksi ke database dengan nama sql
    conn = sqlite3.connect('sql.db')

    # inisialisasi varibale num
    num = 0

    # lakukan perulangan sebanyak jumlah data di json_data['Instagram Comment Text']
    while num < len(json_data['Instagram Comment Text']):

        # eksekusi syntax query
        conn.execute("insert into table_tweet (old_text, censored_text) values (?, ?)",
                     (json_data['Instagram Comment Text'][num], json_data['censored_text'][num]))

        # tambahkan 1 ke dalam variable num
        num = num + 1

    conn.commit()
    # tutup koneksi
    conn.close()

    return 'SUKSES UPLOAD'
###############################################################################################################
# PUT


@swag_from("docs/update.yml", methods=['PUT'])
@app.route('/update/<id>', methods=['PUT'])
def update_text_abusive(id):
    # masukan kalimat abusive dengan key tweet
    tweet = request.get_json(force=True)

    # masukan data tweet ke variable text
    text = tweet['tweet']

    # masukan inputan variable text ke dalam function sesor_abusive dan masukan hasil return ke variabel value_sensor_abusive
    value_sensor_abusive = sensor_abusive(text)

    # buat dict untuk list text
    list_text = {'old_text': [], 'censored_text': []}

    # masukan inputan variable text ke list_text['old_text']
    list_text['old_text'].append(text.lower())
    # masukan variable value_sensor_abusive ke list_text['censored_text']
    list_text['censored_text'].append(value_sensor_abusive)

    # koneksi ke database dengan nama sql
    conn = sqlite3.connect('sql.db')

    # query untuk mengubah data di table_tweet berdasarkan id
    query = '''UPDATE table_tweet
                SET old_text = '{}',  censored_text = '{}'
                WHERE id = {}'''.format(list_text['old_text'][0], list_text['censored_text'][0], id)

    # eksekusi syntax query
    conn.execute(query)

    conn.commit()
    # tutup koneksi
    conn.close()

    # ubah variable list_text ke json
    # response_data = jsonify(list_text)
    # kembalikan variable response_data
    return "SUKSES UPDATE"


###############################################################################################################

# DELETE


@swag_from("docs/delete.yml", methods=['DELETE'])
@app.route('/delete/<id>', methods=['DELETE'])
def delete_text_abusive(id):

    # koneksi ke database dengan nama sql
    conn = sqlite3.connect('sql.db')

    # query untuk menghapus data di table_tweet berdasarkan id
    query = '''DELETE FROM table_tweet WHERE id = {}'''.format(id)

    # eksekusi syntax query
    conn.execute(query)

    conn.commit()
    # tutup koneksi
    conn.close()

    # ubah variable list_text ke json
    # response_data = jsonify(list_text)
    # kembalikan variable response_data
    return "SUKSES DELETE"


###############################################################################################################
if __name__ == '__main__':
    app.run()
