from functools import partial
import inspect
import pandas as pd
from typing import Any, Callable, Dict, Iterable, List, Optional, Tuple, Type, Union


class DynamicSeriesAccessor:
    """
    Pandas Series Accessor for dynamically accessing methods and properties
    of a target class.

    The accessor allows you to call the methods and properties of the specified
    target class on a pandas Series. Each method or property applied via the accessor
    returns a new Series, where each element is the result of applying the method
    or property to the target class instance, initialised with the value from the
    original Series.

    You can also define custom methods that can be accessed directly on the Series,
    in addition to the methods and properties of the target class.

    Parameters:
    - series (pd.Series): The pandas Series to extend.
    - target_class (Type): The class whose methods and properties will be mapped.
    - excluded_attrs (Iterable[str]): A tuple of blocked attributes.
    - valid_types (Optional[Iterable[Type]]): Allowed value types in the Series.
      If not provided, it defaults to the types of the initialisation parameters
      of the target class (from `__init__` method).
    - custom_methods (Optional[Dict[str, Callable]]): Custom methods that can be
      accessed on the Series.
    """

    def __init__(
        self,
        series: pd.Series,
        target_class: Type,
        excluded_attrs: Iterable[str],
        valid_types: Optional[Iterable[Type]] = None,
        custom_methods: Optional[Dict[str, Callable]] = None,
    ):
        self._s = series
        self._cls = target_class
        self._cls_init_params = self._get_cls_init_params()
        self._excl = excluded_attrs
        self._valid = (
            valid_types if valid_types else tuple(self._cls_init_params.values())
        )
        self._custom_methods = custom_methods if custom_methods else {}
        self._validate()

    def _validate(self):
        """Ensure the Series is compatible with the target class.

        Raises an AttributeError if the Series is empty, contains invalid types,
        or if the target class requires more than one parameter to initialise.
        """
        if len(self._cls_init_params) > 1:
            raise AttributeError(
                f"{self._cls.__name__!r} requires more than one initialisation parameter."
            )

        if self._s.empty:
            raise AttributeError(f"{self} only works with non-empty series.")

        if not self._s.map(type).isin(self._valid).all():
            raise AttributeError(
                f"{self} only works with series of type(s) "
                f"{", ".join(t.__name__ for t in self._valid)}."
            )

    def _get_cls_init_params(self) -> Dict[str, Type]:
        """Get the init parameters of the target class, including their types."""
        init_signature = inspect.signature(self._cls.__init__)
        return {
            param.name: param.annotation
            for param in init_signature.parameters.values()
            if param.name != "self"
        }

    def _wrap_cls_attribute(
        self, name: str
    ) -> Union[pd.Series, Callable[..., pd.Series]]:
        """Wrap the target class method or property for dynamic invocation."""
        attr = getattr(self._cls, name)

        # Handle properties
        if not callable(attr):
            return self._s.apply(lambda x: attr.__get__(self._cls(x)))

        # Handle methods
        def method_wrapper(*args, **kwargs) -> pd.Series:
            return self._s.apply(lambda x: attr(self._cls(x), *args, **kwargs))

        return method_wrapper

    def _wrap_custom_method(self, name: str) -> Callable[..., pd.Series]:
        """Wrap custom methods for dynamic invocation on the Series."""
        custom_method = self._custom_methods[name]

        def custom_method_wrapper(*args, **kwargs) -> pd.Series:
            return self._s.apply(lambda x: custom_method(x, *args, **kwargs))

        return custom_method_wrapper

    def __dir__(self) -> List[str]:
        """Maps available target class attributes and custom methods to the accessor."""
        class_attrs = dir(self._cls)
        attrs = [attr for attr in class_attrs if attr not in self._excl]
        return attrs + list(self._custom_methods.keys())

    def __getattr__(self, name: str) -> Union[Callable[..., pd.Series], pd.Series]:
        """Maps methods and properties of the target class to the accessor."""
        if name not in dir(self):
            raise AttributeError(f"{self} does not provide attribute {name!r}.")

        if name in self._custom_methods:
            return self._wrap_custom_method(name)

        return self._wrap_cls_attribute(name)

    def __str__(self) -> str:
        """Return a string representation of the dynamic series accessor."""
        return f"Dynamic {self._cls.__name__!r} series accessor"


def create_dynamic_series_accessor(
    name: str,
    target_class: Type,
    excluded_attrs: Iterable[str] = (),
    valid_types: Optional[Iterable[Type]] = None,
    custom_methods: Optional[Dict[str, Callable]] = None,
) -> None:
    """
    Configures and registers a Pandas Series accessor for dynamic access to methods
    and properties of a target class.

    This function preconfigures the accessor with the specified target class,
    excluded attributes, and valid types, then registers it under the given
    name as an extension to the Pandas Series.

    See `DynamicSeriesAccessor` for full documentation.
    """
    accessor = partial(
        DynamicSeriesAccessor,
        target_class=target_class,
        excluded_attrs=excluded_attrs,
        valid_types=valid_types,
        custom_methods=custom_methods,
    )
    pd.api.extensions.register_series_accessor(name)(accessor)
