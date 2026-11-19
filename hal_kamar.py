import pymysql
import flet as ft

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
# 🔹 HALAMAN KELOLA KAMAR
# =========================================================
def kelola_kamar_view(page: ft.Page):
    selected_id = {"id": None}

    # ================= STATE =================
    current_page = {"value": 1}
    limit_per_page = 10
    total_data = {"value": 0}
    keyword_cari = {"value": ""}

    # ================= FORM INPUT =================
    input_nomor = ft.TextField(label="Nomor Kamar", prefix_icon=ft.Icons.NUMBERS, width=360)

    # --- ft.Dropdown wrapper key (biar bisa remount/reset total) ---
    dd_tipe_counter = {"value": 0}
    dd_status_counter = {"value": 0}

    input_tipe = ft.Dropdown(
        label="Tipe Kamar",
        options=[ft.dropdown.Option("AC"), ft.dropdown.Option("Non-AC")],
        leading_icon=ft.Icons.AIR,
        width=360,
    )
    tipe_container = ft.Container(key=f"dd_tipe_{dd_tipe_counter['value']}", content=input_tipe)

    input_lantai = ft.TextField(label="Lantai", prefix_icon=ft.Icons.LAYERS, width=360)
    input_fasilitas = ft.TextField(
        label="Fasilitas (TV, Kasur, dsb)",
        multiline=True,
        min_lines=2,
        width=360
    )
    input_harga = ft.TextField(label="Harga Per Bulan", prefix_icon=ft.Icons.MONETIZATION_ON, width=360)

    input_status = ft.Dropdown(
        label="Status Huni",
        options=[ft.dropdown.Option("Kosong"), ft.dropdown.Option("Terisi")],
        leading_icon=ft.Icons.BED,
        width=360,
    )
    status_container = ft.Container(key=f"dd_status_{dd_status_counter['value']}", content=input_status)

    notif_kamar = ft.Text("")

    # ================= INPUT SEARCH =================
    def proses_cari(e):
        keyword_cari["value"] = e.control.value
        current_page["value"] = 1
        muat_data_kamar()
        page.update()

    input_cari = ft.TextField(
        hint_text="Cari nomor kamar...",
        prefix_icon=ft.Icons.SEARCH,
        on_change=proses_cari,
        width=350
    )

    # ================= RESET FORM =================
    def bersihkan_form():
        input_nomor.value = ""
        input_lantai.value = ""
        input_fasilitas.value = ""
        input_harga.value = ""
        selected_id["id"] = None

        # reset value dropdown
        input_tipe.value = None
        input_status.value = None

        # remount dropdown (paksa render ulang)
        dd_tipe_counter["value"] += 1
        dd_status_counter["value"] += 1
        tipe_container.key = f"dd_tipe_{dd_tipe_counter['value']}"
        status_container.key = f"dd_status_{dd_status_counter['value']}"

        notif_kamar.value = ""
        page.update()

    # ================= SIMPAN / UPDATE =================
    def simpan_kamar(e):
        if not input_nomor.value or not input_tipe.value or not input_harga.value:
            notif_kamar.value = "❌ Nomor, Tipe, dan Harga wajib diisi"
            notif_kamar.color = ft.Colors.RED
            page.update()
            return

        db = koneksi_database()
        cur = db.cursor()

        if selected_id["id"]:  # UPDATE
            cur.execute(
                """ UPDATE data_kamar 
                    SET nomor_kamar=%s, tipe_kamar=%s, lantai=%s, fasilitas=%s, harga_per_bulan=%s, status_huni=%s
                    WHERE id_kamar=%s """,
                (
                    input_nomor.value,
                    input_tipe.value,
                    input_lantai.value,
                    input_fasilitas.value,
                    input_harga.value,
                    input_status.value,
                    selected_id["id"],
                )
            )
            notif_kamar.value = "✅ Data kamar diperbarui"
        else:  # INSERT
            cur.execute(
                """ INSERT INTO data_kamar (nomor_kamar, tipe_kamar, lantai, fasilitas, harga_per_bulan, status_huni)
                    VALUES (%s, %s, %s, %s, %s, %s) """,
                (
                    input_nomor.value,
                    input_tipe.value,
                    input_lantai.value,
                    input_fasilitas.value,
                    input_harga.value,
                    input_status.value,
                )
            )
            notif_kamar.value = "✅ Kamar berhasil ditambahkan"

        db.commit()
        db.close()

        notif_kamar.color = ft.Colors.GREEN
        bersihkan_form()
        muat_data_kamar()
        page.update()

    # ================= HAPUS =================
    def hapus_kamar(id_kamar):
        db = koneksi_database()
        cur = db.cursor()
        cur.execute("DELETE FROM data_kamar WHERE id_kamar=%s", (id_kamar,))
        db.commit()
        db.close()
        muat_data_kamar()
        page.update()

    # ================= EDIT =================
    def edit_kamar(row):
        selected_id["id"] = row[0]
        input_nomor.value = row[1]
        input_tipe.value = row[2]
        input_lantai.value = str(row[3]) if row[3] is not None else ""
        input_fasilitas.value = row[4] if row[4] is not None else ""
        input_harga.value = str(row[5]) if row[5] is not None else ""
        input_status.value = row[6]

        page.update()

    # ================= TABEL =================
    tabel_kamar = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("No.")),
            ft.DataColumn(ft.Text("Nomor")),
            ft.DataColumn(ft.Text("Tipe")),
            ft.DataColumn(ft.Text("Lantai")),
            ft.DataColumn(ft.Text("Fasilitas")),
            ft.DataColumn(ft.Text("Harga")),
            ft.DataColumn(ft.Text("Status")),
            ft.DataColumn(ft.Text("Aksi")),
        ],
        rows=[]
    )

    # ft.Container untuk scroll:
    # - Vertical: ft.Column(scroll=AUTO)
    # - Horizontal: ft.Row(scroll=AUTO) membungkus ft.DataTable
    tabel_scroll_area = ft.Column(
        expand=True,
        scroll=ft.ScrollMode.AUTO,     # ✅ scroll atas-bawah
        controls=[
            ft.Row(
                scroll=ft.ScrollMode.AUTO,  # ✅ scroll kiri-kanan
                controls=[tabel_kamar]
            )
        ]
    )

    def muat_data_kamar():
        tabel_kamar.rows.clear()
        db = koneksi_database()
        cur = db.cursor()

        keyword = f"%{keyword_cari['value']}%"

        # total data
        cur.execute("SELECT COUNT(*) FROM data_kamar WHERE nomor_kamar LIKE %s", (keyword,))
        total_data["value"] = cur.fetchone()[0]

        offset = (current_page["value"] - 1) * limit_per_page
        cur.execute(
            "SELECT * FROM data_kamar WHERE nomor_kamar LIKE %s LIMIT %s OFFSET %s",
            (keyword, limit_per_page, offset)
        )

        rows = cur.fetchall()
        db.close()

        for index, row in enumerate(rows):
            no_urut = offset + index + 1

            fasilitas_text = row[4] if row[4] is not None else ""

            fasilitas_cell = ft.DataCell(
                ft.Container(
                    width=260,
                    content=ft.Text(
                        fasilitas_text,
                        max_lines=1,                      # 1 baris biar rapi
                        overflow=ft.TextOverflow.ELLIPSIS,   # jadi "..."
                        tooltip=fasilitas_text            # hover untuk lihat full
                    ),
                )
            )

            tabel_kamar.rows.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(no_urut)),
                    ft.DataCell(ft.Text(str(row[1]))),  # nomor_kamar
                    ft.DataCell(ft.Text(str(row[2]))),  # tipe_kamar
                    ft.DataCell(ft.Text(str(row[3]))),  # lantai
                    fasilitas_cell,               # fasilitas (wrap)
                    ft.DataCell(ft.Text(f"Rp {float(row[5]):,.0f}" if row[5] is not None else "Rp 0")),
                    ft.DataCell(ft.Text(str(row[6]))),  # status_huni
                    ft.DataCell(ft.Row([
                        ft.IconButton(ft.Icons.EDIT, on_click=lambda e, r=row: edit_kamar(r)),
                        ft.IconButton(ft.Icons.DELETE, icon_color="red", on_click=lambda e, i=row[0]: hapus_kamar(i)),
                    ]))
                ])
            )

        page.update()

    muat_data_kamar()

    # ================= LAYOUT =================
    form_column = ft.Column(
        spacing=15,
        controls=[
            ft.Text("Form Entri Kamar", size=18, weight="bold"),
            input_nomor,
            tipe_container,
            input_lantai,
            input_fasilitas,
            input_harga,
            status_container,
            ft.Row([
                ft.Button("Simpan", icon=ft.Icons.SAVE, bgcolor=ft.Colors.TEAL, color=ft.Colors.WHITE, on_click=simpan_kamar),
                ft.Button("Batal", icon=ft.Icons.CLEAR, bgcolor=ft.Colors.BLACK, color=ft.Colors.WHITE, on_click=lambda e: bersihkan_form()),
            ]),
            notif_kamar,
        ],
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
                            ft.Text("Daftar Kamar Kos", size=18, weight="bold"),
                            input_cari,
                            ft.Divider(),
                            tabel_scroll_area,  # ✅ tabel dengan scroll horizontal+vertical
                        ]
                    )
                )
            ]
        )
    )
