import flet as ft

from hal_dashboard import dashboard_view
from hal_login import login_view
from hal_profil import profil_view
from hal_tentang import tentang_view
from hal_kamar import kelola_kamar_view
from hal_penghuni import kelola_penghuni_view
from hal_tagihan import kelola_tagihan_view
from hal_laporan import kelola_laporan_view


def main(page: ft.Page):
    page.title = "Smart Boarding House - Manajemen Kos"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.bgcolor = "#e8ecf3"
    page.window.width = 1280
    page.window.height = 800
    page.window.maximized = True

    session_user = {"username": None, "hak_akses": None}

    def tampil_hallogin():
        page.clean()
        page.add(login_view(page, tampil_halpengguna))
        page.update()

    def proses_logout():
        session_user["username"] = None
        session_user["hak_akses"] = None
        tampil_hallogin()

    def tampil_halpengguna(username, hak_akses):
        session_user["username"] = username
        session_user["hak_akses"] = hak_akses

        page.clean()
        content = ft.Column(expand=True)

        is_pemilik = str(hak_akses).lower() == "pemilik"

        admin_destinations = [
            ft.NavigationRailDestination(icon=ft.Icons.DASHBOARD, label="Beranda"),
            ft.NavigationRailDestination(icon=ft.Icons.BED, label="Kelola Kamar"),
            ft.NavigationRailDestination(icon=ft.Icons.PEOPLE, label="Kelola Penghuni"),
            ft.NavigationRailDestination(icon=ft.Icons.RECEIPT_LONG, label="Total Tagihan"),
            ft.NavigationRailDestination(icon=ft.Icons.DESCRIPTION, label="Laporan PDF"),
            ft.NavigationRailDestination(icon=ft.Icons.PERSON, label="Profil"),
            ft.NavigationRailDestination(icon=ft.Icons.INFO, label="Tentang"),
            ft.NavigationRailDestination(icon=ft.Icons.LOGOUT, label="Logout"),
        ]

        pemilik_destinations = [
            ft.NavigationRailDestination(icon=ft.Icons.DASHBOARD, label="Beranda"),
            ft.NavigationRailDestination(icon=ft.Icons.RECEIPT_LONG, label="Total Tagihan"),
            ft.NavigationRailDestination(icon=ft.Icons.DESCRIPTION, label="Laporan PDF"),
            ft.NavigationRailDestination(icon=ft.Icons.PERSON, label="Profil"),
            ft.NavigationRailDestination(icon=ft.Icons.INFO, label="Tentang"),
            ft.NavigationRailDestination(icon=ft.Icons.LOGOUT, label="Logout"),
        ]

        destinations = pemilik_destinations if is_pemilik else admin_destinations

        rail = ft.NavigationRail(
            selected_index=0,
            label_type=ft.NavigationRailLabelType.ALL,
            extended=True,
            destinations=destinations,
        )

        def change(e):
            content.controls.clear()

            if is_pemilik:
                if rail.selected_index == 0:
                    content.controls.append(
                        ft.Column(
                            spacing=10, expand=True,
                            controls=[
                                ft.Text(
                                    f"👋 Selamat Datang, {session_user['username']} ({session_user['hak_akses']})",
                                    size=18, weight=ft.FontWeight.BOLD
                                ),
                                dashboard_view(),
                            ],
                        )
                    )
                elif rail.selected_index == 1:
                    content.controls.append(
                        ft.Column(
                            spacing=10, expand=True,
                            controls=[
                                ft.Text("💻 Tagihan Bulanan & Prediksi AI", size=18, weight=ft.FontWeight.BOLD),
                                kelola_tagihan_view(page),
                            ],
                        )
                    )
                elif rail.selected_index == 2:
                    content.controls.append(
                        ft.Column(
                            spacing=10, expand=True,
                            controls=[
                                ft.Text("💻 Cetak Laporan Keuangan", size=18, weight=ft.FontWeight.BOLD),
                                kelola_laporan_view(page),
                            ],
                        )
                    )
                elif rail.selected_index == 3:
                    content.controls.append(profil_view(page, session_user["username"], session_user["hak_akses"]))
                elif rail.selected_index == 4:
                    content.controls.append(tentang_view())
                elif rail.selected_index == 5:
                    content.controls.append(
                        ft.Container(
                            alignment=ft.Alignment.CENTER,
                            content=ft.Container(
                                width=420, padding=25, bgcolor=ft.Colors.WHITE, border_radius=16,
                                shadow=ft.BoxShadow(blur_radius=20, color=ft.Colors.BLACK_12),
                                content=ft.Column(
                                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                    spacing=20,
                                    controls=[
                                        ft.Icon(ft.Icons.LOGOUT, size=60, color=ft.Colors.RED_400),
                                        ft.Text("Konfirmasi Logout", size=22, weight=ft.FontWeight.BOLD),
                                        ft.Text("Apakah Anda yakin ingin keluar?", text_align=ft.TextAlign.CENTER),
                                        ft.Row(
                                            alignment=ft.MainAxisAlignment.SPACE_EVENLY,
                                            controls=[
                                                ft.OutlinedButton(
                                                    "Batal",
                                                    on_click=lambda e: (setattr(rail, "selected_index", 0), change(None))
                                                ),
                                                ft.Button(
                                                    "Logout",
                                                    bgcolor=ft.Colors.RED,
                                                    color=ft.Colors.WHITE,
                                                    on_click=lambda e: proses_logout(),
                                                ),
                                            ],
                                        ),
                                    ],
                                ),
                            ),
                        )
                    )

            else:
                # ADMIN
                if rail.selected_index == 0:
                    content.controls.append(
                        ft.Column(
                            spacing=10, expand=True,
                            controls=[
                                ft.Text(
                                    f"👋 Selamat Datang, {session_user['username']} ({session_user['hak_akses']})",
                                    size=18, weight=ft.FontWeight.BOLD
                                ),
                                dashboard_view(),
                            ],
                        )
                    )
                elif rail.selected_index == 1:
                    content.controls.append(
                        ft.Column(
                            spacing=10, expand=True,
                            controls=[
                                ft.Text("💻 Manajemen Data Kamar", size=18, weight=ft.FontWeight.BOLD),
                                kelola_kamar_view(page),
                            ],
                        )
                    )
                elif rail.selected_index == 2:
                    content.controls.append(
                        ft.Column(
                            spacing=10, expand=True,
                            controls=[
                                ft.Text("💻 Manajemen Data Penghuni", size=18, weight=ft.FontWeight.BOLD),
                                kelola_penghuni_view(page),
                            ],
                        )
                    )
                elif rail.selected_index == 3:
                    content.controls.append(
                        ft.Column(
                            spacing=10, expand=True,
                            controls=[
                                ft.Text("💻 Tagihan Bulanan & Prediksi AI", size=18, weight=ft.FontWeight.BOLD),
                                kelola_tagihan_view(page),
                            ],
                        )
                    )
                elif rail.selected_index == 4:
                    content.controls.append(
                        ft.Column(
                            spacing=10, expand=True,
                            controls=[
                                ft.Text("💻 Cetak Laporan Keuangan", size=18, weight=ft.FontWeight.BOLD),
                                kelola_laporan_view(page),
                            ],
                        )
                    )
                elif rail.selected_index == 5:
                    content.controls.append(profil_view(page, session_user["username"], session_user["hak_akses"]))
                elif rail.selected_index == 6:
                    content.controls.append(tentang_view())
                elif rail.selected_index == 7:
                    content.controls.append(
                        ft.Container(
                            alignment=ft.Alignment.CENTER,
                            content=ft.Container(
                                width=420, padding=25, bgcolor=ft.Colors.WHITE, border_radius=16,
                                shadow=ft.BoxShadow(blur_radius=20, color=ft.Colors.BLACK_12),
                                content=ft.Column(
                                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                    spacing=20,
                                    controls=[
                                        ft.Icon(ft.Icons.LOGOUT, size=60, color=ft.Colors.RED_400),
                                        ft.Text("Konfirmasi Logout", size=22, weight=ft.FontWeight.BOLD),
                                        ft.Text("Apakah Anda yakin ingin keluar?", text_align=ft.TextAlign.CENTER),
                                        ft.Row(
                                            alignment=ft.MainAxisAlignment.SPACE_EVENLY,
                                            controls=[
                                                ft.OutlinedButton(
                                                    "Batal",
                                                    on_click=lambda e: (setattr(rail, "selected_index", 0), change(None))
                                                ),
                                                ft.Button(
                                                    "Logout",
                                                    bgcolor=ft.Colors.RED,
                                                    color=ft.Colors.WHITE,
                                                    on_click=lambda e: proses_logout(),
                                                ),
                                            ],
                                        ),
                                    ],
                                ),
                            ),
                        )
                    )

            page.update()

        rail.on_change = change

        page.add(
            ft.Row(
                expand=True, spacing=12,
                controls=[
                    ft.Container(
                        width=260, padding=12, bgcolor=ft.Colors.WHITE, border_radius=12,
                        shadow=ft.BoxShadow(blur_radius=12, color=ft.Colors.BLACK_12),
                        content=ft.Column(
                            spacing=18,
                            controls=[
                                ft.Column(
                                    horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8,
                                    controls=[
                                        ft.Container(
                                            width=80, height=80, border_radius=40, bgcolor=ft.Colors.BLUE_100,
                                            alignment=ft.Alignment.CENTER,
                                            content=ft.Icon(ft.Icons.PERSON, size=46),
                                        ),
                                        ft.Text(session_user["username"], weight=ft.FontWeight.BOLD),
                                        ft.Text(session_user["hak_akses"], size=12, color=ft.Colors.GREY_600),
                                        ft.Divider(),
                                    ],
                                ),
                                ft.Container(height=page.height - 220, content=rail),
                            ],
                        ),
                    ),
                    ft.Container(expand=True, padding=15, content=content),
                ],
            )
        )

        change(None)

    tampil_hallogin()


if __name__ == "__main__":
    ft.run(main)
