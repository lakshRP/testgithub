import sys
import json

def summarize_feedback(feedbacks):
    # Implement your summarization logic here.
    # For demonstration, we'll just join the feedbacks with a summary statement.
    summary = "Summary of feedbacks: " + " ".join(feedbacks)
    return summary

if __name__ == "__main__":
    feedbacks = json.loads(sys.stdin.read())
    summary = summarize_feedback(feedbacks)
    print(summary)