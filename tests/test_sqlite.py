import sqlite3
from aries_cloudagent_vsw.wallet import crypto

def test_sqlite():
    conn = sqlite3.connect("/Users/Felix/.indy_client/wallet/sunny/sqlite.db")
    cursor = conn.cursor()
    query = "SELECT type FROM items"
    cursor.execute(query)
    for row in cursor.fetchall():
        print(crypto.decrypt_plaintext(row[0]))
        # print(repr(row[0]))
    cursor.close()
