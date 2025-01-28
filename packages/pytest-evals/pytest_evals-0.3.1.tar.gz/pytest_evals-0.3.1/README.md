<div id="top"></div>

# `pytest-evals` 🚀

Test your LLM outputs against examples - no more manual checking! A (minimalistic) pytest plugin that helps you to
evaluate that your LLM is giving good answers.

[![PyPI version](https://img.shields.io/pypi/v/pytest-evals.svg)](https://pypi.org/p/pytest-evals)
[![License](https://img.shields.io/github/license/AlmogBaku/pytest-evals.svg)](https://github.com/AlmogBaku/pytest-evals/blob/main/LICENSE)
[![Issues](https://img.shields.io/github/issues/AlmogBaku/pytest-evals.svg)](https://github.com/AlmogBaku/pytest-evals/issues)
[![Stars](https://img.shields.io/github/stars/AlmogBaku/pytest-evals.svg)](https://github.com/AlmogBaku/pytest-evals/stargazers)

# 🧐 Why pytest-evals?

Building LLM applications is exciting, but how do you know they're actually working well? `pytest-evals` helps you:

- 🎯 **Test & Evaluate:** Run your LLM prompt against many cases
- 📈 **Track & Measure:** Collect metrics and analyze the overall performance
- 🔄 **Integrate Easily:** Works with pytest, Jupyter notebooks, and CI/CD pipelines
- ✨ **Scale Up:** Run tests in parallel with [`pytest-xdist`](https://pytest-xdist.readthedocs.io/) and
  asynchronously with [`pytest-asyncio`](https://pytest-asyncio.readthedocs.io/).

# 🚀 Getting Started

To get started, install `pytest-evals` and write your tests:

```bash
pip install pytest-evals
```

#### ⚡️ Quick Example

For example, say you're building a support ticket classifier. You want to test cases like:

| Input Text                                             | Expected Classification |
|--------------------------------------------------------|-------------------------|
| My login isn't working and I need to access my account | account_access          |
| Can I get a refund for my last order?                  | billing                 |
| How do I change my notification settings?              | settings                |

`pytest-evals` helps you automatically test how your LLM perform against these cases, track accuracy, and ensure it
keeps working as expected over time.

```python
# Predict the LLM performance for each case
@pytest.mark.eval(name="my_classifier")
@pytest.mark.parametrize("case", TEST_DATA)
def test_classifier(case: dict, eval_bag, classifier):
    # Run predictions and store results
    eval_bag.prediction = classifier(case["Input Text"])
    eval_bag.expected = case["Expected Classification"]
    eval_bag.accuracy = eval_bag.prediction == eval_bag.expected


# Now let's see how our app performing across all cases...
@pytest.mark.eval_analysis(name="my_classifier")
def test_analysis(eval_results):
    accuracy = sum([result.accuracy for result in eval_results]) / len(eval_results)
    print(f"Accuracy: {accuracy:.2%}")
    assert accuracy >= 0.7  # Ensure our performance is not degrading 🫢
```

Then, run your evaluation tests:

```bash
# Run test cases
pytest --run-eval

# Analyze results
pytest --run-eval-analysis
```

## 😵‍💫 Why Another Eval Tool?

**Evaluations are just tests.** No need for complex frameworks or DSLs. `pytest-evals` is minimalistic by design:

- Use `pytest` - the tool you already know
- Keep tests and evaluations together
- Focus on logic, not infrastructure

It just collects your results and lets you analyze them as a whole. Nothing more, nothing less.
<p align="right">(<a href="#top">back to top</a>)</p>

# 📚 User Guide

Check out our detailed guides and examples:

- [Basic evaluation](example/example_test.py)
- [Basic of LLM as a judge evaluation](example/example_judge_test.py)
- [Notebook example](example/example_notebook.ipynb)
- [Advanced notebook example](example/example_notebook_advanced.ipynb)

## 🤔 How It Works

Built on top of [pytest-harvest](https://smarie.github.io/python-pytest-harvest/), `pytest-evals` splits evaluation into
two phases:

1. **Evaluation Phase**: Run all test cases, collecting results and metrics in `eval_bag`. The results are saved in a
   temporary file to allow the analysis phase to access them.
2. **Analysis Phase**: Process all results at once through `eval_results` to calculate final metrics

This split allows you to:

- Run evaluations in parallel (since the analysis test MUST run after all cases are done, we must run them separately)
- Make pass/fail decisions on the overall evaluation results instead of individual test failures (by passing the
  `--supress-failed-exit-code --run-eval` flags)
- Collect comprehensive metrics

**Note**: When running evaluation tests, the rest of your test suite will not run. This is by design to keep the results
clean and focused.

## 💾 Saving case results
By default, `pytest-evals` saves the results of each case in a json file to allow the analysis phase to access them.
However, this might not be a friendly format for deeper analysis. To save the results in a more friendly format, as a
CSV file, use the `--save-evals-csv` flag:

```bash
pytest --run-eval --save-evals-csv
```

## 📝 Working with a notebook

It's also possible to run evaluations from a notebook. To do that, simply
install [ipytest](https://github.com/chmp/ipytest), and load the extension:

```python
%load_ext pytest_evals
```

Then, use the magic commands `%%ipytest_eval` in your cell to run evaluations. This will run the evaluation phase and
then the analysis phase. By default, using this magic will run both `--run-eval` and `--run-eval-analysis`, but you can
specify your own flags by passing arguments right after the magic command (e.g., `%%ipytest_eval --run-eval`).

```python
%%ipytest_eval
import pytest


@pytest.mark.eval(name="my_eval")
def test_agent(eval_bag):
    eval_bag.prediction = agent.run(case["input"])


@pytest.mark.eval_analysis(name="my_eval")
def test_analysis(eval_results):
    print(f"F1 Score: {calculate_f1(eval_results):.2%}")
```

You can see an example of this in the [`example/example_notebook.ipynb`](example/example_notebook.ipynb) notebook. Or
look at the [advanced example](example/example_notebook_advanced.ipynb) for a more complex example that tracks multiple
experiments.
<p align="right">(<a href="#top">back to top</a>)</p>

## 🏗️ Production Use

### 📚 Managing Test Data (Evaluation Set)

It's recommended to use a CSV file to store test data. This makes it easier to manage large datasets and allows you to
communicate with non-technical stakeholders.

To do this, you can use `pandas` to read the CSV file and pass the test cases as parameters to your tests using
`@pytest.mark.parametrize` 🙃 :

```python
import pandas as pd
import pytest

test_data = pd.read_csv("tests/testdata.csv")


@pytest.mark.eval(name="my_eval")
@pytest.mark.parametrize("case", test_data.to_dict(orient="records"))
def test_agent(case, eval_bag, agent):
    eval_bag.prediction = agent.run(case["input"])
```

In case you need to select a subset of the test data (e.g., a golden set), you can simply define an environment variable
to indicate that, and filter the data with `pandas`.

### 🔀 CI Integration

Run tests and analysis as separate steps:

```yaml
evaluate:
  steps:
    - run: pytest --run-eval -n auto --supress-failed-exit-code  # Run cases in parallel
    - run: pytest --run-eval-analysis  # Analyze results
```

Use `--supress-failed-exit-code` with `--run-eval` - let the analysis phase determine success/failure. **If all your
cases pass, your evaluation set is probably too small!**

### ⚡️ Parallel Testing

As your evaluation set grows, you may want to run your test cases in parallel. To do this, install
[`pytest-xdist`](https://pytest-xdist.readthedocs.io/). `pytest-evals` will support that out of the box 🚀.

```bash
run: pytest --run-eval -n auto
```

<p align="right">(<a href="#top">back to top</a>)</p>

# 👷 Contributing

Contributions make the open-source community a fantastic place to learn, inspire, and create. Any contributions you make
are **greatly appreciated** (not only code! but also documenting, blogging, or giving us feedback) 😍.

Please fork the repo and create a pull request if you have a suggestion. You can also simply open an issue to give us
some feedback.

**Don't forget to give the project [a star](#top)! ⭐️**

For more information about contributing code to the project, read the [CONTRIBUTING.md](CONTRIBUTING.md) guide.

# 📃 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
<p align="right">(<a href="#top">back to top</a>)</p>