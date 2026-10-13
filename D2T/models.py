from abc import ABC, abstractmethod
from datetime import datetime


class GameEntity(ABC):

    @abstractmethod
    def get_info(self) -> str:
        raise NotImplementedError


class Hero(GameEntity):

    def __init__(self, hero_id: int, name: str, games: int = 0, wins: int = 0):

        self._hero_id = int(hero_id)
        self._name = str(name)
        self._games = max(0, int(games))
        self._wins = max(0, min(int(wins), self._games))

    @property
    def hero_id(self) -> int:
        return self._hero_id

    @hero_id.setter
    def hero_id(self, value: int):
        self._hero_id = int(value)

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str):
        self._name = str(value).strip()

    @property
    def games(self) -> int:
        return self._games

    @games.setter
    def games(self, value: int):
        self._games = max(0, int(value))
        self._wins = min(self._wins, self._games)

    @property
    def wins(self) -> int:
        return self._wins

    @wins.setter
    def wins(self, value: int):
        self._wins = max(0, min(int(value), self._games))

    @property
    def losses(self) -> int:
        return self._games - self._wins

    @property
    def winrate(self) -> float:
        return self._wins / self._games * 100 if self._games else 0.0

    def get_info(self) -> str:
        return f'{self.name}: {self.games} matches, {self.winrate:.1f}% win rate'

    def __str__(self) -> str:
        return self.get_info()

    def __repr__(self) -> str:
        return f'Hero(hero_id={self.hero_id!r}, name={self.name!r}, games={self.games}, wins={self.wins})'

    def __eq__(self, other) -> bool:
        if not isinstance(other, Hero):
            return NotImplemented
        return self.hero_id == other.hero_id


class Match(GameEntity):

    def __init__(self, match_id: int, hero_name: str, won: bool,
                 kills: int = 0, deaths: int = 0, assists: int = 0,
                 duration: int = 0, start_time: int = 0):
        self._match_id = int(match_id)
        self._hero_name = str(hero_name)
        self._won = bool(won)
        self._kills = int(kills)
        self._deaths = int(deaths)
        self._assists = int(assists)
        self._duration = int(duration)
        self._start_time = int(start_time)


    @property
    def match_id(self) -> int:
        return self._match_id

    @property
    def hero_name(self) -> str:
        return self._hero_name

    @property
    def won(self) -> bool:
        return self._won

    @property
    def kills(self) -> int:
        return self._kills

    @property
    def deaths(self) -> int:
        return self._deaths

    @property
    def assists(self) -> int:
        return self._assists

    @property
    def duration(self) -> int:
        return self._duration

    @property
    def date_text(self) -> str:
        
        if not self._start_time:
            return 'Неизвестная дата'
        return datetime.fromtimestamp(self._start_time).strftime('%d.%m.%Y %H:%M')

    @property
    def duration_text(self) -> str:
        return f"{self.duration // 60}:{self.duration % 60:02d}"

    def get_info(self) -> str:
        result = 'Победа' if self.won else 'Поражение'
        return f'{result}: {self.hero_name}, {self.kills}/{self.deaths}/{self.assists}'

    def __str__(self) -> str:
        return self.get_info()

    def __repr__(self) -> str:
        return f'Match(match_id={self.match_id}, hero_name={self.hero_name!r})'

    def __eq__(self, other) -> bool:
        if not isinstance(other, Match):
            return NotImplemented
        return self.match_id == other.match_id


class Player(GameEntity):

    def __init__(self, account_id: int):
        self._account_id = int(account_id)
        self._username = ""
        self._rank_tier = None
        self._mmr_estimate = None
        self._avatar = ""
        self._heroes = []
        self._matches = []
        self._wins = 0
        self._losses = 0

    @property
    def account_id(self) -> int:
        return self._account_id

    @account_id.setter
    def account_id(self, value: int):
        self._account_id = int(value)

    @property
    def username(self) -> str:
        return self._username

    @username.setter
    def username(self, value: str):
        self._username = str(value or '').strip()

    @property
    def rank_tier(self):
        return self._rank_tier

    @rank_tier.setter
    def rank_tier(self, value):
        self._rank_tier = value

    @property
    def mmr_estimate(self):
        return self._mmr_estimate

    @mmr_estimate.setter
    def mmr_estimate(self, value):
        self._mmr_estimate = value

    @property
    def avatar(self) -> str:
        return self._avatar

    @avatar.setter
    def avatar(self, value: str):
        self._avatar = str(value or '')

    @property
    def heroes(self) -> list:
        return self._heroes.copy()

    @heroes.setter
    def heroes(self, value: list):
        self._heroes = list(value)

    @property
    def matches(self) -> list:
        return self._matches.copy()

    @matches.setter
    def matches(self, value: list):
        self._matches = list(value)

    @property
    def wins(self) -> int:
        return self._wins

    @wins.setter
    def wins(self, value: int):
        self._wins = max(0, int(value))

    @property
    def losses(self) -> int:
        return self._losses

    @losses.setter
    def losses(self, value: int):
        self._losses = max(0, int(value))

    @property
    def total_matches(self) -> int:
        return self.wins + self.losses

    @property
    def winrate(self) -> float:
        return self.wins / self.total_matches * 100 if self.total_matches else 0.0

    def get_info(self) -> str:
        return f"{self.username or 'Профиль не найден'} (ID: {self.account_id})"

    def __str__(self) -> str:
        return self.get_info()


    def __repr__(self) -> str:
        return f'Player(account_id={self.account_id}, username={self.username!r})'

    
    def __eq__(self, other) -> bool:
        if not isinstance(other, Player):


            return NotImplemented
        return self.account_id == other.account_id
