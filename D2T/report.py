from datetime import datetime
from pathlib import Path


class SessionReport:
    
    TIME_FORMAT = '%d.%m.%Y %H:%M:%S'

    def __init__(self, username: str, report_dir='reports'):
        self._username = username or 'unknown'
        self._login_time = datetime.now()
        self._logout_time = None
        self._report_dir = Path(report_dir)

    @property
    def username(self):
        return self._username

    @property
    def login_time(self):
        return self._login_time

    @property
    def logout_time(self):
        return self._logout_time

    def finish(self):
        
        if self._logout_time is None:
            self._logout_time = datetime.now()

    def save(self):

        self.finish()
        self._report_dir.mkdir(parents=True, exist_ok=True)
        safe_username = ''.join(
            char if char.isalnum() or char in ('-', '_') else '_'
            for char in self._username
        ) or 'unknown'
        filename = self._report_dir / f'session_{safe_username}_{self._login_time:%Y%m%d_%H%M%S}.txt'

        with filename.open('w', encoding='utf-8') as file:
            file.write('+----------------------+---------------------+---------------------+\n')
            file.write('| login                | time_in             | time_out            |\n')
            file.write('+----------------------+---------------------+---------------------+\n')
            file.write(
                f'| {self._username[:20]:20} | '
                f'{self._login_time.strftime(self.TIME_FORMAT):19} | '
                f'{self._logout_time.strftime(self.TIME_FORMAT):19} |\n'
            )
            file.write('+----------------------+---------------------+---------------------+\n')
        return filename

    def __str__(self):

        return f'SessionReport(username={self.username}, login={self.login_time})'

    def __repr__(self):

        return f'SessionReport(username={self.username!r})'

    def __eq__(self, other):

        if not isinstance(other, SessionReport):
            return NotImplemented
        return self.username == other.username and self.login_time == other.login_time
