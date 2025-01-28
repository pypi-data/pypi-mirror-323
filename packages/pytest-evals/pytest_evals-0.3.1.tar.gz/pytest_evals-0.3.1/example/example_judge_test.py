import openai
import pytest

# Simple test data
TEST_DATA = [
    {
        "text": "I am experiencing a frustrating issue with my Python code where the variables keep returning undefined values and the loops aren't terminating properly. I need to debug this to find the root cause.",
        "label": "debugging Python code with undefined variables and non-terminating loops",
    },
    {
        "text": "In a display of remarkable agility, the swift orange cat gracefully propelled itself over the sleeping brown dog, who remained completely undisturbed by this acrobatic feat.",
        "label": "agile orange cat jumping over a sleeping brown dog",
    },
    {
        "text": "The LCD display on my desktop computer has been exhibiting concerning behavior lately - the screen keeps flickering intermittently and displaying random artifacts, making it very difficult to work.",
        "label": "LCD monitor displaying intermittent flickering and artifacts",
    },
]


@pytest.fixture
def summarizer():
    def _summarize(text: str) -> str:
        """Simple LLM agent that summarizes text"""
        res = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "Write a concise summary of the text.",
                },
                {"role": "user", "content": text},
            ],
        )
        return res.choices[0].message.content  # type: ignore

    return _summarize


@pytest.fixture
def judge():
    def _judge(text, summary, main_subject) -> bool:
        """LLM as a judge that determines if the summary is about the main subject"""
        resp = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "Decide whether the summary is about the main subject. "
                    "Reply ONLY with either true or false.",
                },
                {
                    "role": "user",
                    "content": f"Original Text: {text}\nSummary: {summary}\nMain Subject: {main_subject}",
                },
            ],
        )
        return resp.choices[0].message.content.lower() == "true"  # type: ignore

    return _judge


@pytest.mark.eval(name="summary")
@pytest.mark.parametrize("case", TEST_DATA)
def test_classifier(case: dict, eval_bag, summarizer, judge) -> None:
    # Store input and prediction for analysis
    eval_bag.input_text = case["text"]
    eval_bag.label = case["label"]  # the label is the main subject of the text
    eval_bag.prediction = summarizer(case["text"])
    eval_bag.judgement = judge(eval_bag.input_text, eval_bag.prediction, eval_bag.label)

    # Basic assertion
    assert eval_bag.judgement  # Assert that the summary is about the main subject


@pytest.mark.eval_analysis(name="summary")
def test_analysis(eval_results):
    # Calculate various metrics
    total_samples = len(eval_results)

    # Subject relevance (based on judge's assessment)
    relevant_summaries = sum(1 for r in eval_results if r.result.judgement)
    subject_accuracy = relevant_summaries / total_samples if total_samples else 0

    # Length analysis
    avg_summary_length = (
        sum(len(r.result.prediction.split()) for r in eval_results) / total_samples
        if total_samples
        else 0
    )
    avg_input_length = (
        sum(len(r.result.input_text.split()) for r in eval_results) / total_samples
        if total_samples
        else 0
    )
    compression_ratio = avg_summary_length / avg_input_length if avg_input_length else 0

    # Print metrics
    print(f"Subject Accuracy: {subject_accuracy:.2%}")
    print(f"Average Summary Length: {avg_summary_length:.1f} words")
    print(f"Average Input Length: {avg_input_length:.1f} words")
    print(f"Compression Ratio: {compression_ratio:.2f}")

    # Basic quality assertions
    assert subject_accuracy >= 0.7, "Subject accuracy below threshold"
    assert 0.2 <= compression_ratio <= 0.8, "Compression ratio outside acceptable range"
