import flet as ft
import mysql.connector
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
import os


def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="db_manajemenkos"
    )


def kelola_laporan_view(page: ft.Page):

    # ---------- Ambil data tagihan dari database ----------
    def load_data(nomor_kamar_filter=None):
        conn = get_connection()
        cursor = conn.cursor()

        base_sql = """
            SELECT
                t.id_tagihan,
                k.nomor_kamar,
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
        """

        params = []
        if nomor_kamar_filter and str(nomor_kamar_filter).strip() != "":
            base_sql += " WHERE k.nomor_kamar = %s"
            params.append(str(nomor_kamar_filter).strip())

        base_sql += " ORDER BY t.tahun_tagihan DESC, t.bulan_tagihan DESC"

        cursor.execute(base_sql, tuple(params))
        rows = cursor.fetchall()
        conn.close()
        return rows

    def rupiah(x):
        try:
            return f"Rp {float(x):,.0f}".replace(",", ".")
        except:
            return str(x)

    # ---------- Refresh tabel preview ----------
    def refresh_table():
        table.rows.clear()
        data = load_data(txt_filter.value)

        for row in data:
            table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(row[0]))),         # id_tagihan
                        ft.DataCell(ft.Text(str(row[1]))),         # nomor_kamar
                        ft.DataCell(ft.Text(str(row[2]))),         # nama penghuni
                        ft.DataCell(ft.Text(str(row[3]))),         # bulan
                        ft.DataCell(ft.Text(str(row[4]))),         # tahun
                        ft.DataCell(ft.Text(rupiah(row[5]))),      # sewa
                        ft.DataCell(ft.Text(rupiah(row[6]))),      # listrik
                        ft.DataCell(ft.Text(rupiah(row[7]))),      # air
                        ft.DataCell(ft.Text(rupiah(row[8]))),      # sampah
                        ft.DataCell(ft.Text(rupiah(row[9]))),      # total
                        ft.DataCell(ft.Text(str(row[10]))),        # status
                    ]
                )
            )
        page.update()

    # ---------- Cetak PDF (LANDSCAPE) ----------
    def cetak_laporan(e):
        data = load_data(txt_filter.value)

        if not data:
            page.snack_bar = ft.SnackBar(ft.Text("⚠️ Tidak ada data untuk dicetak"), bgcolor=ft.Colors.RED)
            page.snack_bar.open = True
            page.update()
            return

        file_name = "laporan_tagihan_kos_landscape.pdf"
        pdf = SimpleDocTemplate(
            file_name,
            pagesize=landscape(A4),
            leftMargin=20,
            rightMargin=20,
            topMargin=20,
            bottomMargin=20,
        )

        styles = getSampleStyleSheet()
        elements = []

        elements.append(
            Paragraph(
                "<para align='center'><font size='18'><b>SMART BOARDING HOUSE</b></font></para>",
                styles["Normal"]
            )
        )
        elements.append(Spacer(1, 8))
        elements.append(
            Paragraph(
                "<para align='center'><font size='11'>Laporan Rekapitulasi Pembayaran Kos</font></para>",
                styles["Normal"]
            )
        )
        elements.append(Spacer(1, 16))

        table_data = [[
            "ID", "Kamar", "Penghuni", "Bulan", "Tahun",
            "Sewa", "Listrik", "Air", "Sampah", "Total", "Status"
        ]]

        for row in data:
            table_data.append([
                row[0],
                row[1],
                row[2],
                row[3],
                row[4],
                rupiah(row[5]),
                rupiah(row[6]),
                rupiah(row[7]),
                rupiah(row[8]),
                rupiah(row[9]),
                row[10],
            ])

        col_widths = [35, 45, 120, 40, 45, 70, 70, 60, 70, 75, 70]

        table_pdf = Table(table_data, repeatRows=1, colWidths=col_widths)
        table_pdf.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2563eb")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 9),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("FONTSIZE", (0, 1), (-1, -1), 8),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.whitesmoke, colors.lightgrey]),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 6),
            ("TOPPADDING", (0, 0), (-1, 0), 6),
        ]))

        elements.append(table_pdf)
        pdf.build(elements)

        try:
            os.startfile(file_name)
        except:
            page.snack_bar = ft.SnackBar(ft.Text(f"✅ PDF tersimpan: {file_name}"), bgcolor=ft.Colors.GREEN)
            page.snack_bar.open = True
            page.update()

    # ================= UI =================
    txt_filter = ft.TextField(label="Filter Nomor Kamar", width=220, prefix_icon=ft.Icons.SEARCH)
    btn_filter = ft.Button("Tampilkan", icon=ft.Icons.FILTER_ALT, on_click=lambda e: refresh_table())
    btn_cetak = ft.Button(
        "Cetak PDF",
        icon=ft.Icons.PRINT,
        bgcolor=ft.Colors.BLUE,
        color=ft.Colors.WHITE,
        on_click=cetak_laporan
    )

    table = ft.DataTable(
        # jangan pakai expand=True di ft.DataTable, biar ft.Row scroll horizontal jalan normal
        columns=[
            ft.DataColumn(ft.Text("ID")),
            ft.DataColumn(ft.Text("Kamar")),
            ft.DataColumn(ft.Text("Penghuni")),
            ft.DataColumn(ft.Text("Bulan")),
            ft.DataColumn(ft.Text("Tahun")),
            ft.DataColumn(ft.Text("Sewa")),
            ft.DataColumn(ft.Text("Listrik")),
            ft.DataColumn(ft.Text("Air")),
            ft.DataColumn(ft.Text("Sampah")),
            ft.DataColumn(ft.Text("Total")),
            ft.DataColumn(ft.Text("Status")),
        ],
        rows=[]
    )

    # ✅ SCROLL FIX:
    # - ft.Row(scroll=...) => scroll kanan-kiri (horizontal)
    # - ft.Column(scroll=...) => scroll atas-bawah (vertical) kalau rows banyak
    table_scroll = ft.Row(
        controls=[
            ft.Column(
                controls=[table],
                scroll=ft.ScrollMode.AUTO,   # ✅ vertical scroll
                expand=True
            )
        ],
        scroll=ft.ScrollMode.AUTO,           # ✅ horizontal scroll
        expand=True
    )

    refresh_table()

    return ft.Container(
        expand=True,
        content=ft.Column(
            expand=True,
            controls=[
                ft.Container(
                    padding=15,
                    bgcolor=ft.Colors.WHITE,
                    border_radius=12,
                    content=ft.Row(
                        alignment="spaceBetween",
                        controls=[
                            ft.Row([txt_filter, btn_filter]),
                            btn_cetak
                        ]
                    )
                ),
                ft.Container(
                    expand=True,
                    padding=10,
                    bgcolor=ft.Colors.WHITE,
                    border_radius=12,
                    clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
                    content=table_scroll
                )
            ]
        )
    )
