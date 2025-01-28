import json
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from pytest_evals import eval_analysis_marker
from pytest_evals import plugin


def test_eval_marker_configuration(pytester):
    """Test basic eval marker functionality

    Verifies that a test with properly configured eval marker:
    - Is collected when --run-eval is used
    - Successfully executes and passes
    """
    pytester.makepyfile("""
        import pytest
        
        @pytest.mark.eval(name="test_eval")
        def test_simple():
            assert True
    """)

    result = pytester.runpytest("--run-eval")
    result.assert_outcomes(passed=1)


def test_eval_analysis_marker_configuration(pytester):
    """Test that tests are properly selected/skipped based on eval/eval-analysis markers

    Verifies:
    - With --run-eval: eval_analysis tests are skipped
    - With --run-eval-analysis: eval tests are skipped
    """

    pytester.makepyfile("""
        import pytest
        
        @pytest.mark.eval_analysis(name="test_eval")
        def test_analysis(eval_results):
            assert len(eval_results) == 0
    """)

    result = pytester.runpytest("--run-eval-analysis")
    result.assert_outcomes(passed=1)


def test_missing_name_in_eval_marker(pytester):
    """Test that eval marker requires name parameter"""
    pytester.makepyfile("""
        import pytest
        
        @pytest.mark.eval
        def test_simple():
            assert True
    """)

    result = pytester.runpytest("--run-eval")
    assert result.ret != 0


# Comprehensive workflow test
def test_complete_evaluation_workflow(pytester):
    """Test complete evaluation workflow including fixture behavior"""
    pytester.makepyfile("""
        import pytest
        
        TEST_DATA = [
            {"input": "test1", "expected": True},
            {"input": "test2", "expected": False},
        ]
        
        @pytest.fixture
        def mock_classifier():
            def classify(text: str) -> bool:
                return "test1" in text
            return classify
        
        # Evaluation phase with fixture usage
        @pytest.mark.eval(name="test_classifier")
        @pytest.mark.parametrize("case", TEST_DATA)
        def test_classifier(case, eval_bag, mock_classifier):
            eval_bag.input = case["input"]
            eval_bag.expected = case["expected"]
            eval_bag.prediction = mock_classifier(case["input"])
            eval_bag.metadata = {"test_type": "classification"}
            assert eval_bag.prediction == case["expected"]
        
        # Analysis phase with enhanced fixture verification
        @pytest.mark.eval_analysis(name="test_classifier")
        def test_analysis(eval_results):
            assert len(eval_results) == 2
            
            # Verify fixture data preservation
            for result in eval_results:
                assert hasattr(result.result, "metadata")
                assert result.result.metadata["test_type"] == "classification"
            
            # Verify analysis results
            correct = sum(1 for r in eval_results 
                        if r.result.prediction == r.result.expected)
            accuracy = correct / len(eval_results)
            assert accuracy == 1.0
    """)

    # Run evaluation phase
    result_eval = pytester.runpytest("--run-eval")
    result_eval.assert_outcomes(passed=2, skipped=1)

    # Run analysis phase
    result_analysis = pytester.runpytest("--run-eval-analysis")
    result_analysis.assert_outcomes(passed=1, skipped=2)


def test_output_file_creation(pytester, tmp_path):
    """Test that results are properly saved to output file"""
    out_dir = tmp_path / "test-output"
    out_dir.mkdir(exist_ok=True)

    pytester.makepyfile("""
        import pytest
        
        @pytest.mark.eval(name="test_eval")
        def test_simple(eval_bag):
            eval_bag.result = "test_value"
            assert True
    """)

    result = pytester.runpytest("--run-eval", f"--out-path={out_dir}", "-v")
    result.assert_outcomes(passed=1)

    results_file = Path(out_dir) / "eval-results-raw.json"
    assert results_file.exists()

    with open(results_file) as f:
        results = json.load(f)
        assert any(
            "test_value" in str(v.get("fixtures").get("eval_bag"))
            for v in results.values()
        )


def test_eval_marker_collection_scenarios(pytester):
    """Test different scenarios for eval marker collection"""
    pytester.makepyfile("""
        import pytest
        from pytest_harvest import get_session_results_dct
        
        # Case 1: No pytestmark attribute
        def test_no_pytestmark():
            assert True
            
        # Case 2: Has pytestmark but not the eval mark
        @pytest.mark.skip
        def test_other_mark():
            assert True
            
        # Case 3: Class without pytestmark
        class TestClass:
            def test_method(self):
                assert True
                
        # Case 4: Class with non-eval pytestmark
        class TestClassWithMark:
            pytestmark = [pytest.mark.skip]
            def test_no_eval_marker(self):
                assert True
            
        # Case 5: Test with eval mark (should be included)
        @pytest.mark.eval(name="test")
        def test_with_eval(eval_bag):
            eval_bag.value = 42
            assert True
    """)

    result = pytester.runpytest("--run-eval")
    result.assert_outcomes(passed=1)


@pytest.mark.parametrize(
    "scenario",
    [
        # Empty file scenario - expect empty results
        ("empty_file", {}),
        # Valid data scenario - expect one result with specific values
        (
            "valid_data",
            {
                "test_1": {
                    "eval_name": "sample_eval",
                    "fixtures": {"eval_bag": {"value": 42}},
                }
            },
        ),
        # Missing file scenario - expect empty results
        ("missing_file", None),
    ],
)
def test_eval_bag_results_scenarios(pytester, tmp_path, scenario):
    """Test eval_bag_results behavior with different results file states

    Parameters:
        scenario: Tuple of (scenario_name, file_content) where:
            - empty_file: Results file exists but is empty ({})
            - valid_data: Results file exists with valid test data
            - missing_file: Results file does not exist (None)

    Each scenario should handle the case gracefully and provide appropriate results.
    """
    scenario_name, file_content = scenario
    out_dir = tmp_path / "test-out"
    out_dir.mkdir(parents=True)
    results_file = out_dir / "eval-results-raw.json"

    if file_content is not None:
        results_file.parent.mkdir(exist_ok=True)
        results_file.write_text(json.dumps(file_content))

    pytester.makepyfile(f"""
        def test_results(eval_bag_results):
            if "{scenario_name}" == "empty_file":
                assert len(eval_bag_results) == 0
            elif "{scenario_name}" == "valid_data":
                assert len(eval_bag_results) == 1
                assert "test_1" in eval_bag_results
                assert eval_bag_results["test_1"]["eval_name"] == "sample_eval"
            else:  # missing_file
                assert len(eval_bag_results) == 0
    """)

    result = pytester.runpytest(f"--out-path={out_dir}")
    result.assert_outcomes(passed=1)


# Error handling and configuration tests
def test_invalid_marker_combination(pytester):
    """Test that a test cannot have both eval and eval_analysis markers"""
    pytester.makepyfile("""
        import pytest
        
        @pytest.mark.eval(name="test")
        @pytest.mark.eval_analysis(name="test")
        def test_invalid():
            assert True
    """)

    result = pytester.runpytest("--run-eval")
    assert result.ret != 0


def test_suppress_failed_exit_code_scenarios(pytester):
    """Test all scenarios related to suppressing failed exit codes"""
    pytester.makepyfile("""
        import pytest
        
        @pytest.mark.eval(name="test_eval")
        def test_failing():
            assert False
            
        @pytest.mark.eval(name="test_eval")
        def test_internal_error():
            raise pytest.UsageError("Internal error")
    """)

    # Case 1: Without suppress flag - should fail with non-zero exit code
    result1 = pytester.runpytest("--run-eval")
    result1.assert_outcomes(failed=2)
    assert result1.ret != 0

    # Case 2: With suppress flag - expect zero exit code despite failures
    result2 = pytester.runpytest("--run-eval", "--supress-failed-exit-code")
    result2.assert_outcomes(failed=2)
    assert result2.ret == 0


def test_xdist_eval_flags_unit():
    """Unit test for xdist session with both eval and eval-analysis flags"""
    config = Mock()
    config.getoption.side_effect = lambda x: x in ["--run-eval", "--run-eval-analysis"]

    with patch.object(plugin, "is_xdist_session", return_value=True):
        with pytest.raises(ValueError, match="cannot be used together"):
            plugin.pytest_collection_modifyitems(config, [])


def test_xdist_eval_flags_integration(pytester):
    """Integration test for xdist compatibility with eval flags

    Verifies that attempting to run eval and eval-analysis tests together
    in distributed mode raises appropriate error with explanation message
    """
    pytester.makepyfile("""
        import pytest
        
        @pytest.mark.eval(name="test")
        def test_eval():
            assert True
            
        @pytest.mark.eval_analysis(name="test")
        def test_analysis(eval_results):
            assert True
    """)

    result = pytester.runpytest("--run-eval", "--run-eval-analysis", "-n", "2")
    assert result.ret != 0
    result.stdout.fnmatch_lines(
        "*evaluation analysis must run after the evaluation tests*"
    )


def test_marker_basic_cases():
    """Test eval_analysis_marker validation logic

    Tests multiple marker scenarios:
    - Valid marker with name parameter
    - Invalid marker missing name parameter
    - No markers present
    - Other unrelated markers
    - Mixed markers (eval with other marks)

    Verifies proper marker validation and selection in each case.
    """
    # Valid marker
    valid = pytest.mark.eval_analysis(name="test")
    assert eval_analysis_marker([valid.mark]) == valid.mark

    # Missing name param
    invalid = pytest.mark.eval_analysis()
    with pytest.raises(ValueError, match="must have a 'name' argument"):
        eval_analysis_marker([invalid.mark])

    # No markers
    assert eval_analysis_marker([]) is None

    # Other markers
    other = pytest.mark.skip(reason="skip")
    assert eval_analysis_marker([other.mark]) is None

    # Mixed markers
    mixed = [other.mark, valid.mark]
    assert eval_analysis_marker(mixed) == valid.mark


def test_eval_analysis_marker_selection(pytester):
    """Test marker skipping behavior"""
    pytester.makepyfile("""
        import pytest
        
        @pytest.mark.eval(name="test")
        def test_eval():
            pass
            
        @pytest.mark.eval_analysis(name="test")
        def test_analysis():
            pass
    """)

    # Test with run_eval
    result1 = pytester.runpytest("--run-eval")
    result1.assert_outcomes(skipped=1, passed=1)

    # Test with run_eval_analysis
    result2 = pytester.runpytest("--run-eval-analysis")
    result2.assert_outcomes(skipped=1, passed=1)


def test_worker_session_finish(pytestconfig):
    """Test worker session finish handling"""

    class WorkerSession:
        class Config:
            workerinput = {}

            def getoption(self, *args, **kwargs):
                return False

        config = Config()
        exitstatus = 0

    assert plugin.pytest_sessionfinish(WorkerSession()) is None


def test_save_evals_csv_option(pytester, tmp_path):
    """Test the --save-evals-csv option with various scenarios"""
    out_dir = tmp_path / "test-output"
    out_dir.mkdir(exist_ok=True)

    # Create test file with evaluation test
    pytester.makepyfile("""
        import pytest
        
        @pytest.mark.eval(name="test_eval")
        def test_simple(eval_bag):
            eval_bag.result = "test_value"
            eval_bag.metadata = {"key": "value"}
            assert True
    """)

    result1 = pytester.runpytest(f"--out-path={out_dir}", "--save-evals-csv")
    assert result1.ret != 0
    result1.stderr.fnmatch_lines(
        "*--save-evals-csv option can only be used with the --run-eval option*"
    )

    # Case 2: Test with both flags and verify CSV creation
    result2 = pytester.runpytest(
        "--run-eval", f"--out-path={out_dir}", "--save-evals-csv", "-v"
    )
    result2.assert_outcomes(passed=1)

    # Verify both JSON and CSV files exist
    csv_file = out_dir / "eval-results-raw.csv"
    json_file = out_dir / "eval-results-raw.json"
    assert csv_file.exists()
    assert json_file.exists()


def test_save_evals_csv_missing_pandas(pytester, tmp_path, monkeypatch):
    """Test handling of missing pandas when --save-evals-csv is used"""
    out_dir = tmp_path / "test-output"
    out_dir.mkdir(exist_ok=True)

    # Mock pandas to raise ImportError
    import sys

    with patch.dict(sys.modules, {"pandas": None}):
        pytester.makepyfile("""
            import pytest
            
            @pytest.mark.eval(name="test_eval")
            def test_simple():
                assert True
        """)

        result = pytester.runpytest(
            "--run-eval", f"--out-path={out_dir}", "--save-evals-csv"
        )
        assert result.ret != 0
        result.stderr.fnmatch_lines(
            "*The --save-evals-csv option requires the pandas library*"
        )


def test_csv_data_normalization(pytester, tmp_path):
    """Test that complex data structures are properly normalized in CSV output"""
    out_dir = tmp_path / "test-output"
    out_dir.mkdir(exist_ok=True)

    pytester.makepyfile("""
        import pytest
        from datetime import datetime
        
        TEST_DATA = [
            {"input": "test1", "expected": True},
            {"input": "test2", "expected": False}
        ]
        
        @pytest.mark.eval(name="test_eval")
        @pytest.mark.parametrize("case", TEST_DATA)
        def test_complex_data(eval_bag, case):
            eval_bag.nested_data = {
                "list": [1, 2, 3],
                "dict": {"a": 1, "b": 2},
                "date": str(datetime.now()),
                "case": case
            }
            assert True
    """)

    result = pytester.runpytest(
        "--run-eval", f"--out-path={out_dir}", "--save-evals-csv", "-v"
    )
    result.assert_outcomes(passed=2)  # Two test cases due to parametrize

    # Verify CSV was created with normalized data
    csv_file = out_dir / "eval-results-raw.csv"
    assert csv_file.exists()

    # Read the CSV content to verify structure (if pandas is available)
    try:
        import pandas as pd

        df = pd.read_csv(csv_file)
        assert not df.empty
        assert "eval_bag.nested_data.date" in df.columns
    except ImportError:
        pass  # Skip detailed verification if pandas isn't available
