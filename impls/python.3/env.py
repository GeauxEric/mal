from reader import LispType, LispSymbol
from typing import Optional


class EnvNotFoundError(ValueError):
    def __init__(self, *args: object, missing_env_key="") -> None:
        super().__init__(*args)
        self._env_key = missing_env_key

    def get_missing_env_key(self):
        return self._env_key


class Env:
    def __init__(self, outer: Optional['Env'] = None) -> None:
        self._outer = outer
        self._data = {}

    def set(self, key: LispSymbol, value: LispType):
        self._data[key] = value
        return value

    def find(self, key: LispSymbol) -> Optional['Env']:
        if key in self._data:
            return self
        if self._outer is not None:
            return self._outer.find(key)
        return None

    def get(self, key: LispSymbol) -> Optional[LispType]:
        env = self.find(key)
        if env is None:
            raise EnvNotFoundError(missing_env_key=key.value)
        return env._data[key]
