from enum import Enum


def enum_list(enum: type[Enum]) -> list[str]:
    return [member.name.replace("_", " ").title() for member in enum]
