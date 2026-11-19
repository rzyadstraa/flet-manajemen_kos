import pymysql
import flet as ft
from datetime import datetime
import asyncio

def koneksi_database():
    return pymysql.connect(host="localhost", user="root", password="", database="db_manajemenkos")

def login_view(page: ft.Page, on_login_success):
    inputan_username = ft.TextField(label="Username", width=300)
    inputan_password = ft.TextField(label="Password", password=True, width=300)
    notif_login = ft.Text("", color=ft.Colors.RED)

    def tampil_loading(text=""):
        page.clean()
        page.add(ft.Container(alignment=ft.Alignment.CENTER, content=ft.Container(
            padding=30, margin=ft.Margin.only(top=300), bgcolor="white", border_radius=20,
            shadow=ft.BoxShadow(blur_radius=20, color="black12"),
            content=ft.Column(spacing=15, horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[ft.ProgressRing(width=60, height=60), ft.Text(text, size=16, weight=ft.FontWeight.BOLD)]),
        )))
        page.update()

    def proses_login(e):
        async def lanjut_setelah_loading(v_user, v_akses):
            await asyncio.sleep(1)
            on_login_success(v_user, v_akses)

        db = None
        try:
            db = koneksi_database()
            cur = db.cursor()
            cur.execute(
                "SELECT id_user, username, password, hak_akses FROM user WHERE username=%s AND password=%s",
                (inputan_username.value, inputan_password.value),
            )
            user = cur.fetchone()

            if user:
                v_id, v_user, _, v_akses = user
                cur.execute("UPDATE user SET akses_terakhir=%s WHERE id_user=%s", (datetime.now(), v_id))
                db.commit()
                tampil_loading("Memasuki Sistem Kos... 🍵")
                page.run_task(lanjut_setelah_loading, v_user, v_akses)
            else:
                notif_login.value = "❌ Akun tidak ditemukan!"
                page.update()
        except Exception as ex:
            notif_login.value = f"❌ Gagal terhubung ke database: {ex}"
            page.update()
        finally:
            if db is not None:
                db.close()

    return ft.Container(
        expand=True, alignment=ft.Alignment.CENTER,
        content=ft.Container(
            width=420, padding=30, height=400, bgcolor="white", border_radius=20,
            shadow=ft.BoxShadow(blur_radius=20, color="black12"),
            content=ft.Column(horizontal_alignment="center", spacing=15, controls=[
                ft.Text("🏠", size=50, weight="bold"),
                ft.Text("Smart Boarding House", size=24, weight="bold"),
                inputan_username, inputan_password,
                ft.Button("Log In ➡️", width=300, height=50, on_click=proses_login, color=ft.Colors.WHITE, bgcolor=ft.Colors.TEAL),
                notif_login
            ]),
        ),
    )