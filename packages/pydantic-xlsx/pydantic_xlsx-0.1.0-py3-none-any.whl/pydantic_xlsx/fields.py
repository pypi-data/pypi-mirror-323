"""
Extends pydantic's fields with some extra functionality.
"""

from abc import ABCMeta, abstractmethod
from typing import Any, Generic, Optional, Type, TypeVar, Unpack, Self

from openpyxl.styles import Font
from pydantic.fields import FieldInfo, PydanticUndefined, _FromFieldInfoInputs

from .types import Money


class XlsxFieldInfo(FieldInfo):
    """
    Extends pydantic's Field class for some extra functionality (e.g. cell
    formatting).
    """

    __slots__ = (
        "font",
        "number_format",
    )

    def __init__(self, font: Optional[Font] = None,
                 number_format: Optional[str] = None,
                 **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.font = font
        self.number_format = number_format





def XlsxField(
    default: Any = PydanticUndefined,
    *,
    font: Optional[Font] = None,
    number_format: Optional[str] = None,
    **kwargs,
) -> Any:
    """
    A field for extra formatting etc. The styles defined by a field will be
    applied to the whole column.
    """
    field_info = XlsxFieldInfo(
        font=font,
        number_format=number_format,
        default=default,
        **kwargs,
    )
    return field_info


T = TypeVar('T')


class FieldTypeInfo(Generic[T], metaclass=ABCMeta):
    """
    Some `XlsxField` settings can be derived from certain field types like
    `types.Money`.
    """

    field_type = T

    def __init__(self, field_type: Type[T]) -> None:
        self.field_type = field_type

    @abstractmethod
    def field_info(self) -> XlsxFieldInfo:
        """Returns `XlsxFieldInfo` based on the Field type."""
        pass


class MoneyFieldInfo(FieldTypeInfo[Money]):
    def field_info(self) -> XlsxFieldInfo:
        return XlsxFieldInfo(number_format=self.field_type.number_format())


class FieldTypeInfoFactory:
    """
    Creates the correct `FieldTypeInfo` for a given type.
    """

    @classmethod
    def from_field_type(cls, field_type: Type[T]) -> Optional[FieldTypeInfo]:
        """
        Creates and returns the correct `FieldTypeInfo` for a given type.
        """
        if issubclass(field_type, Money):
            return MoneyFieldInfo(field_type)
        return None

    @classmethod
    def field_info_from_type(
            cls,
            field_type: Type[T]
    ) -> Optional[XlsxFieldInfo]:
        """
        Same as `from_field_type` but directly calls `FieldTypeInfo.field_info`
        (if available) and returns the result.
        """
        if (impl := cls.from_field_type(field_type)) is not None:
            return impl.field_info()
        return None

