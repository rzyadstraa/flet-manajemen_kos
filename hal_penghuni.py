import pymysql
import flet as ft
from datetime import date

# =========================================================
# 🔹 Koneksi Database
# =========================================================
def koneksi_database():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="",
        database="db_manajemenkos"
    )

# =========================================================
# 🔹 HALAMAN KELOLA PENGHUNI
# =========================================================
def kelola_penghuni_view(page: ft.Page):
    selected_id = {"id": None}

    # ================= PAGINATION & SEARCH STATE =================
    current_page = {"value": 1}
    limit_per_page = 10
    keyword_cari = {"value": ""}

    # ================= FORM INPUT =================
    input_nama = ft.TextField(label="Nama Lengkap", prefix_icon=ft.Icons.PERSON, width=360)
    input_pekerjaan = ft.TextField(label="Pekerjaan", prefix_icon=ft.Icons.WORK, width=360)
    input_no_hp = ft.TextField(label="Nomor WhatsApp", prefix_icon=ft.Icons.PHONE, width=360)
    input_alamat = ft.TextField(
        label="Alamat Asal",
        multiline=True,
        min_lines=2,
        prefix_icon=ft.Icons.HOME,
        width=360
    )
    input_kontak_darurat = ft.TextField(label="Kontak Darurat (Keluarga)", prefix_icon=ft.Icons.EMERGENCY, width=360)
    input_tgl_masuk = ft.TextField(label="Tanggal Masuk", prefix_icon=ft.Icons.CALENDAR_TODAY, read_only=True, width=250)

    # ================= DATE PICKER =================
    def pilih_tanggal(e):
        if e.control.value:
            try:
                input_tgl_masuk.value = e.control.value.strftime("%Y-%m-%d")
            except:
                input_tgl_masuk.value = str(e.control.value)
            input_tgl_masuk.update()

    date_picker = ft.DatePicker(
        first_date=date(2020, 1, 1),
        last_date=date(2030, 12, 31),
        on_change=pilih_tanggal
    )
    page.overlay.append(date_picker)

    btn_tgl = ft.Button(
        "Pilih",
        icon=ft.Icons.CALENDAR_MONTH,
        width=80,
        on_click=lambda e: page.open(date_picker)
    )

    notif_penghuni = ft.Text("")

    # ================= INPUT SEARCH =================
    def proses_cari(e):
        keyword_cari["value"] = e.control.value
        current_page["value"] = 1
        muat_data_penghuni()

    input_cari = ft.TextField(
        hint_text="Cari nama penghuni...",
        prefix_icon=ft.Icons.SEARCH,
        on_change=proses_cari,
        width=350
    )

    # ================= RESET FORM =================
    def bersihkan_form():
        input_nama.value = ""
        input_pekerjaan.value = ""
        input_no_hp.value = ""
        input_alamat.value = ""
        input_kontak_darurat.value = ""
        input_tgl_masuk.value = ""
        selected_id["id"] = None
        notif_penghuni.value = ""
        page.update()

    # ================= SIMPAN / UPDATE =================
    def simpan_penghuni(e):
        if not input_nama.value or not input_no_hp.value:
            notif_penghuni.value = "❌ Nama dan No HP wajib diisi"
            notif_penghuni.color = ft.Colors.RED
            page.update()
            return

        db = koneksi_database()
        cur = db.cursor()

        if selected_id["id"]:  # UPDATE
            cur.execute(
                """UPDATE data_penghuni
                   SET nama=%s, pekerjaan=%s, no_hp=%s,
                       alamat_asal=%s, kontak_darurat=%s, tanggal_masuk=%s
                   WHERE id_penghuni=%s""",
                (
                    input_nama.value,
                    input_pekerjaan.value,
                    input_no_hp.value,
                    input_alamat.value,
                    input_kontak_darurat.value,
                    input_tgl_masuk.value,
                    selected_id["id"]
                )
            )
            notif_penghuni.value = "✅ Data penghuni diperbarui"
        else:  # INSERT
            cur.execute(
                """INSERT INTO data_penghuni
                   (nama, pekerjaan, no_hp, alamat_asal, kontak_darurat, tanggal_masuk)
                   VALUES (%s, %s, %s, %s, %s, %s)""",
                (
                    input_nama.value,
                    input_pekerjaan.value,
                    input_no_hp.value,
                    input_alamat.value,
                    input_kontak_darurat.value,
                    input_tgl_masuk.value
                )
            )
            notif_penghuni.value = "✅ Penghuni berhasil ditambahkan"

        db.commit()
        db.close()

        notif_penghuni.color = ft.Colors.GREEN
        bersihkan_form()
        muat_data_penghuni()
        page.update()

    # ================= HAPUS DATA =================
    def konfirmasi_hapus(id_p):
        db = koneksi_database()
        cur = db.cursor()
        cur.execute("DELETE FROM data_penghuni WHERE id_penghuni=%s", (id_p,))
        db.commit()
        db.close()
        muat_data_penghuni()
        page.update()

    # ================= EDIT DATA =================
    def edit_penghuni(row):
        selected_id["id"] = row[0]
        input_nama.value = row[1] or ""
        input_pekerjaan.value = row[2] or ""
        input_no_hp.value = row[3] or ""
        input_alamat.value = row[4] or ""
        input_kontak_darurat.value = row[5] or ""
        input_tgl_masuk.value = str(row[6]) if row[6] else ""
        page.update()

    # ================= TABEL (MODIFIKASI SPACING) =================
    tabel_penghuni = ft.DataTable(
        column_spacing=20,  # 🔹 Dikecilkan agar kolom tidak terlalu jauh
        columns=[
            ft.DataColumn(ft.Text("No.")),
            ft.DataColumn(ft.Text("Nama")),
            ft.DataColumn(ft.Text("Pekerjaan")),
            ft.DataColumn(ft.Text("No. HP")),
            ft.DataColumn(ft.Text("Alamat")),
            ft.DataColumn(ft.Text("Kontak")),
            ft.DataColumn(ft.Text("Tgl Masuk")),
            ft.DataColumn(ft.Text("Aksi")),
        ],
        rows=[]
    )

    def muat_data_penghuni():
        tabel_penghuni.rows.clear()

        db = koneksi_database()
        cur = db.cursor()
        keyword = f"%{keyword_cari['value']}%"

        offset = (current_page["value"] - 1) * limit_per_page
        cur.execute(
            "SELECT * FROM data_penghuni WHERE nama LIKE %s LIMIT %s OFFSET %s",
            (keyword, limit_per_page, offset)
        )
        data = cur.fetchall()
        db.close()

        for index, row in enumerate(data):
            no_urut = offset + index + 1
            nama = row[1] or ""
            pekerjaan = row[2] or ""
            no_hp = row[3] or ""
            alamat = row[4] or ""
            kontak_darurat = row[5] or ""
            tgl_masuk = str(row[6]) if row[6] else ""

            tabel_penghuni.rows.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(no_urut)),
                    ft.DataCell(ft.Text(nama)),
                    ft.DataCell(ft.Text(pekerjaan)),
                    # No HP: Diberi container agar lebar terkontrol
                    ft.DataCell(ft.Container(width=100, content=ft.Text(no_hp))),

                    # Alamat: Lebar dikurangi (150) + Titik-titik jika kepanjangan
                    ft.DataCell(
                        ft.Container(
                            width=150, 
                            content=ft.Text(alamat, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS, tooltip=alamat)
                        )
                    ),

                    # Kontak Darurat: Lebar dikurangi (120)
                    ft.DataCell(
                        ft.Container(
                            width=120, 
                            content=ft.Text(kontak_darurat, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS, tooltip=kontak_darurat)
                        )
                    ),

                    ft.DataCell(ft.Text(tgl_masuk)),
                    ft.DataCell(ft.Row([
                        ft.IconButton(ft.Icons.EDIT, on_click=lambda e, r=row: edit_penghuni(r), icon_size=18),
                        ft.IconButton(ft.Icons.DELETE, icon_color="red", on_click=lambda e, i=row[0]: konfirmasi_hapus(i), icon_size=18),
                    ], spacing=0))
                ])
            )

        page.update()

    muat_data_penghuni()

    # ================= LAYOUT =================
    form_column = ft.Column(
        spacing=15,
        controls=[
            ft.Text("Form Penghuni", size=18, weight="bold"),
            input_nama,
            input_pekerjaan,
            input_no_hp,
            input_alamat,
            input_kontak_darurat,
            ft.Row([input_tgl_masuk, btn_tgl]),
            ft.Row([
                ft.Button("Simpan", icon=ft.Icons.SAVE, bgcolor=ft.Colors.TEAL, color=ft.Colors.WHITE, on_click=simpan_penghuni),
                ft.Button("Batal", icon=ft.Icons.CLEAR, bgcolor=ft.Colors.BLACK, color=ft.Colors.WHITE, on_click=lambda e: bersihkan_form()),
            ]),
            notif_penghuni,
        ],
    )

    tabel_scroll = ft.Column(
        expand=True,
        scroll=ft.ScrollMode.AUTO,
        controls=[
            ft.Row(
                scroll=ft.ScrollMode.AUTO,
                controls=[tabel_penghuni]
            )
        ]
    )

    return ft.Container(
        expand=True,
        padding=20,
        content=ft.Row(
            spacing=20,
            controls=[
                ft.Container(
                    width=380,
                    padding=20,
                    bgcolor="white",
                    border_radius=20,
                    shadow=ft.BoxShadow(blur_radius=20, color="black12"),
                    content=form_column
                ),
                ft.Container(
                    expand=True,
                    padding=20,
                    bgcolor="white",
                    border_radius=20,
                    shadow=ft.BoxShadow(blur_radius=20, color="black12"),
                    content=ft.Column(
                        expand=True,
                        controls=[
                            ft.Text("Data Penghuni Kos", size=18, weight="bold"),
                            input_cari,
                            ft.Divider(),
                            tabel_scroll
                        ]
                    )
                )
            ]
        )
    )