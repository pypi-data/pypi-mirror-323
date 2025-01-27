from wexample_helpers.classes.mixin.has_short_class_name_class_mixin import (
    HasShortClassNameClassMixin,
)


class HasSnakeShortClassNameClassMixin(HasShortClassNameClassMixin):
    @classmethod
    def get_snake_short_class_name(cls) -> str:
        from wexample_helpers.helpers.string import string_to_snake_case

        return string_to_snake_case(cls.get_short_class_name())

    @classmethod
    def get_name(cls) -> str:
        return cls.get_snake_short_class_name()
