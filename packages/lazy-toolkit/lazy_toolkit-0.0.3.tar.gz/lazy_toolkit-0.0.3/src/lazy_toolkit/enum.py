from .mixin import ContainableEnum


class Frequency(ContainableEnum):
    """Frequency enum of all purposes:
    - As k-line frequency for data downloading and processing
    - As resampling frequency for data resampling, by calling `Frequency.as_pandas_offset()`
    - As timed job frequency for job scheduling
    """
    # _1s = '1s'
    _1m = '1m'
    _5m = '5m'
    _15m = '15m'
    _1h = '1h'
    # _2h = '2h'
    _4h = '4h'
    _6h = '6h'
    # _8h = '8h'
    _12h = '12h'
    _1d = '1d'
    _1w = '1w'

    def __lt__(self, other: 'Frequency'):
        return self.to_minutes() < other.to_minutes()

    def __gt__(self, other: 'Frequency'):
        return self.to_minutes() > other.to_minutes()

    def to_minutes(self) -> int:
        """Convert the frequency to minute count
        - Manual add new frequency here
        """
        if self == Frequency._1m:
            return 1
        if self == Frequency._5m:
            return 5
        elif self == Frequency._15m:
            return 15
        elif self == Frequency._1h:
            return 60
        elif self == Frequency._4h:
            return 240
        elif self == Frequency._6h:
            return 360
        elif self == Frequency._12h:
            return 720
        elif self == Frequency._1d:
            return 1440
        elif self == Frequency._1w:
            return 10080
        return -1

    def to_seconds(self) -> int:
        """Convert the frequency to second count
        """
        return self.to_minutes() * 60

    def to_hours(self) -> int:
        """Convert the frequency to hour count
        """
        return self.to_minutes() // 60

    def to_days(self) -> int:
        """Convert the frequency to day count
        """
        return self.to_minutes() // 1440

    def is_minute_frequency(self) -> bool:
        return self.to_minutes() < 60

    def is_hour_frequency(self) -> bool:
        return 60 <= self.to_minutes() < 1440

    def is_day_frequency(self) -> bool:
        return self.to_minutes() >= 1440

    def as_pandas_offset(self) -> str:
        """Convert the frequency to pandas resample offset
        - The string values (min, h, D, etc.) are offset alias of pandas
        - https://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html#offset-aliases
        """
        if self.is_minute_frequency():
            return f'{self.to_minutes()}min'
        elif self.is_hour_frequency():
            return f'{self.to_hours()}h'
        elif self.is_day_frequency():
            return f'{self.to_days()}D'
        elif self == Frequency._1w:
            return f'1W'
        return ''


class Colors:
    Grey: str = 'rgba(214, 237, 255, 0.6)'
    Cyan: str = 'rgba(0, 255, 255, 0.6)'
    Red: str = 'rgba(255, 0, 0, 0.6)'
    Green: str = 'rgba(0, 255, 0, 0.6)'
    Yellow: str = 'rgba(255, 255, 0, 0.6)'
    Purple: str = 'rgba(255, 0, 255, 0.6)'
    Orange: str = 'rgba(255, 165, 0, 0.6)'
    Blue: str = 'rgba(0, 0, 255, 0.6)'
    Black: str = 'rgba(0, 0, 0, 0.6)'
    White: str = 'rgba(255, 255, 255, 0.6)'

    b_Grey: str = 'rgba(214, 237, 255, 1)'
    b_Cyan: str = 'rgba(0, 255, 255, 1)'
    b_Red: str = 'rgba(255, 50, 50, 1)'
    b_Green: str = 'rgba(50, 255, 50, 1)'
    b_Yellow: str = 'rgba(255, 255, 50, 1)'
    b_Purple: str = 'rgba(255, 50, 255, 1)'
    b_Orange: str = 'rgba(255, 165, 50, 1)'
    b_Blue: str = 'rgba(50, 50, 255, 1)'
    b_Black: str = 'rgba(50, 50, 50, 1)'
    b_White: str = 'rgba(255, 255, 255, 1)'

    d_Grey: str = 'rgba(214, 237, 255, 0.3)'
    d_Cyan: str = 'rgba(0, 255, 255, 0.3)'
    d_Red: str = 'rgba(255, 50, 50, 0.3)'
    d_Green: str = 'rgba(50, 255, 50, 0.3)'
    d_Yellow: str = 'rgba(255, 255, 50, 0.3)'
    d_Purple: str = 'rgba(255, 50, 255, 0.3)'
    d_Orange: str = 'rgba(255, 165, 50, 0.3)'
    d_Blue: str = 'rgba(50, 50, 255, 0.3)'
    d_Black: str = 'rgba(50, 50, 50, 0.3)'
    d_White: str = 'rgba(255, 255, 255, 0.3)'

    t_Grey: str = 'rgba(214, 237, 255, 0.1)'
    t_Cyan: str = 'rgba(0, 255, 255, 0.1)'
    t_Red: str = 'rgba(255, 50, 50, 0.1)'
    t_Green: str = 'rgba(50, 255, 50, 0.1)'
    t_Yellow: str = 'rgba(255, 255, 50, 0.1)'
    t_Purple: str = 'rgba(255, 50, 255, 0.1)'
    t_Orange: str = 'rgba(255, 165, 50, 0.1)'
    t_Blue: str = 'rgba(50, 50, 255, 0.1)'
    t_Black: str = 'rgba(50, 50, 50, 0.1)'
    t_White: str = 'rgba(255, 255, 255, 0.1)'
