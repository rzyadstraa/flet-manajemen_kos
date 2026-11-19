import pymysql
import flet as ft

def koneksi_database():
    return pymysql.connect(host="localhost", user="root", password="", database="db_manajemenkos")

def profil_view(page: ft.Page, username, hak_akses):
    input_username = ft.TextField(label="Username Baru", prefix_icon=ft.Icons.PERSON, width=320)
    input_password = ft.TextField(label="Password Baru", prefix_icon=ft.Icons.LOCK, password=True, can_reveal_password=True, width=320)
    notif_profil = ft.Text("", color=ft.Colors.GREEN)

    def simpan_perubahan(e):
        if not input_username.value and not input_password.value:
            notif_profil.value = "⚠️ Isi data yang ingin diubah"
            notif_profil.color = ft.Colors.RED
            page.update()
            return
        
        db = koneksi_database()
        cur = db.cursor()
        if input_username.value:
            cur.execute("UPDATE user SET username=%s WHERE username=%s", (input_username.value, username))
        if input_password.value:
            cur.execute("UPDATE user SET password=%s WHERE username=%s", (input_password.value, input_username.value or username))
        db.commit()
        db.close()
        notif_profil.value = "✅ Profil berhasil diperbarui"
        page.update()

    return ft.Container(
        alignment=ft.Alignment.TOP_LEFT,
        content=ft.Container(
            width=450, padding=30, bgcolor="white", border_radius=20,
            shadow=ft.BoxShadow(blur_radius=20, color="black12"),
            content=ft.Column(spacing=18, horizontal_alignment="center", controls=[
                ft.Icon(ft.Icons.ACCOUNT_CIRCLE, size=90, color=ft.Colors.BLUE),
                ft.Text("Pengaturan Profil", size=18, weight="bold"),
                ft.Divider(),
                ft.Row(alignment="center", controls=[ft.Icon(ft.Icons.BADGE), ft.Text(f"Username : {username}")]),
                ft.Row(alignment="center", controls=[ft.Icon(ft.Icons.VERIFIED_USER), ft.Text(f"Status : {hak_akses}")]),
                ft.Divider(),
                input_username, input_password,
                ft.Button("Simpan Perubahan", icon=ft.Icons.SAVE, width=320, height=45, on_click=simpan_perubahan, color=ft.Colors.WHITE, bgcolor=ft.Colors.TEAL),
                notif_profil
            ]),
        ),
    )