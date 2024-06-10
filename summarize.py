import sys
import json
from transformers import pipeline

def summarize_feedback(feedbacks):
    summarizer = pipeline("summarization")

    feedback_text = " ".join(feedbacks)
    lfeedback = len(feedback_text)

    # Define max_length and min_length with reasonable values
    max_length = min(512, lfeedback // 2)  # Limit max_length to 512 or half the text length
    min_length = max(30, lfeedback // 8)  # Ensure min_length is at least 30 or one-eighth the text length

    # Generate the summary with num_beams for better quality and truncation for complete sentences
    summary = summarizer(
        feedback_text, 
        max_length=max_length, 
        min_length=min_length, 
        do_sample=False, 
        num_beams=4, 
        truncation=True
    )

    return summary[0]['summary_text']

if __name__ == "__main__":
    feedbacks = json.loads(sys.stdin.read())
    summary = summarize_feedback(feedbacks)
    print(json.dumps({"summary": summary}))