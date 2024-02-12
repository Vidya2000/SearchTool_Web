import os
import shutil
import spacy
import random
from spacy.training.example import Example

# Joining the user's home directory with 'Searchtool_Web'
output_directory = os.path.join(os.getenv('USERPROFILE'), 'Searchtool_Web')

# Print the constructed output directory for verification
print("Output Directory:", output_directory)

def train_ner(file_path):
    # Check if the output directory exists, if not, create it
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    # Load a blank English model
    nlp = spacy.blank("en")

    # Check if the user file exists in the output directory, if not, create it
    user_file_path = os.path.join(output_directory, "usersfile.txt")
    if not os.path.exists(user_file_path):
        with open(user_file_path, "w") as user_file:
            print("User file created successfully")

    # Copy the production file from the installer location to the output directory
    production_file_path = "training_data.txt"
    if os.path.exists(production_file_path):
        shutil.copy(production_file_path, output_directory)
        print("Production file copied successfully")
    else:
        print("Production file not found. Please specify the correct path.")

    # Load training data from text file
    TRAINING_DATA = []
    with open(file_path, "r") as file:
        for line in file:
            line = line.strip()
            if line:
                text, label = line.split("@@")  # Split text and label using @@
                text = text.strip()  # Remove leading and trailing whitespaces
                label = label.strip()  # Remove leading and trailing whitespaces
                entities = [(0, len(text), label)] 
                TRAINING_DATA.append((text, {"entities": entities}))

    # Add ner component to the pipeline
    ner = nlp.add_pipe("ner")

    # Add labels to the ner component
    for _, annotations in TRAINING_DATA:
        for ent in annotations.get("entities"):
            ner.add_label(ent[2])

    # Train the ner component
    random.shuffle(TRAINING_DATA)
    train_data = []
    for text, annotations in TRAINING_DATA:
        doc = nlp.make_doc(text)
        example = Example.from_dict(doc, annotations)
        train_data.append(example)

    nlp.begin_training()
    for _ in range(10): 
        random.shuffle(train_data)
        losses = {}
        for example in train_data:
            nlp.update([example], losses=losses)

    # Save the model in the output directory with a specified model name
    model_name = "training_model"
    output_model_path = os.path.join(output_directory, model_name)
    nlp.to_disk(output_model_path)
    print("Model saved successfully:", output_model_path)

# Train using production file
train_ner(output_directory+"\\training_data.txt")

# Train using user file
train_ner(output_directory+"\\usersfile.txt")
