import sqlite3
import json
import os
from pathlib import Path
home = str(Path.home())
db_file = Path(home).joinpath(f".indy_client/vsw/sqlite.db").resolve()


def init():
    if not os.path.exists(str(Path(os.path.expanduser('~'))) + "/.indy_client/vsw/"):
        os.makedirs(str(Path(os.path.expanduser('~'))) + "/.indy_client/vsw/")
    conn = sqlite3.connect(db_file)
    c = conn.cursor()
    sql = 'CREATE TABLE IF NOT EXISTS credentials (issuer_did TEXT NOT NULL, software_name TEXT, software_did TEXT, status TEXT, content TEXT,  sqltime TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL);'
    c.execute(sql)
    conn.commit()
    c.close()
    conn.close()


def save_credential(issuer_did, software_name, software_did, status, jsonObject):
    conn = sqlite3.connect(db_file)
    c = conn.cursor()
    sql = f"INSERT INTO credentials (issuer_did, software_name, software_did, status, content) VALUES(?,?,?,?,?)"
    c.execute(sql, (issuer_did, software_name, software_did, status, json.dumps(jsonObject)))
    conn.commit()
    c.close()
    conn.close()


def get_credential_by_issuer_did(issuer_did):
    conn = sqlite3.connect(db_file)
    c = conn.cursor()
    sql = "select content from credentials where issuer_did = ?"
    c.execute(sql, (issuer_did,))
    results = c.fetchall()
    c.close()
    conn.close()
    return results


def get_credential_by_issuer_did_and_name(issuer_did, software_name):
    conn = sqlite3.connect(db_file)
    c = conn.cursor()
    sql = "select content from credentials where issuer_did= ? and software_name= ? "
    c.execute(sql, (issuer_did, software_name))
    results = c.fetchall()
    c.close()
    conn.close()
    return results


def remove_credential(issuer_did):
    conn = sqlite3.connect(db_file)
    c = conn.cursor()
    c.execute(f"delete from credentials where issuer_did = ?", (issuer_did))
    conn.commit()
    c.close()
    conn.close()
