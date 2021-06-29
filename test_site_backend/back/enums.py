import enum


@enum.unique
class ActionEnum(int, enum.Enum):
    VIEW = 0x01
    EDIT = 0x02
    CREATE = 0x04
