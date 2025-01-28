import dataclasses
from typing import Any, Mapping

from pytest_harvest import ResultsBag


class EvalBag(ResultsBag):
    pass


@dataclasses.dataclass
class EvalResults:
    """Data class representing an evaluation result."""

    eval_name: str
    status: str
    duration_ms: float
    test_params: dict[str, Any]
    test_name: str
    result: ResultsBag

    @classmethod
    def from_result_bag(cls, item: Mapping[str, Any]) -> "EvalResults":
        """Create an EvalResult instance from a result bag item."""
        return cls(
            eval_name=item["eval_name"],
            status=item["status"],
            duration_ms=item["duration_ms"],
            test_params=item["params"],
            test_name=item["pytest_obj_name"],
            result=ResultsBag(item["fixtures"]["eval_bag"])
            if "eval_bag" in item["fixtures"]
            else ResultsBag(),
        )
