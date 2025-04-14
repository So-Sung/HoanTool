import os
import shutil
import sqlite3
import win32crypt
import tkinter as tk
from tkinter import messagebox

def insert_to_edge(url, username, password):
    try:
        login_data_path = os.path.join(
            os.environ["LOCALAPPDATA"],
            "Microsoft", "Edge", "User Data", "Default", "Login Data"
        )

        if not os.path.exists(login_data_path):
            messagebox.showerror("오류", "Edge Login Data 파일을 찾을 수 없습니다.")
            return

        # 백업 및 암호화
        backup_path = login_data_path + ".bak"
        shutil.copyfile(login_data_path, backup_path)
        enc_pw = win32crypt.CryptProtectData(password.encode(), None, None, None, None, 0)

        # 임시 파일에서 수정
        tmp_path = "temp_edge_login.db"
        shutil.copyfile(login_data_path, tmp_path)

        conn = sqlite3.connect(tmp_path)
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO logins (
            origin_url, action_url, username_value, password_value,
            date_created, blacklisted_by_user, scheme, times_used
        ) VALUES (?, ?, ?, ?, 13250000000000000, 0, 0, 1)
        """, (url, url, username, enc_pw))
        conn.commit()
        conn.close()

        # 덮어쓰기
        shutil.copyfile(tmp_path, login_data_path)
        os.remove(tmp_path)
        messagebox.showinfo("성공", f"{url} - {username} 저장 완료!")
    except Exception as e:
        messagebox.showerror("에러", f"삽입 실패: {e}")

def gui_main():
    window = tk.Tk()
    window.title("Edge 계정 자동 저장기")
    window.geometry("350x250")

    tk.Label(window, text="웹사이트 URL/IP").pack()
    url_entry = tk.Entry(window, width=40)
    url_entry.pack()

    tk.Label(window, text="계정 이름").pack()
    user_entry = tk.Entry(window, width=40)
    user_entry.pack()

    tk.Label(window, text="비밀번호").pack()
    pw_entry = tk.Entry(window, width=40, show="*")
    pw_entry.pack()

    def on_save():
        url = url_entry.get().strip()
        user = user_entry.get().strip()
        pw = pw_entry.get().strip()
        if not url or not user or not pw:
            messagebox.showwarning("입력 오류", "모든 항목을 입력하세요.")
            return
        insert_to_edge(url, user, pw)

    tk.Button(window, text="저장", command=on_save, width=10).pack(pady=10)
    tk.Label(window, text="※ Edge는 실행 중이면 안됩니다.", fg="red").pack()

    window.mainloop()

if __name__ == "__main__":
    gui_main()
