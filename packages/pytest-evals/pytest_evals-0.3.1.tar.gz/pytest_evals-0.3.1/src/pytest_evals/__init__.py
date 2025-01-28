"""A pytest plugin for running and analyzing LLM evaluation tests."""

from .plugin import (
    eval_bag,
    eval_bag_results,
    eval_results,
    eval_analysis_marker,
    eval_marker,
    out_path,
)
from .models import EvalResults, EvalBag
from .ipython_extension import load_ipython_extension

__all__ = [
    # Core functionality
    "EvalResults",
    "EvalBag",
    "eval_bag",
    "eval_bag_results",
    "eval_results",
    "out_path",
    # Marker utilities
    "eval_analysis_marker",
    "eval_marker",
    # Extensions
    "load_ipython_extension",
]
