import openai
import pytest

# Simple test data
TEST_DATA = [
    {"text": "I need to debug this Python code", "label": True},
    {"text": "The cat jumped over the lazy dog", "label": False},
    {"text": "My monitor keeps flickering", "label": True},
]


@pytest.fixture
def classifier():
    def _classify(text: str) -> bool:
        """Simple LLM agent that classifies text as computer-related or not."""
        resp = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "Is this text about a computer-related subject?"
                    "Reply ONLY with either true or false.",
                },
                {"role": "user", "content": text},
            ],
        )
        return resp.choices[0].message.content.lower() == "true"  # type: ignore

    return _classify


@pytest.mark.eval(name="computer_classifier")
@pytest.mark.parametrize("case", TEST_DATA)
def test_classifier(case: dict, eval_bag, classifier) -> None:
    # Store input and prediction for analysis
    eval_bag.input_text = case["text"]
    eval_bag.label = case["label"]
    eval_bag.prediction = classifier(case["text"])

    # Basic assertion
    assert eval_bag.prediction == eval_bag.label


@pytest.mark.eval_analysis(name="computer_classifier")
def test_analysis(eval_results):
    # Calculate true positives, false positives, and false negatives
    true_positives = sum(
        1 for r in eval_results if r.result.prediction and r.result.label
    )
    false_positives = sum(
        1 for r in eval_results if r.result.prediction and not r.result.label
    )
    false_negatives = sum(
        1 for r in eval_results if not r.result.prediction and r.result.label
    )

    total_predictions = len(eval_results)
    correct_predictions = sum(
        1 for r in eval_results if r.result.prediction == r.result.label
    )

    # Calculate metrics
    accuracy = correct_predictions / total_predictions if total_predictions else 0
    precision = (
        true_positives / (true_positives + false_positives)
        if (true_positives + false_positives)
        else 0
    )
    recall = (
        true_positives / (true_positives + false_negatives)
        if (true_positives + false_negatives)
        else 0
    )
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0

    print(f"Accuracy: {accuracy:.2%}")
    print(f"Precision: {precision:.2%}")
    print(f"Recall: {recall:.2%}")
    print(f"F1: {f1:.2%}")

    assert f1 >= 0.7
