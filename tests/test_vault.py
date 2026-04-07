import pytest
import sqlite3

from src.encryption import derive_pass, encrypt_message, decrypt_message
from src.database import SQLiteDB, FileDB, _validate_identifier


# ---------------------------------------------------------------------------
# encryption.py
# ---------------------------------------------------------------------------

def test_derive_pass_returns_bytes():
    assert isinstance(derive_pass("mypassword"), bytes)


def test_derive_pass_deterministic():
    assert derive_pass("secret") == derive_pass("secret")


def test_derive_pass_different_passwords_different_keys():
    assert derive_pass("secret") != derive_pass("other")


def test_encrypt_decrypt_roundtrip():
    msg = "hello vault"
    pwd = "testpass"
    encrypted = encrypt_message(msg, pwd)
    assert decrypt_message(encrypted.decode('ascii'), pwd) == msg


def test_decrypt_wrong_password_returns_sentinel():
    encrypted = encrypt_message("hello vault", "correctpass")
    assert decrypt_message(encrypted.decode('ascii'), "wrongpass") == "Wrong password"


def test_decrypt_garbage_input_returns_wrong_password():
    # InvalidToken should be caught; any other error should still propagate
    assert decrypt_message("not-a-valid-fernet-token==", "anypass") == "Wrong password"


# ---------------------------------------------------------------------------
# database.py – _validate_identifier
# ---------------------------------------------------------------------------

def test_validate_identifier_accepts_valid_names():
    assert _validate_identifier("dev2") == "dev2"
    assert _validate_identifier("my_table_1") == "my_table_1"


def test_validate_identifier_rejects_sql_injection():
    with pytest.raises(ValueError):
        _validate_identifier("dev2; DROP TABLE dev2--")


def test_validate_identifier_rejects_spaces():
    with pytest.raises(ValueError):
        _validate_identifier("table name")


def test_validate_identifier_rejects_hyphens():
    with pytest.raises(ValueError):
        _validate_identifier("table-name")


# ---------------------------------------------------------------------------
# database.py – SQLiteDB
# ---------------------------------------------------------------------------

@pytest.fixture
def db(tmp_path):
    db_path = str(tmp_path / "test.db")
    with SQLiteDB(db_path) as database:
        database.create_table("entries")
        yield database


def test_create_table_idempotent(db):
    db.create_table("entries")  # second call must not raise


def test_add_and_select_all(db):
    db.add("entries", "value_one")
    db.add("entries", "value_two")
    assert db.select_all("entries") == ["value_one", "value_two"]


def test_add_rejects_injection_in_table_name(db):
    with pytest.raises(ValueError):
        db.add("entries; DROP TABLE entries--", "data")


def test_select_all_rejects_injection_in_table_name(db):
    with pytest.raises(ValueError):
        db.select_all("entries; DROP TABLE entries--")


def test_context_manager_closes_connection(tmp_path):
    db_path = str(tmp_path / "cm_test.db")
    with SQLiteDB(db_path) as db:
        db.create_table("t")
        db.add("t", "val")
    # Connection is closed after __exit__; further operations should raise
    with pytest.raises(Exception):
        db.select_all("t")


# ---------------------------------------------------------------------------
# database.py – FileDB
# ---------------------------------------------------------------------------

def test_filedb_save_and_load(tmp_path):
    f = tmp_path / "data.txt"
    fdb = FileDB(str(f))
    fdb.save_to_file("line one\nline two")
    assert fdb.load_file() == ["line one", "line two"]


def test_filedb_load_uses_instance_file(tmp_path):
    f = tmp_path / "myfile.txt"
    f.write_text("alpha\nbeta\n")
    fdb = FileDB(str(f))
    assert fdb.load_file() == ["alpha", "beta"]


# ---------------------------------------------------------------------------
# Flask routes (app.py)
# ---------------------------------------------------------------------------

@pytest.fixture
def client(tmp_path, monkeypatch):
    from src.encryption import encrypt_message

    # Build a test DB with one encrypted entry
    db_path = str(tmp_path / "test_app.db")
    conn = sqlite3.connect(db_path)
    enc = encrypt_message("secret message", "correctpass")
    conn.execute("CREATE TABLE dev2 (encrypted_text TEXT)")
    conn.execute("INSERT INTO dev2 VALUES (?)", (enc.decode('ascii'),))
    conn.commit()
    conn.close()

    import app as app_mod
    monkeypatch.setattr(app_mod, "SQL_DB_NAME", db_path)
    app_mod.app.config["TESTING"] = True
    app_mod.app.secret_key = "test-key"

    with app_mod.app.test_client() as c:
        yield c


def test_get_shows_initial_message(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert b"Enter password" in resp.data


def test_post_correct_password_decrypts(client):
    resp = client.post("/", data={"title": "correctpass"})
    assert resp.status_code == 200
    assert b"secret message" in resp.data


def test_post_wrong_password_shows_sentinel(client):
    resp = client.post("/", data={"title": "wrongpass"})
    assert resp.status_code == 200
    assert b"Wrong password" in resp.data


def test_post_empty_password_shows_validation_error(client):
    resp = client.post("/", data={"title": ""})
    assert resp.status_code == 200
    assert b"cannot be empty" in resp.data
