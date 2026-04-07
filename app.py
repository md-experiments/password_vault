import os

from flask import Flask, render_template, request

from src.database import SQLiteDB
from src.encryption import decrypt_message

app = Flask(__name__)
# Set FLASK_SECRET_KEY env var in production. Fallback is for local dev only.
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'dev-only-insecure-key')

SQL_DB_NAME = 'pass_dev.db'
SQL_TBL_NAME = 'dev2'


@app.route('/', methods=['POST', 'GET'])
def home_template():
    if request.method == 'POST':
        password = request.form.get('title', '').strip()
        if not password:
            return render_template('home.html', decrypt_text=['Password cannot be empty.'])

        with SQLiteDB(SQL_DB_NAME) as db:
            encrypted_text = db.select_all(SQL_TBL_NAME)

        decrypt_text = [decrypt_message(txt, password) for txt in encrypted_text]
    else:
        decrypt_text = ['Enter password to open Chicken Vault']

    return render_template('home.html', decrypt_text=decrypt_text)


if __name__ == '__main__':
    app.run(port=4995, debug=True)
