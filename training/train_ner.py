import json
import random
import spacy
from spacy.training.example import Example
import os

def load_data(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    formatted_data = []
    for item in data:
        text = item["text"]
        entities = []
        for ent_text, label in item["entities"].items():
            start = text.find(ent_text)
            if start != -1:
                end = start + len(ent_text)
                entities.append((start, end, label))
        formatted_data.append((text, {"entities": entities}))
    return formatted_data

def train_ner(data_filepath, output_dir, iterations=30):
    train_data = load_data(data_filepath)
    
    # Load base model
    try:
        nlp = spacy.load("en_core_web_sm")
    except OSError:
        nlp = spacy.blank("en")
        
    # Add NER if not present
    if "ner" not in nlp.pipe_names:
        ner = nlp.add_pipe("ner", last=True)
    else:
        ner = nlp.get_pipe("ner")
        
    # Add labels
    for _, annotations in train_data:
        for ent in annotations.get("entities"):
            ner.add_label(ent[2])
            
    # Disable other pipes during training
    other_pipes = [pipe for pipe in nlp.pipe_names if pipe != "ner"]
    with nlp.disable_pipes(*other_pipes):
        optimizer = nlp.resume_training()
        for itn in range(iterations):
            random.shuffle(train_data)
            losses = {}
            for text, annotations in train_data:
                doc = nlp.make_doc(text)
                example = Example.from_dict(doc, annotations)
                nlp.update([example], drop=0.35, sgd=optimizer, losses=losses)
            print(f"Iteration {itn} Losses:", losses)
            
    # Save model
    os.makedirs(output_dir, exist_ok=True)
    nlp.to_disk(output_dir)
    print(f"Saved model to {output_dir}")

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(base_dir, "data", "train_data.json")
    out_path = os.path.join(os.path.dirname(base_dir), "models", "custom_ner")
    train_ner(data_path, out_path)
