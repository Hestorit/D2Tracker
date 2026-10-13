import requests

from models import Hero, Match, Player


class OpenDotaAPI:

    BASE_URL = 'https://api.opendota.com/api'


    def __init__(self, timeout=15):

        self._timeout = timeout
        self._session = requests.Session()


    def _get_json(self, endpoint):

        response = self._session.get(
            f'{self.BASE_URL}{endpoint}',
            timeout=self._timeout,
        )
        response.raise_for_status()
        return response.json()

    def get_player(self, account_id: int) -> Player:

        data = self._get_json(f'/players/{int(account_id)}')
        player = Player(account_id)
        profile = data.get("profile") or {}
        player.username = profile.get('personaname') or 'Unknown player'
        player.avatar = profile.get('avatarfull') or profile.get('avatarmedium') or ''
        player.rank_tier = data.get('rank_tier')
        player.mmr_estimate = data.get('computed_mmr')


        wl = self._get_json(f'/players/{int(account_id)}/wl')
        player.wins = wl.get('win', 0)
        player.losses = wl.get('lose', 0)
        return player

    def get_heroes(self, account_id: int) -> list[Hero]:

        player_rows = self._get_json(f'/players/{int(account_id)}/heroes')
        hero_rows = self._get_json('/heroes')


        hero_lookup = [(int(row['id']), row['localized_name']) for row in hero_rows]

        def hero_name(hero_id):


            for known_id, name in hero_lookup:
                if known_id == int(hero_id):
                    return name
            return f'Hero {hero_id}'

        heroes = []
        for row in player_rows:
            

            games = int(row.get('games', 0))
            wins = int(row.get('win', 0))
            if games:

                heroes.append(
                    Hero(
                        hero_id=row['hero_id'],
                        name=hero_name(row['hero_id']),
                        games=games,
                        wins=wins,
                    )
                )
        return sorted(heroes, key=lambda hero: hero.games, reverse=True)

    def get_recent_matches(self, account_id: int) -> list[Match]:

        rows = self._get_json(f'/players/{int(account_id)}/recentMatches')
        hero_rows = self._get_json('/heroes')
        hero_lookup = [(int(row['id']), row['localized_name']) for row in hero_rows]

        def hero_name(hero_id):

            for known_id, name in hero_lookup:

                if known_id == int(hero_id):
                    return name
            return f'Hero {hero_id}'

        matches = []
        for row in rows:

            player_slot = int(row.get('player_slot', 0))
            radiant = player_slot < 128
            won = bool(row.get('radiant_win', False)) == radiant
            matches.append(
                Match(
                    match_id=row.get('match_id', 0),
                    hero_name=hero_name(row.get('hero_id', 0)),
                    won=won,
                    kills=row.get('kills', 0),
                    deaths=row.get('deaths', 0),
                    assists=row.get('assists', 0),
                    duration=row.get('duration', 0),
                    start_time=row.get('start_time', 0),
                )
            )
        return matches

    def close(self):

        self._session.close()
