from time import time
from typing import Any, Hashable, Optional, Union


class TTLDict:
    def __init__(self):
        self._base = dict()

    def set(self, key: Hashable, value: Any, *, ttl: Optional[int] = None) -> bool:
        try:
            self._base[key] = (self._get_ttl_timestamp(ttl), value)
            print(self._base)
        except Exception:  # pragma: no cover
            return False  # pragma: no cover
        return True

    def add(self, key: Hashable, value: Any, *, ttl: Optional[int] = None) -> bool:
        if key in self._base:
            return False
        return self.set(key, value, ttl=ttl)

    def get(self, key: Hashable, default: Optional[Any] = None) -> Any:
        ttl, value = self._base.get(key, (None, default))
        print(self._base)
        if ttl is not None and self._is_ttl_expired(ttl):
            self.delete(key)
            return default
        return value

    def delete(self, key: Hashable) -> bool:
        if key not in self._base:
            return False
        del self._base[key]
        return True

    def exists(self, *keys: Hashable) -> bool:
        hits = []
        for key in keys:
            if key not in self._base:
                hits.append(False)
                continue
            ttl, _ = self._base.get(key, (None, None))
            if ttl is not None and self._is_ttl_expired(ttl):
                hits.append(False)
            else:
                hits.append(True)

        return any(hits)

    def expire(self, key: Hashable, ttl: int) -> bool:
        value = self._base.get(key)
        if value:
            _, value = value
            self._base[key] = (self._get_ttl_timestamp(ttl), value)
            return True
        return False

    def flush(self) -> None:
        self._base.clear()

    def _get_ttl_timestamp(self, ttl: Union[int, None]) -> Union[int, None]:
        if ttl is None:
            return None
        return int(time()) + ttl

    def _is_ttl_expired(self, timestamp: int) -> bool:
        return int(time()) >= timestamp
