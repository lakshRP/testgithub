import sys
import json
from transformers import pipeline

def summarize_feedback(feedbacks):
    summarizer = pipeline("summarization")

    feedback_text = " ".join(feedbacks)
    max_length = len(feedback_text.split())
    min_length = max_length // 2

    summary = summarizer(feedback_text, max_length=max_length, min_length=min_length, do_sample=False)

    return summary[0]['summary_text']

if __name__ == "__main__":
    feedbacks = json.loads(sys.stdin.read())
    summary = summarize_feedback(feedbacks)
    print(json.dumps({"summary": summary}))
