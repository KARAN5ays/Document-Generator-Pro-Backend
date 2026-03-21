from enum import Enum

class Role(Enum):
    SUPERUSER = 'superuser'
    MANAGER = 'manager'
    FINANCE = 'finance'
    DIRECTOR = 'director'