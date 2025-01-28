import json
import sys
from dataclasses import dataclass
from enum import Enum
from unittest.mock import patch

import pandas as pd
from pydantic import BaseModel

from pytest_evals.json_encoder import AdvancedJsonEncoder


# Test structures
@dataclass
class Person:
    name: str
    age: int


class Color(Enum):
    RED = "red"
    BLUE = "blue"


class User(BaseModel):
    name: str
    age: int


def test_advanced_json_encoder():
    """Test all AdvancedJsonEncoder functionality"""
    # Setup test data
    person = Person(name="John", age=30)
    data = {
        "person": person,
        "color": Color.RED,
        "basic": {"num": 42, "list": [1, 2]},
    }

    # Test encoding and decoding
    encoded = json.dumps(data, cls=AdvancedJsonEncoder)
    decoded = json.loads(encoded)

    # Verify results
    assert decoded["person"] == {"name": "John", "age": 30}
    assert decoded["color"] == "red"
    assert decoded["basic"] == {"num": 42, "list": [1, 2]}


def test_pydantic_encoding():
    """Test Pydantic model encoding"""
    user = User(name="John", age=30)
    encoded = json.dumps(user, cls=AdvancedJsonEncoder)
    assert json.loads(encoded) == {"name": "John", "age": 30}


def test_function_encoding():
    """Test error on unsupported type"""
    assert (
        json.dumps(lambda x: x, cls=AdvancedJsonEncoder)
        == '"<tests.test_json_encoder.<lambda>>"'
    )


def test_dataframe_encoding():
    """Test DataFrame encoding"""
    assert (
        json.dumps(pd.DataFrame([{"field": "value"}]), cls=AdvancedJsonEncoder)
        == '[{"field": "value"}]'
    )


def test_series_encoding():
    """Test Series encoding"""
    assert (
        json.dumps(pd.Series([1, 2, 3]), cls=AdvancedJsonEncoder)
        == '{"0": 1, "1": 2, "2": 3}'
    )


def test_none_encoding():
    """Test None type encoding"""
    data = {"null_value": None}
    encoded = json.dumps(data, cls=AdvancedJsonEncoder)
    assert json.loads(encoded) == {"null_value": None}


def test_unsupported_type_fallback():
    """Test fallback to default encoder for unsupported types"""

    class UnsupportedType:
        pass

    assert ".UnsupportedType object" in json.dumps(
        UnsupportedType(), cls=AdvancedJsonEncoder
    )


# Test for json_encoder.py ImportError case
def test_pydantic_import_error():
    with patch.dict(sys.modules, {"pydantic": None}):
        # Force reload of the module to trigger ImportError
        import importlib
        import pytest_evals.json_encoder

        importlib.reload(pytest_evals.json_encoder)

        assert not pytest_evals.json_encoder.HAVE_PYDANTIC
        assert pytest_evals.json_encoder.BaseModel is type(None)


def test_pandas_import_error():
    """Test the JSON encoder when pandas is not available"""
    with patch.dict(sys.modules, {"pandas": None}):
        # Force reload of the module to trigger ImportError
        import importlib
        import pytest_evals.json_encoder

        importlib.reload(pytest_evals.json_encoder)

        # Verify pandas-related flags and functions
        assert not pytest_evals.json_encoder.HAVE_PANDAS

        # Test is_series function
        class MockObject:
            pass

        mock_obj = MockObject()
        assert not pytest_evals.json_encoder.is_series(mock_obj)

        # Test is_dataframe function
        assert not pytest_evals.json_encoder.is_dataframe(mock_obj)


def test_none_type_variations():
    """Test different scenarios involving None type"""
    # Test None in different contexts
    test_cases = [
        {"direct_none": None},
        {"nested_none": {"key": None}},
        {"none_in_list": [1, None, 3]},
        {"multiple_nones": [None, None]},
        None,
    ]

    for case in test_cases:
        encoded = json.dumps(case, cls=AdvancedJsonEncoder)
        decoded = json.loads(encoded)
        assert decoded == case


def test_mixed_none_with_other_types():
    """Test None combined with other supported types"""

    @dataclass
    class DataWithNone:
        value: None
        name: str

    data = DataWithNone(value=None, name="test")
    encoded = json.dumps(data, cls=AdvancedJsonEncoder)
    decoded = json.loads(encoded)

    assert decoded == {"value": None, "name": "test"}

    # Test with enum
    class StatusEnum(Enum):
        NONE = None
        ACTIVE = "active"

    data = {"status": StatusEnum.NONE}
    encoded = json.dumps(data, cls=AdvancedJsonEncoder)
    decoded = json.loads(encoded)

    assert decoded == {"status": None}


def test_explicit_none_handling():
    """Test the explicit None handling in the default method of AdvancedJsonEncoder"""

    class CustomNone:
        """A custom class that returns None from its default encoding"""

        def __repr__(self):
            return "None"

    # Create an instance and encode it directly to trigger the default method
    encoder = AdvancedJsonEncoder()
    result = encoder.default(
        type(None)()
    )  # This explicitly calls default() with None type

    assert result is None

    # Test in context
    data = {"null_value": type(None)()}
    encoded = json.dumps(data, cls=AdvancedJsonEncoder)
    decoded = json.loads(encoded)

    assert decoded == {"null_value": None}


def test_callable_encoding_edge_cases():
    """Test various edge cases in callable encoding"""

    def simple_callable():
        pass

    encoded = json.dumps(simple_callable, cls=AdvancedJsonEncoder)
    assert '"<tests.test_json_encoder.simple_callable>"' == encoded

    # Test case for when o.__module__ exists but o.__name__ raises an exception
    class ComplexCallable:
        def __call__(self, *args, **kwargs):
            pass

    complex_callable = ComplexCallable()
    encoded = json.dumps(complex_callable, cls=AdvancedJsonEncoder)
    assert '"<tests.test_json_encoder.ComplexCallable>"' == encoded
