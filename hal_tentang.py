import flet as ft

def tentang_view():
    return ft.Container(
        alignment=ft.Alignment.TOP_LEFT,
        content=ft.Container(
            width=600, padding=30, bgcolor="white", border_radius=20,
            shadow=ft.BoxShadow(blur_radius=20, color="black12"),
            content=ft.Column(spacing=20, horizontal_alignment=ft.CrossAxisAlignment.CENTER, controls=[
                ft.Icon(ft.Icons.HOME_REPAIR_SERVICE, size=80, color=ft.Colors.BLUE),
                ft.Text("Tentang Aplikasi", size=18, weight=ft.FontWeight.BOLD),
                ft.Divider(),
                ft.Text(
                    "Smart Boarding House adalah sistem manajemen kos-kosan digital "
                    "yang dikembangkan untuk memudahkan pengelolaan kamar, penghuni, "
                    "dan tagihan secara otomatis.",
                    text_align=ft.TextAlign.CENTER, size=14,
                ),
                ft.Text(
                    "Dilengkapi dengan fitur AI Linear Regression untuk memprediksi "
                    "estimasi biaya operasional di masa mendatang.",
                    text_align=ft.TextAlign.CENTER, size=14, color=ft.Colors.BLACK_54,
                ),
                ft.Divider(),
                ft.Row(alignment=ft.MainAxisAlignment.CENTER, spacing=30, controls=[
                    _info_item(ft.Icons.CODE, "Framework", "Flet"),
                    _info_item(ft.Icons.STORAGE, "Database", "MySQL"),
                    _info_item(ft.Icons.AUTO_GRAPH, "AI Model", "Regression"),
                ]),
                ft.Divider(),
                ft.Text("© 2026 • Proyek UAS • Sistem Manajemen Kos", size=12, color=ft.Colors.BLACK_38),
            ]),
        ),
    )

def _info_item(icon, title, value):
    return ft.Column(
        spacing=5, horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            ft.Icon(icon, size=32, color=ft.Colors.BLUE),
            ft.Text(title, size=12, color=ft.Colors.BLACK_54),
            ft.Text(value, size=14, weight=ft.FontWeight.BOLD),
        ],
    )