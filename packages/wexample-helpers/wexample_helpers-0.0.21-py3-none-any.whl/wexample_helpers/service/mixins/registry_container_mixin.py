from typing import Dict, Any, Optional, List, Type

from wexample_helpers.service.registry import Registry


class RegistryContainerMixin:
    """Abstract container for managing multiple registries of any type."""
    _registries: Dict[str, Registry] = {}

    def _get_registry_class_type(self) -> Type[Registry]:
        """Get the type of registry to use. Must be overridden by child classes."""
        return Registry

    def get_registry(self, name: str) -> Registry:
        """Get a registry by its name."""
        registry_name = f"_{name}_registry"
        if registry_name not in self._registries:
            self._registries[registry_name] = (self._get_registry_class_type())(container=self)
        return self._registries[registry_name]

    def register_item(self, registry_name: str, key: str, item: Any) -> None:
        """Register an item in a specific registry."""
        registry = self.get_registry(registry_name)
        registry.register(key, item)

    def register_items(self, registry_name: str, items: List[Any]) -> None:
        """Register multiple items at once in a specific registry."""
        registry = self.get_registry(registry_name)
        if hasattr(registry, 'register_multiple'):
            registry.register_multiple(items)
        else:
            for item in items:
                if hasattr(item, 'get_name'):
                    key = item.get_snake_short_class_name()
                else:
                    key = item.__name__
                registry.register(key, item)

    def get_item(self, registry_name: str, key: str, **kwargs) -> Optional[Any]:
        """Retrieve an item from a specific registry by its key."""
        registry = self.get_registry(registry_name)
        return registry.get(key, **kwargs)
