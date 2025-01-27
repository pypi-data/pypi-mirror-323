from typing import Dict, Any, Optional, TypeVar, Generic

from pydantic import BaseModel

RegistrableType = TypeVar('RegistrableType')


class Registry(BaseModel, Generic[RegistrableType]):
    """Generic registry for managing any type of data."""
    _items: Dict[str, RegistrableType] = {}
    container: Any

    def register(self, key: str, item: RegistrableType) -> None:
        """Register an item in the registry."""
        self._items[key] = item

    def get(self, key: str, **kwargs) -> Optional[RegistrableType]:
        """
        Retrieve an item by its key.
        Additional kwargs can be used by child classes.
        """
        return self._items.get(key)

    def get_all(self) -> Dict[str, RegistrableType]:
        """Get all items in the registry."""
        return self._items

    def has(self, key: str) -> bool:
        """Check if an item exists in the registry."""
        return key in self._items
