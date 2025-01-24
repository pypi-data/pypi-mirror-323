from enum import Enum, EnumMeta
from functools import total_ordering
from typing import Any


class ContainableEnumImpl(EnumMeta):
    """Customized ENUM which can be used with "in"
    """
    def __contains__(cls, item: Any):
        try:
            cls(item)
        except ValueError:
            return False
        return True


class ContainableEnum(Enum, metaclass=ContainableEnumImpl):
    """Base class for creating enums that can be used with "in" and basic comparison
    """
    def __str__(self) -> str:
        return str(self.value)

    def __repr__(self) -> str:
        return self.__str__()


@total_ordering
class ComparableMixin:
    """Base class for creating comparable classes
    """
    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return NotImplemented
        return self._compare_key() == other._compare_key()

    def __lt__(self, other):
        if not isinstance(other, type(self)):
            return NotImplemented
        return self._compare_key() < other._compare_key()

    def _compare_key(self):
        raise NotImplementedError('Subclasses must implement "_compare_key" method')
