import pymysql
import flet as ft
import pandas as pd
from sklearn.linear_model import LinearRegression
import warnings

warnings.filterwarnings("ignore", category=UserWarning)

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
# 🔹 Helper format rupiah (tanpa nambah nol)
# =========================================================
def rupiah(x):
    try:
        v = float(x)
        return f"Rp {v:,.0f}".replace(",", ".")
    except:
        return f"Rp {x}"

def to_float(v):
    """
    Aman untuk:
    - "1500000"
    - "1500000.0"
    - "1.500.000"
    - "1.500.000,50"
    """
    if v is None:
        return 0.0
    s = str(v).strip()
    if s == "":
        return 0.0

    # kalau format desimal normal: 1500000.0 / 1500000.50
    if s.count(".") == 1 and s.replace(".", "").isdigit():
        return float(s)

    # kalau format indonesia: 1.500.000 atau 1.500.000,50
    s = s.replace(".", "").replace(",", ".")
    try:
        return float(s)
    except:
        return 0.0

# =========================================================
# 🔹 HALAMAN KELOLA TAGIHAN & AI (FULL)
# =========================================================
def kelola_tagihan_view(page: ft.Page):
    selected_id = {"id": None}

    # -------------------- builder dropdown --------------------
    def buat_dropdown_kamar():
        db = koneksi_database()
        cur = db.cursor()
        cur.execute("SELECT id_kamar, nomor_kamar, tipe_kamar FROM data_kamar ORDER BY nomor_kamar ASC")
        opts = [ft.dropdown.Option(key=str(r[0]), text=f"Kamar {r[1]} ({r[2]})") for r in cur.fetchall()]
        db.close()
        return ft.Dropdown(label="Pilih Kamar", options=opts, width=360, leading_icon=ft.Icons.BED)

    def buat_dropdown_penghuni():
        db = koneksi_database()
        cur = db.cursor()
        cur.execute("SELECT id_penghuni, nama FROM data_penghuni ORDER BY nama ASC")
        opts = [ft.dropdown.Option(key=str(r[0]), text=r[1]) for r in cur.fetchall()]
        db.close()
        return ft.Dropdown(label="Pilih Penghuni", options=opts, width=360, leading_icon=ft.Icons.PERSON)

    def buat_dropdown_status():
        return ft.Dropdown(
            label="Status Bayar",
            options=[ft.dropdown.Option("Lunas"), ft.dropdown.Option("Belum Lunas")],
            width=360,
            leading_icon=ft.Icons.CHECK_CIRCLE
        )

    # -------------------- komponen input (dibungkus container biar gampang reset) --------------------
    dropdown_kamar = buat_dropdown_kamar()
    dropdown_penghuni = buat_dropdown_penghuni()
    dropdown_status = buat_dropdown_status()

    container_kamar = ft.Container(content=dropdown_kamar)
    container_penghuni = ft.Container(content=dropdown_penghuni)
    container_status = ft.Container(content=dropdown_status)

    input_bulan = ft.TextField(label="Bulan (1-12)", width=360, prefix_icon=ft.Icons.CALENDAR_MONTH)
    input_tahun = ft.TextField(label="Tahun (YYYY)", width=360, prefix_icon=ft.Icons.DATE_RANGE)

    input_sewa = ft.TextField(label="Biaya Sewa", width=360, prefix_icon=ft.Icons.MONEY)
    input_listrik = ft.TextField(label="Biaya Listrik", width=360, prefix_icon=ft.Icons.ELECTRICAL_SERVICES)
    input_air = ft.TextField(label="Biaya Air", width=360, prefix_icon=ft.Icons.WATER_DROP)
    input_sampah = ft.TextField(label="Biaya Sampah", width=360, prefix_icon=ft.Icons.DELETE_OUTLINE)

    input_total = ft.TextField(
        label="Total Tagihan (Otomatis)",
        width=360,
        prefix_icon=ft.Icons.RECEIPT_LONG,
        read_only=True
    )

    notif_tagihan = ft.Text("")

    # -------------------- total otomatis --------------------
    def hitung_total_otomatis(e=None):
        total = (
            to_float(input_sewa.value)
            + to_float(input_listrik.value)
            + to_float(input_air.value)
            + to_float(input_sampah.value)
        )
        input_total.value = rupiah(total)
        page.update()

    input_sewa.on_change = hitung_total_otomatis
    input_listrik.on_change = hitung_total_otomatis
    input_air.on_change = hitung_total_otomatis
    input_sampah.on_change = hitung_total_otomatis

    # -------------------- auto isi sewa dari data_kamar --------------------
    def isi_sewa_otomatis(e):
        dd = container_kamar.content
        if not dd.value:
            return
        db = koneksi_database()
        cur = db.cursor()
        cur.execute("SELECT harga_per_bulan FROM data_kamar WHERE id_kamar=%s", (dd.value,))
        r = cur.fetchone()
        db.close()
        if r:
            # ✅ pastikan tidak jadi "1500000.0"
            input_sewa.value = str(int(float(r[0])))
            hitung_total_otomatis()

    container_kamar.content.on_change = isi_sewa_otomatis

    # -------------------- validasi --------------------
    def validasi_input():
        dd_kamar = container_kamar.content
        dd_penghuni = container_penghuni.content
        dd_status = container_status.content

        if not dd_kamar.value or not dd_penghuni.value:
            return False, "Pilih kamar dan penghuni."
        try:
            b = int(input_bulan.value)
            if b < 1 or b > 12:
                return False, "Bulan harus 1-12."
        except:
            return False, "Bulan harus angka (1-12)."
        try:
            t = int(input_tahun.value)
            if t < 2000 or t > 2100:
                return False, "Tahun tidak valid."
        except:
            return False, "Tahun harus angka (YYYY)."
        if not dd_status.value:
            return False, "Pilih status bayar."
        return True, ""

    # -------------------- AI prediksi listrik (per kamar, prediksi bulan depan) --------------------
    def prediksi_listrik_ai(e):
        try:
            dd_kamar = container_kamar.content
            if not dd_kamar.value:
                dlg = ft.AlertDialog(
                    title=ft.Text("Info"),
                    content=ft.Text("Pilih kamar dulu untuk prediksi."),
                    actions=[ft.TextButton("Tutup", on_click=lambda e: page.close(dlg))]
                )
                page.open(dlg)
                return

            id_kamar = int(dd_kamar.value)

            db = koneksi_database()
            df = pd.read_sql(
                """
                SELECT bulan_tagihan, tahun_tagihan, biaya_listrik
                FROM tagihan_bulanan
                WHERE id_kamar = %s
                ORDER BY tahun_tagihan ASC, bulan_tagihan ASC
                """,
                db,
                params=[id_kamar]
            )
            db.close()

            if len(df) < 2:
                dlg = ft.AlertDialog(
                    title=ft.Text("Info AI"),
                    content=ft.Text("Minimal 2 data historis diperlukan untuk prediksi (lebih bagus 3+)."),
                    actions=[ft.TextButton("Tutup", on_click=lambda e: page.close(dlg))]
                )
                page.open(dlg)
                return

            df["t"] = df["tahun_tagihan"] * 12 + df["bulan_tagihan"]
            X = df[["t"]].values
            y = df["biaya_listrik"].astype(float).values

            model = LinearRegression().fit(X, y)

            t_last = int(df["t"].max())
            t_next = t_last + 1
            pred = float(model.predict([[t_next]])[0])
            if pred < 0:
                pred = 0

            tahun_pred = t_next // 12
            bulan_pred = t_next % 12
            if bulan_pred == 0:
                bulan_pred = 12
                tahun_pred -= 1

            def isi_ke_form(ev):
                input_listrik.value = str(int(pred))
                hitung_total_otomatis()
                page.close(dlg_hasil)

            dlg_hasil = ft.AlertDialog(
                title=ft.Text("Hasil Prediksi AI"),
                content=ft.Text(f"Prediksi listrik kamar ID {id_kamar} untuk {bulan_pred}/{tahun_pred}:\n\n{rupiah(pred)}"),
                actions=[
                    ft.TextButton("Isi ke Form (Listrik)", on_click=isi_ke_form),
                    ft.TextButton("Tutup", on_click=lambda ev: page.close(dlg_hasil))
                ]
            )
            page.open(dlg_hasil)

        except Exception as ex:
            dlg = ft.AlertDialog(
                title=ft.Text("Error"),
                content=ft.Text(f"Prediksi gagal:\n{ex}"),
                actions=[ft.TextButton("Tutup", on_click=lambda e: page.close(dlg))]
            )
            page.open(dlg)

    # -------------------- CRUD --------------------
    def simpan_tagihan(e):
        ok, msg = validasi_input()
        if not ok:
            notif_tagihan.value = f"⚠️ {msg}"
            notif_tagihan.color = ft.Colors.ORANGE
            page.update()
            return

        try:
            dd_kamar = container_kamar.content
            dd_penghuni = container_penghuni.content
            dd_status = container_status.content

            total = (
                to_float(input_sewa.value)
                + to_float(input_listrik.value)
                + to_float(input_air.value)
                + to_float(input_sampah.value)
            )

            db = koneksi_database()
            cur = db.cursor()

            if selected_id["id"]:
                cur.execute("""
                    UPDATE tagihan_bulanan
                    SET id_kamar=%s, id_penghuni=%s, bulan_tagihan=%s, tahun_tagihan=%s,
                        biaya_sewa=%s, biaya_listrik=%s, biaya_air=%s, biaya_sampah=%s,
                        total_tagihan=%s, status_lunas=%s
                    WHERE id_tagihan=%s
                """, (
                    dd_kamar.value, dd_penghuni.value,
                    int(input_bulan.value), int(input_tahun.value),
                    to_float(input_sewa.value), to_float(input_listrik.value),
                    to_float(input_air.value), to_float(input_sampah.value),
                    total, dd_status.value,
                    selected_id["id"]
                ))
                notif_tagihan.value = "✅ Tagihan diperbarui"
            else:
                cur.execute("""
                    INSERT INTO tagihan_bulanan
                        (id_kamar, id_penghuni, bulan_tagihan, tahun_tagihan,
                         biaya_sewa, biaya_listrik, biaya_air, biaya_sampah,
                         total_tagihan, status_lunas)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                """, (
                    dd_kamar.value, dd_penghuni.value,
                    int(input_bulan.value), int(input_tahun.value),
                    to_float(input_sewa.value), to_float(input_listrik.value),
                    to_float(input_air.value), to_float(input_sampah.value),
                    total, dd_status.value
                ))
                notif_tagihan.value = "✅ Tagihan baru disimpan"

            db.commit()
            db.close()

            notif_tagihan.color = ft.Colors.GREEN
            reset_form()
            muat_data_tagihan()
            page.update()

        except Exception as ex:
            notif_tagihan.value = f"❌ Error: {ex}"
            notif_tagihan.color = ft.Colors.RED
            page.update()

    def edit_tagihan(row):
        # row: sesuai SELECT eksplisit di muat_data_tagihan()
        selected_id["id"] = row[0]

        container_kamar.content.value = str(row[1])      # id_kamar
        container_penghuni.content.value = str(row[4])   # id_penghuni

        input_bulan.value = str(row[6])
        input_tahun.value = str(row[7])

        # ✅ pastikan tidak jadi 1500000.0
        input_sewa.value = str(int(float(row[8])))
        input_listrik.value = str(int(float(row[9])))
        input_air.value = str(int(float(row[10])))
        input_sampah.value = str(int(float(row[11])))

        container_status.content.value = str(row[13])
        hitung_total_otomatis()
        page.update()

    def hapus_tagihan(id_t):
        try:
            db = koneksi_database()
            cur = db.cursor()
            cur.execute("DELETE FROM tagihan_bulanan WHERE id_tagihan=%s", (id_t,))
            db.commit()
            db.close()
            muat_data_tagihan()
        except Exception as ex:
            notif_tagihan.value = f"❌ Gagal hapus: {ex}"
            notif_tagihan.color = ft.Colors.RED
            page.update()

    # -------------------- Reset form (pakai container rebuild dropdown supaya benar-benar kosong) --------------------
    def reset_form(e=None):
        nonlocal dropdown_kamar, dropdown_penghuni, dropdown_status

        input_bulan.value = ""
        input_tahun.value = ""
        input_sewa.value = ""
        input_listrik.value = ""
        input_air.value = ""
        input_sampah.value = ""
        input_total.value = ""
        notif_tagihan.value = ""
        selected_id["id"] = None

        # rebuild dropdown => benar-benar kembali placeholder kosong
        dropdown_kamar = buat_dropdown_kamar()
        dropdown_penghuni = buat_dropdown_penghuni()
        dropdown_status = buat_dropdown_status()

        dropdown_kamar.on_change = isi_sewa_otomatis

        container_kamar.content = dropdown_kamar
        container_penghuni.content = dropdown_penghuni
        container_status.content = dropdown_status

        page.update()

    # -------------------- ft.DataTable (biar tidak ada space kosong di atas) --------------------
    tabel_tagihan = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Kamar")),
            ft.DataColumn(ft.Text("Tipe")),
            ft.DataColumn(ft.Text("Penghuni")),
            ft.DataColumn(ft.Text("Periode")),
            ft.DataColumn(ft.Text("Sewa")),
            ft.DataColumn(ft.Text("Listrik")),
            ft.DataColumn(ft.Text("Air")),
            ft.DataColumn(ft.Text("Sampah")),
            ft.DataColumn(ft.Text("Total")),
            ft.DataColumn(ft.Text("Status")),
            ft.DataColumn(ft.Text("Aksi")),
        ],
        rows=[]
    )

    def muat_data_tagihan():
        tabel_tagihan.rows.clear()
        db = koneksi_database()
        cur = db.cursor()
        cur.execute("""
            SELECT
                t.id_tagihan,
                t.id_kamar,
                k.nomor_kamar,
                k.tipe_kamar,
                t.id_penghuni,
                p.nama,
                t.bulan_tagihan,
                t.tahun_tagihan,
                t.biaya_sewa,
                t.biaya_listrik,
                t.biaya_air,
                t.biaya_sampah,
                t.total_tagihan,
                t.status_lunas
            FROM tagihan_bulanan t
            JOIN data_kamar k ON t.id_kamar = k.id_kamar
            JOIN data_penghuni p ON t.id_penghuni = p.id_penghuni
            ORDER BY t.id_tagihan DESC
        """)
        rows = cur.fetchall()
        db.close()

        for row in rows:
            tabel_tagihan.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(row[2]))),
                        ft.DataCell(ft.Text(str(row[3]))),
                        ft.DataCell(ft.Text(str(row[5]))),
                        ft.DataCell(ft.Text(f"{row[6]}/{row[7]}")),
                        ft.DataCell(ft.Text(rupiah(row[8]))),
                        ft.DataCell(ft.Text(rupiah(row[9]))),
                        ft.DataCell(ft.Text(rupiah(row[10]))),
                        ft.DataCell(ft.Text(rupiah(row[11]))),
                        ft.DataCell(ft.Text(rupiah(row[12]))),
                        ft.DataCell(ft.Text(str(row[13]))),
                        ft.DataCell(
                            ft.Row(
                                controls=[
                                    ft.IconButton(ft.Icons.EDIT, on_click=lambda e, r=row: edit_tagihan(r)),
                                    ft.IconButton(ft.Icons.DELETE, icon_color="red", on_click=lambda e, i=row[0]: hapus_tagihan(i)),
                                ],
                                spacing=0
                            )
                        ),
                    ]
                )
            )
        page.update()

    muat_data_tagihan()

    # -------------------- Layout form kiri --------------------
    form_input = ft.Column(
        spacing=12,
        scroll=ft.ScrollMode.AUTO,
        controls=[
            ft.Text("Entri Tagihan Bulanan", size=18, weight="bold"),
            container_kamar,
            container_penghuni,
            input_bulan,
            input_tahun,
            input_sewa,
            input_listrik,
            input_air,
            input_sampah,
            input_total,
            container_status,
            ft.Row(
                controls=[
                    ft.Button("Simpan", icon=ft.Icons.SAVE, bgcolor=ft.Colors.TEAL, color=ft.Colors.WHITE, on_click=simpan_tagihan),
                    ft.Button("Prediksi AI (Listrik)", icon=ft.Icons.AUTO_GRAPH, on_click=prediksi_listrik_ai),
                    ft.OutlinedButton("Reset", icon=ft.Icons.RESTART_ALT, on_click=reset_form),
                ],
                wrap=True
            ),
            notif_tagihan
        ]
    )

    # -------------------- Layout tabel kanan (FIX: tidak ada space kosong besar) --------------------
    # Penyebab space besar: ft.Column tanpa expand/vertical alignment, lalu child ft.DataTable tidak "nempel atas".
    # Solusi: ft.Column(expand=True) + taruh tabel dalam ft.Container(expand=True, alignment=ft.Alignment.TOP_LEFT)
        # -------------------- Layout tabel kanan (FIX: bisa scroll bawah & kanan) --------------------
    tabel_area = ft.Column(
        expand=True,
        spacing=10,
        controls=[
            ft.Text("Riwayat Pembayaran Kos", size=18, weight="bold"),
            ft.Divider(height=1),

            # ✅ wadah utama yang punya tinggi + scroll vertikal
            ft.Container(
                expand=True,
                alignment=ft.Alignment.TOP_LEFT,
                content=ft.Column(
                    expand=True,
                    scroll=ft.ScrollMode.AUTO,  # ✅ scroll bawah-atas
                    controls=[
                        ft.Row(
                            scroll=ft.ScrollMode.AUTO,  # ✅ scroll kanan-kiri
                            controls=[tabel_tagihan],
                        )
                    ],
                ),
            ),
        ],
    )

    return ft.Container(
        expand=True,
        padding=20,
        content=ft.Row(
            spacing=20,
            controls=[
                ft.Container(
                    width=420,
                    padding=20,
                    bgcolor="white",
                    border_radius=20,
                    shadow=ft.BoxShadow(blur_radius=20, color="black12"),
                    content=form_input
                ),
                ft.Container(
                    expand=True,
                    padding=20,
                    bgcolor="white",
                    border_radius=20,
                    shadow=ft.BoxShadow(blur_radius=20, color="black12"),
                    content=tabel_area
                )
            ]
        )
    )