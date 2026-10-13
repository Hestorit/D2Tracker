import flet as ft
import requests

from obj_collections import ObjectCollection
from models import Player, Hero, Match
from opendota_api import OpenDotaAPI
from report import SessionReport


class Dota2Tracker:

    def __init__(self, page: ft.Page):

        self.page = page
        self.api = OpenDotaAPI()
        self.current_player = None
        self.session_report = None
        self.hero_collection = ObjectCollection()
        self.match_collection = ObjectCollection()
        self.player_history = ObjectCollection()

        for index in range(10):

            self.player_history.add(Player(index + 1))

        self.page.title = 'Dota 2 Tracker'
        self.page.padding = 20
        self.page.theme_mode = ft.ThemeMode.DARK
        self.page.window.width = 1100
        self.page.window.height = 760
        self.page.on_close = self.on_close
        self.show_login()

    def show_login(self, error_message=''):

        self.page.clean()
        self.page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.page.vertical_alignment = ft.MainAxisAlignment.CENTER

        self.id_field = ft.TextField(

            label='Steam Account ID',
            hint_text='Например, 1783412791',
            value='',
            width=360,
            autofocus=True,
        )

        self.login_error = ft.Text(error_message, color=ft.Colors.RED)

        def login_click(e):

            raw_id = (self.id_field.value or '').strip()

            if not raw_id.isdigit() or int(raw_id) <= 0:

                self.login_error.value = 'Введите положительный числовой Steam ID'
                return

            button.disabled = True
            self.login_error.value = 'Загружаем данные OpenDota...'

            try:
                player = self.api.get_player(int(raw_id))
                self.current_player = player
                self.player_history.add(player)
                self.session_report = SessionReport(player.username or str(player.account_id))
                self.show_profile()
            except requests.RequestException as error:

                button.disabled = False

                self.login_error.value = f'Ошибка OpenDota API: {error}'
            except (ValueError, TypeError) as error:

                button.disabled = False
                self.login_error.value = f'Не удалось обработать данные: {error}'

        button = ft.Button('Найти игрока', width=360, on_click=login_click)
        self.page.add(

            ft.Container(
                content=ft.Column(
                    controls=[

                        ft.Icon(ft.Icons.SPORTS_ESPORTS, size=54),
                        ft.Text('Dota 2 Tracker', size=32, weight=ft.FontWeight.BOLD),
                        ft.Text('Профиль и статистика игрока OpenDota'),
                        self.id_field,
                        button,
                        self.login_error,
                    ],

                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=16,
                    tight=True,
                ),
                alignment=ft.Alignment.CENTER,
                expand=True,
            )
        )

    def show_profile(self):

        player = self.current_player
        self.page.clean()
        self.page.horizontal_alignment = ft.CrossAxisAlignment.STRETCH
        self.page.vertical_alignment = ft.MainAxisAlignment.START

        name = ft.Text(player.username or 'Неизвестный игрок', size=28, weight=ft.FontWeight.BOLD)
        avatar = ft.Image(src=player.avatar, width=96, height=96, fit=ft.BoxFit.COVER) if player.avatar else ft.Icon(ft.Icons.ACCOUNT_CIRCLE, size=96)

        rank = self.format_rank(player.rank_tier)
        mmr = str(player.mmr_estimate) if player.mmr_estimate else 'Нет данных'

        profile_card = ft.Container(

            content=ft.Row(
                controls=[
                    avatar,
                    ft.Column(
                        controls=[
                            name,
                            ft.Text(f'Steam ID: {player.account_id}'),
                            ft.Text(f'Ранг: {rank}'),
                            ft.Text(f'Примерный MMR: {mmr}'),

                        ],
                        spacing=6,
                        expand=True,
                    ),
                ],
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=20,
            ),
            padding=20,
            border=ft.Border.all(1, ft.Colors.BLUE_GREY_700),
            border_radius=12,
        )


        stats_row = ft.Row(
            controls=[
                self.metric_card('Победы', str(player.wins), ft.Icons.CHECK_CIRCLE),
                self.metric_card('Поражения', str(player.losses), ft.Icons.CANCEL),
                self.metric_card('Винрейт', f"{player.winrate:.1f}%", ft.Icons.PERCENT),
                self.metric_card('Матчи', str(player.total_matches), ft.Icons.SPORTS_ESPORTS),
            ],
            spacing=12,
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )


        hero_button = ft.Button('Статистика по героям', icon=ft.Icons.MILITARY_TECH, on_click=lambda e: self.show_heroes())
        match_button = ft.Button('Последние матчи', icon=ft.Icons.HISTORY, on_click=lambda e: self.show_matches())
        refresh_button = ft.Button('Обновить профиль', icon=ft.Icons.REFRESH, on_click=lambda e: self.refresh_profile())
        logout_button = ft.OutlinedButton('Сменить игрока', icon=ft.Icons.LOGOUT, on_click=lambda e: self.show_login())


        self.page.add(
            ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Text('Dota 2 Stats', size=24, weight=ft.FontWeight.BOLD),
                            ft.Container(expand=True),
                            logout_button,
                        ],


                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    profile_card,
                    stats_row,

                    ft.Text('Разделы статистики', size=20, weight=ft.FontWeight.BOLD),
                    ft.Row(controls=[hero_button, match_button, refresh_button], wrap=True, spacing=10),
                    ft.Text('Источник данных: OpenDota API', color=ft.Colors.GREY),
                ],
                spacing=18,
                scroll=ft.ScrollMode.AUTO,
                expand=True,
            )
        )


    def metric_card(self, title, value, icon):
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Icon(icon, size=26),
                    ft.Text(title, size=13, color=ft.Colors.GREY),
                    ft.Text(value, size=22, weight=ft.FontWeight.BOLD),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=5,
            ),

            padding=14,
            border=ft.Border.all(1, ft.Colors.BLUE_GREY),
            border_radius=12,
            expand=True,
            alignment=ft.Alignment.CENTER,
        )

    @staticmethod
    def format_rank(rank_tier):

        if not rank_tier:
            return 'Калибровка'
        tier = int(rank_tier) // 10
        stars = int(rank_tier) % 10
        ranks = [
            'Нет ранга', 'Рекрут', 'Страж', 'Рыцарь', 'Герой',
            'Легенда', 'Властелин', 'Рапира', 'Титян'

        ]

        if 1 <= tier <= 8:
            return f'{ranks[tier]} ({stars} зв.)'
        if tier == 0:
            return 'Нет ранга'
        return 'Титян'
    

    def show_heroes(self):

        self.page.clean()
        title = ft.Text('Статистика по героям', size=26, weight=ft.FontWeight.BOLD)
        status = ft.Text('Загружаем статистику...')
        search_field = ft.TextField(label='Поиск героя', width=300)
        sort_choice = ft.Dropdown(

            label='Сортировка',
            width=230,
            value='games',
            options=[
                ft.dropdown.Option('games', 'По числу матчей'),
                ft.dropdown.Option('winrate', 'По винрейту'),
                ft.dropdown.Option('wins', 'По победам'),
                ft.dropdown.Option('name', 'По имени'),
            ],
        )

        table_holder = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True)

        def render_table(e=None):
            query = (search_field.value or '').strip().casefold()
            sort_key = sort_choice.value or 'games'
            heroes = [hero for hero in self.hero_collection if query in hero.name.casefold()]
            heroes.sort(key=lambda hero: getattr(hero, sort_key), reverse=sort_key != 'name')
            rows = [

                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(hero.name)),
                        ft.DataCell(ft.Text(str(hero.games))),
                        ft.DataCell(ft.Text(str(hero.wins))),
                        ft.DataCell(ft.Text(str(hero.losses))),
                        ft.DataCell(ft.Text(f'{hero.winrate:.1f}%')),

                    ]
                )
                for hero in heroes

            ]
            table_holder.controls = [
                ft.DataTable(
                    columns=[
                        ft.DataColumn(ft.Text('Герой')),
                        ft.DataColumn(ft.Text('Матчи')),
                        ft.DataColumn(ft.Text('Победы')),
                        ft.DataColumn(ft.Text('Поражения')),
                        ft.DataColumn(ft.Text('Винрейт')),
                    ],
                    rows=rows,
                    column_spacing=24,

                )
            ]
            status.value = f'Найдено героев: {len(heroes)}'

        search_field.on_change = render_table
        sort_choice.on_select = render_table

        self.page.add(

            ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Button('← Профиль', on_click=lambda e: self.show_profile()),
                            title,
                        ],
                        spacing=18,
                    ),
                    ft.Row(controls=[search_field, sort_choice], wrap=True, spacing=12),
                    status,
                    table_holder,
                ],

                expand=True,
                spacing=14,
            )
        )

        try:
            self.hero_collection = ObjectCollection(
                self.api.get_heroes(self.current_player.account_id)
            )

            render_table()
        except requests.RequestException as error:
            status.value = f'Ошибка загрузки героев: {error}'

        self.page.update()

    def show_matches(self):

        self.page.clean()
        title = ft.Text('Последние матчи', size=26, weight=ft.FontWeight.BOLD)
        status = ft.Text('Загружаем матчи...')
        match_column = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True)

        self.page.add(
            ft.Column(

                controls=[
                    ft.Row(
                        controls=[
                            ft.Button('← Профиль', on_click=lambda e: self.show_profile()),
                            title,
                        ],
                        spacing=18,
                    ),
                    status,
                    match_column,
                ],
                expand=True,
                spacing=14,
            )
        )

        try:
            self.match_collection = ObjectCollection(
                self.api.get_recent_matches(self.current_player.account_id)
            )

            cards = []
            for match in self.match_collection:
                result = 'ПОБЕДА' if match.won else 'ПОРАЖЕНИЕ'

                color = ft.Colors.GREEN if match.won else ft.Colors.RED
                cards.append(
                    ft.Container(
                        content=ft.Row(

                            controls=[
                                ft.Column(
                                    controls=[
                                        ft.Text(match.hero_name, weight=ft.FontWeight.BOLD, size=17),
                                        ft.Text(match.date_text, color=ft.Colors.GREY),
                                        ft.Text(f'K/D/A: {match.kills}/{match.deaths}/{match.assists}'),
                                    ],
                                    expand=True,
                                    spacing=5,
                                ),

                                ft.Column(
                                    controls=[
                                        ft.Text(result, color=color, weight=ft.FontWeight.BOLD),
                                        ft.Text(f'Длительность: {match.duration_text}'),
                                        ft.Text(f'Match ID: {match.match_id}', size=12),

                                    ],
                                    horizontal_alignment=ft.CrossAxisAlignment.END,
                                    spacing=5,
                                ),
                            ],
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        padding=14,
                        border=ft.Border.all(1, ft.Colors.BLUE_GREY),
                        border_radius=10,
                    )
                )
            match_column.controls = cards or [ft.Text('Матчи не найдены.')]


            status.value = f'Последних матчей: {len(cards)}'
        except requests.RequestException as error:

            status.value = f'Ошибка загрузки матчей: {error}'

        self.page.update()

    def refresh_profile(self):

        try:
            self.current_player = self.api.get_player(self.current_player.account_id)
            self.show_profile()

        except requests.RequestException as error:
            self.show_login(f'Не удалось обновить профиль: {error}')


    def on_close(self, e):

        if self.session_report is not None:
            try:
                path = self.session_report.save()
                print(f'Отчёт сохранён: {path}')
            except OSError as error:
                print(f'Не удалось сохранить отчёт: {error}')
        self.api.close()



def main(page: ft.Page):
    
    Dota2Tracker(page)


ft.run(main)
