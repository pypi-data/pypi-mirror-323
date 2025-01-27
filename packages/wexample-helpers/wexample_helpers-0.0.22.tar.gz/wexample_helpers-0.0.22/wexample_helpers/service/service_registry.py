from typing import Dict, Type, Optional, List, Any

from wexample_app.utils.service.service_mixin import ServiceMixin
from wexample_helpers.service.registry import Registry


class ServiceRegistry(Registry[Type[ServiceMixin]]):
    """Registry for managing services of type ServiceMixin."""
    _service_instances: Dict[str, ServiceMixin] = {}
    container: Any  # Will be ServiceMixinContainer at runtime

    def register(self, key: str, service_class: Type[ServiceMixin]) -> None:
        """Register a service class in the registry."""
        self._items[key] = service_class

    def register_multiple(self, service_classes: List[Type[ServiceMixin]]) -> None:
        """Register multiple service classes at once."""
        for service_class in service_classes:
            if hasattr(service_class, 'get_name'):
                key = service_class.get_snake_short_class_name()
            else:
                key = service_class.__name__
            self.register(key, service_class)

    def get(self, key: str | Type[ServiceMixin], **kwargs) -> Optional[ServiceMixin]:
        """
        Retrieve a service by its key. Instantiates the service if it doesn't exist.
        Additional kwargs are passed to the service constructor.
        """
        # If key is a class, use its name
        if isinstance(key, type):
            key = key.get_snake_short_class_name()

        # Return existing instance if already instantiated
        if key in self._service_instances:
            return self._service_instances[key]

        # Get service class and create new instance if exists
        service_class = self._items.get(key)
        if service_class:
            # Rebuild model if it's a Pydantic model using HasClassDependencies mixin.
            if hasattr(service_class, 'import_dependencies_and_rebuild'):
                service_class.import_dependencies_and_rebuild()
            # Rebuild model if it's a Pydantic model
            elif hasattr(service_class, 'model_rebuild'):
                service_class.model_rebuild()

            # Create instance with kernel
            instance = service_class(**kwargs)
            self._service_instances[key] = instance
            return instance

        return None

    def instantiate_all(self, **kwargs) -> Dict[str, ServiceMixin]:
        """
        Instantiate all registered services with the given kwargs.
        Returns a dictionary of service instances keyed by their names.
        """
        for key, service_class in self._items.items():
            if key not in self._service_instances:
                self.get(key, **kwargs)
        return self._service_instances

    def get_class(self, key: str) -> Optional[Type[ServiceMixin]]:
        """Get the service class without instantiating it."""
        return self._items.get(key)

    def all_classes(self) -> List[Type[ServiceMixin]]:
        """Return all registered service classes."""
        return self._items.values()

    def all_instances(self) -> Dict[str, ServiceMixin]:
        """Return all instantiated services."""
        return self._service_instances.copy()

    def get_all(self) -> Dict[str, ServiceMixin]:
        """Get all instantiated services."""
        return self._service_instances

    def all_classes_models_rebuild(self):
        from src.helpers.polyfill import polyfill_import_kernel_and_rebuild
        polyfill_import_kernel_and_rebuild(list(self.all_classes()))