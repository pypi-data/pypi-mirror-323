import pendulum
from .breed import Breed as Breed
from .country import Country as Country
from .horse_age import HorseAge as HorseAge
from _typeshed import Incomplete

class Horse:
    REGEX: Incomplete
    name: Incomplete
    breed: Incomplete
    country: Incomplete
    age: Incomplete
    def __init__(self, name: str, country: Country | str | None = None, age_or_yob: int | None = None, *, context_date: pendulum.DateTime | None = None) -> None: ...
