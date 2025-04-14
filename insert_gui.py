import os
import sqlite3
import shutil
import win32crypt
import tkinter as tk
from tkinter import messagebox, ttk

EDGE_DB_PATH = os.path.join(
    os.environ["LOCALAPPDATA"], "Microsoft", "Edge", "User Data", "Default", "Login Data"
)

BACKUP_PATH = EDGE_DB_PATH + ".bak"
TMP_DB = "temp_edge_login.db"

# ----------- DB 관련 함수 -----------
def backup_and_prepare_db():
    if not os.path.exists(EDGE_DB_PATH):
        messagebox.showerror("오류", "Edge Login Data DB를 찾을 수 없습니다.")
        return False
    shutil.copyfile(EDGE_DB_PATH, BACKUP_PATH)
    shutil.copyfile(EDGE_DB_PATH, TMP_DB)
    return True

def commit_changes():
    try:
        shutil.copyfile(TMP_DB, EDGE_DB_PATH)
        os.remove(TMP_DB)
    except Exception as e:
        messagebox.showerror("복사 오류", f"Login Data 덮어쓰기 실패:\n{e}\n\nEdge가 실행 중인지 확인하세요.")

# ----------- 저장된 IP 리스트 불러오기 -----------
def get_saved_sites():
    if not backup_and_prepare_db():
        return []
    conn = sqlite3.connect(TMP_DB)
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT origin_url FROM logins")
    rows = cursor.fetchall()
    conn.close()
    return [r[0] for r in rows if r[0]]

# ----------- 데이터 삭제 -----------
def delete_entry(url):
    if not backup_and_prepare_db():
        return
    conn = sqlite3.connect(TMP_DB)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM logins WHERE origin_url = ?", (url,))
    conn.commit()
    conn.close()
    commit_changes()
    messagebox.showinfo("삭제 완료", f"{url} 항목이 삭제되었습니다.")

# ----------- 데이터 추가 -----------
def insert_entry(url, username, password):
    if not url or not username or not password:
        messagebox.showwarning("입력 오류", "모든 필드를 입력해주세요.")
        return

    if not backup_and_prepare_db():
        return

    enc_pw = win32crypt.CryptProtectData(password.encode(), None, None, None, None, 0)
    conn = sqlite3.connect(TMP_DB)
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO logins (
        origin_url, action_url, username_value, password_value,
        signon_realm, date_created, blacklisted_by_user, scheme, times_used
    ) VALUES (?, ?, ?, ?, ?, 13250000000000000, 0, 0, 1)
    """, (url, url, username, enc_pw, url))
    conn.commit()
    conn.close()
    commit_changes()
    messagebox.showinfo("추가 완료", f"{url} 계정이 저장되었습니다.")

# ----------- 추가 창 -----------
def open_add_window(parent):
    def add():
        insert_entry(url_entry.get().strip(), user_entry.get().strip(), pw_entry.get().strip())
        add_win.destroy()

    add_win = tk.Toplevel(parent)
    add_win.title("계정 추가")
    add_win.geometry("300x200")

    tk.Label(add_win, text="웹사이트 URL/IP").pack()
    url_entry = tk.Entry(add_win)
    url_entry.pack()

    tk.Label(add_win, text="계정 이름").pack()
    user_entry = tk.Entry(add_win)
    user_entry.pack()

    tk.Label(add_win, text="비밀번호").pack()
    pw_entry = tk.Entry(add_win, show="*")
    pw_entry.pack()

    tk.Button(add_win, text="저장", command=add).pack(pady=5)
    tk.Button(add_win, text="뒤로가기", command=add_win.destroy).pack(pady=5)

# ----------- 삭제 창 -----------
def open_delete_window(parent):
    def refresh_saved_sites():
        ip_list = get_saved_sites()
        combo_box['values'] = ip_list

    def delete_selected():
        url = combo_box.get()
        if url:
            confirm = messagebox.askyesno("삭제 확인", f"{url} 정말 삭제하시겠습니까?!!!??!")
            if confirm:
                delete_entry(url)
                refresh_saved_sites()

    del_win = tk.Toplevel(parent)
    del_win.title("계정 삭제")
    del_win.geometry("350x200")

    tk.Label(del_win, text="저장된 웹사이트 IP/URL").pack()
    combo_box = ttk.Combobox(del_win, width=40)
    combo_box.pack(pady=5)

    tk.Button(del_win, text="삭제", command=delete_selected).pack(pady=5)
    tk.Button(del_win, text="뒤로가기", command=del_win.destroy).pack(pady=5)

    refresh_saved_sites()

# ----------- 메인 선택 창 -----------
def launch_gui():
    os.system("taskkill /F /IM msedge.exe >nul 2>&1")

    def open_add():
        open_add_window(window)

    def open_delete():
        open_delete_window(window)

    window = tk.Tk()
    window.title("Edge 계정 자동 저장기")
    window.geometry("300x200")

    tk.Label(window, text="원하는 작업을 선택하세요").pack(pady=10)

    tk.Button(window, text="1. 계정 추가", command=open_add, width=20).pack(pady=10)
    tk.Button(window, text="2. 계정 삭제", command=open_delete, width=20).pack(pady=10)

    window.mainloop()

if __name__ == "__main__":
    launch_gui()
