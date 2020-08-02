
import json

from flask import Flask, render_template, request, session, make_response

from src.database import SQLiteDB
from src.encryption import decrypt_message

app = Flask(__name__)  # '__main__'
app.secret_key = "CountingChickens"

SQL_DB_NAME="pass_dev.db"
SQL_TBL_NAME='dev2'

@app.route('/', methods=['POST', 'GET'])
def home_template():
    if request.method == 'POST':
        db=SQLiteDB(SQL_DB_NAME)
        encrypted_text=db.select_all(SQL_TBL_NAME)

        password = request.form['title']

        decrypt_text=[]

        for txt in encrypted_text:
            decrypt_add=decrypt_message(txt, password)
            decrypt_text.append(decrypt_add)
        if isinstance(decrypt_text,str):
            decrypt_text=[decrypt_text]
    else:
        decrypt_text=['Enter password to open Chicken Vault']
    return render_template('home.html',decrypt_text=decrypt_text)



if __name__ == '__main__':
    app.run(port=4995, debug=True)