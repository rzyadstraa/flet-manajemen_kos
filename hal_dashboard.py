import flet as ft
import flet_charts as fc
import pymysql

# Fungsi koneksi ke database manajemen kos
def koneksi_database():
    return pymysql.connect(
        host="localhost", 
        user="root", 
        password="", 
        database="db_manajemenkos"
    )

def dashboard_view():
    # --- PENGAMBILAN DATA DARI DATABASE ---
    try:
        db = koneksi_database()
        cur = db.cursor()
        
        # 1. Hitung statistik kamar (Terisi & Kosong)
        cur.execute("SELECT COUNT(*) FROM data_kamar WHERE status_huni='Terisi'")
        terisi = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM data_kamar WHERE status_huni='Kosong'")
        kosong = cur.fetchone()[0]
        
        # 2. Hitung total penghuni yang terdaftar
        cur.execute("SELECT COUNT(*) FROM data_penghuni")
        total_penghuni = cur.fetchone()[0]
        
        # 3. Hitung total pendapatan dari tagihan yang sudah lunas
        cur.execute("SELECT SUM(total_tagihan) FROM tagihan_bulanan WHERE status_lunas='Lunas'")
        pendapatan = cur.fetchone()[0] or 0
        db.close()
    except Exception as e:
        print(f"Error Database: {e}")
        terisi = kosong = total_penghuni = pendapatan = 0

    # --- KOMPONEN KARTU STATISTIK (Helper Function) ---
    def _create_stat_card(title, value, icon, color, subtitle):
        return ft.Container(
            col={"sm": 12, "md": 3}, # Responsif: 4 kartu dalam satu baris desktop
            padding=20,
            bgcolor="white",
            border_radius=15,
            shadow=ft.BoxShadow(blur_radius=15, color="black12", offset=ft.Offset(0, 5)),
            content=ft.Column([
                ft.Row([
                    ft.Container(
                        content=ft.Icon(icon, color=color, size=30),
                        bgcolor=f"{color}15", # Efek warna transparan di belakang ikon
                        padding=10,
                        border_radius=10,
                    ),
                    ft.Column([
                        ft.Text(title, size=14, color="bluegrey400", weight="w500"),
                        ft.Text(value, size=24, weight="bold"),
                    ], spacing=2),
                ], alignment="spaceBetween"),
                ft.Divider(height=15, color="transparent"),
                ft.Text(subtitle, size=12, color="bluegrey300")
            ])
        )

    # --- LAYOUT UTAMA DASHBOARD ---
    return ft.Container(
        expand=True,
        padding=25,
        content=ft.Column(
            scroll="auto",
            spacing=30,
            controls=[
                # Bagian Header
                ft.Column([
                    ft.Text("Ringkasan Operasional", size=28, weight="bold"),
                    ft.Text("Data diperbarui secara otomatis dari database sistem.", color="grey"),
                ]),

                # ft.Row Kartu Statistik (4 Indikator Utama)
                ft.ResponsiveRow(
                    spacing=20,
                    controls=[
                        _create_stat_card("Kamar Terisi", f"{terisi}", ft.Icons.BED, "green", "Unit saat ini"),
                        _create_stat_card("Kamar Kosong", f"{kosong}", ft.Icons.MEETING_ROOM, "orange", "Tersedia"),
                        _create_stat_card("Total Penghuni", f"{total_penghuni}", ft.Icons.PEOPLE, "purple", "Jiwa terdaftar"),
                        _create_stat_card("Omzet Lunas", f"Rp {pendapatan:,.0f}", ft.Icons.ACCOUNT_BALANCE_WALLET, "blue", "Bulan ini"),
                    ]
                ),

                # Bagian Grafik Analitik
                ft.ResponsiveRow(
                    spacing=20,
                    controls=[
                        # Chart 1: Bar Chart Kapasitas
                        ft.Container(
                            col={"md": 7},
                            padding=25,
                            bgcolor="white",
                            border_radius=15,
                            shadow=ft.BoxShadow(blur_radius=15, color="black12"),
                            content=ft.Column([
                                ft.Text("Perbandingan Data Kamar & Penghuni", size=18, weight="bold"),
                                ft.Container(height=20),
                                fc.BarChart(
                                    groups=[
                                        fc.BarChartGroup(x=1, rods=[fc.BarChartRod(from_y=0, to_y=terisi, width=30, color="green", border_radius=5)]),
                                        fc.BarChartGroup(x=2, rods=[fc.BarChartRod(from_y=0, to_y=kosong, width=30, color="orange", border_radius=5)]),
                                        fc.BarChartGroup(x=3, rods=[fc.BarChartRod(from_y=0, to_y=total_penghuni, width=30, color="purple", border_radius=5)]),
                                    ],
                                    max_y=max(terisi, kosong, total_penghuni) + 5,
                                    height=300,
                                ),
                            ])
                        ),
                        # Chart 2: Donut Chart Proporsi Hunian
                        ft.Container(
                            col={"md": 5},
                            padding=25,
                            bgcolor="white",
                            border_radius=15,
                            shadow=ft.BoxShadow(blur_radius=15, color="black12"),
                            content=ft.Column(
                                horizontal_alignment="center",
                                controls=[
                                    ft.Text("Proporsi Hunian Kamar", size=18, weight="bold"),
                                    ft.Container(height=30),
                                    fc.PieChart(
                                        sections=[
                                            fc.PieChartSection(value=terisi, color="green", title=f"{terisi}", radius=50, title_style=ft.TextStyle(weight="bold", color="white")),
                                            fc.PieChartSection(value=kosong, color="orange", title=f"{kosong}", radius=50, title_style=ft.TextStyle(weight="bold", color="white")),
                                        ],
                                        center_space_radius=45,
                                        height=250,
                                    ),
                                    ft.Row([
                                        ft.Icon(ft.Icons.CIRCLE, color="green", size=12), ft.Text("Terisi", size=12),
                                        ft.Container(width=10),
                                        ft.Icon(ft.Icons.CIRCLE, color="orange", size=12), ft.Text("Kosong", size=12),
                                    ], alignment="center")
                                ]
                            )
                        ),
                    ]
                ),
            ]
        )
    )