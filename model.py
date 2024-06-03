from transformers import BartTokenizer, BartForConditionalGeneration, Trainer, TrainingArguments
import torch
from torch.utils.data import Dataset

# Function to save the model and tokenizer
def save_model(model, tokenizer, save_directory):
    model.save_pretrained(save_directory)
    tokenizer.save_pretrained(save_directory)

# Custom Dataset for handling the input data
class SummaryDataset(Dataset):
    def __init__(self, encodings):
        self.encodings = encodings

    def __getitem__(self, idx):
        return {key: torch.tensor(val[idx]) for key, val in self.encodings.items()}

    def __len__(self):
        return len(self.encodings['input_ids'])

# Function to load the model and tokenizer from a saved directory
def load_model(model_path):
    tokenizer = BartTokenizer.from_pretrained(model_path)
    model = BartForConditionalGeneration.from_pretrained(model_path)
    return tokenizer, model

# Function to generate summary using the model
def generate_summary(text, tokenizer, model):
    inputs = tokenizer(text, return_tensors="pt", max_length=1000, truncation=True)
    summary_ids = model.generate(inputs['input_ids'], max_length=500, min_length=200, length_penalty=2.0, num_beams=4, early_stopping=True)
    summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
    return summary

def ghmain(text):
    # Initialize tokenizer and model from pre-trained
    tokenizer = BartTokenizer.from_pretrained('facebook/bart-large-cnn')
    model = BartForConditionalGeneration.from_pretrained('facebook/bart-large-cnn')

    # Example of training code here
    # Here you would include your dataset and modify this code to train your model
    # For demonstration, we skip training here

    # Save the model and tokenizer
    save_directory = "./model_bart"
    save_model(model, tokenizer, save_directory)

    # Load the model and tokenizer
    tokenizer, model = load_model(save_directory)

    # Sample text to summarize
    text2 = text
    
    # Generate the summary
    summary = generate_summary(text2, tokenizer, model)
    print("Generated Summary:", summary)

if __name__ == '__main__':
    main()
