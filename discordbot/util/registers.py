from typing import TypeVar, Dict, Type

from discordbot.models import supabase_models
from discordbot.store.supabase_manager import SupabaseManager

# Registers can hold any generic type
T = TypeVar("T", bound=supabase_models.SupabaseModel)


class SupabaseRegister:
    def __init__(self, initial_values: Dict[Type[T], SupabaseManager[T]] = None):
        self.__register: Dict[Type[T], SupabaseManager[T]] = {}
        if initial_values:
            for key, value in initial_values.items():
                self[key] = value

    def keys(self):
        return self.__register.keys()

    def values(self):
        return self.__register.values()

    def __getitem__(self, key: Type[T]) -> SupabaseManager[T]:
        if key not in self.__register:
            raise KeyError(f"Key {key} not found in register")
        return self.__register[key]

    def __setitem__(self, key: Type[T], value: SupabaseManager[T]):
        if key in self.__register:
            raise ValueError(f"Key {key} already exists in register")
        self.__register[key] = value

    def __str__(self):
        return f"SupabaseRegister({self.__register})"
