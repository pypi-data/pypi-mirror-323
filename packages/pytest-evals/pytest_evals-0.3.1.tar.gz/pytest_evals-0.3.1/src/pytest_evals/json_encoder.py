import dataclasses
import json
from enum import Enum
from typing import Callable

try:
    from pydantic import BaseModel

    HAVE_PYDANTIC = True
except ImportError:
    HAVE_PYDANTIC = False
    BaseModel = type(None)  # Create a dummy type that won't match anything

try:
    import pandas as pd

    def is_series(obj):  # pyright: ignore [reportRedeclaration]
        return isinstance(obj, pd.Series)

    def is_dataframe(obj):  # pyright: ignore [reportRedeclaration]
        return isinstance(obj, pd.DataFrame)

    HAVE_PANDAS = True
except ImportError:
    HAVE_PANDAS = False

    def is_series(obj):
        return False

    def is_dataframe(obj):
        return False


class AdvancedJsonEncoder(json.JSONEncoder):
    """JSON encoder that handles Pydantic models (if installed) and other special types."""

    # noinspection PyBroadException
    def default(self, o):
        if HAVE_PYDANTIC and isinstance(o, BaseModel):
            return json.loads(o.model_dump_json())  # type: ignore
        if dataclasses.is_dataclass(o):
            return dataclasses.asdict(o)  # type: ignore
        if isinstance(o, Enum):
            return o.value
        if isinstance(o, Callable):
            try:
                return f"<{o.__module__}.{o.__name__}>"
            except Exception:
                try:
                    return f"<{o.__module__}.{o.__class__.__name__}>"
                except Exception:
                    return repr(o)
        if isinstance(o, type(None)):
            return None
        if HAVE_PANDAS and is_series(o):
            return o.to_dict()
        if HAVE_PANDAS and is_dataframe(o):
            return o.to_dict(orient="records")
        if hasattr(o, "__repr__"):
            return repr(o)
        return super().default(o)
