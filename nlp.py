import spacy
import random
from spacy.training.example import Example
import shutil
import os

# Subprocess command to execute training_model.py
# training_data_command = ["python", "training_model.py"]

# try:
#     # Execute the subprocess command and capture output
#     training_data_output = subprocess.check_output(training_data_command, text=True)
#     print("Subprocess Output:", training_data_output)
# except subprocess.CalledProcessError as e:
#     print("Error:", e)
#     print("Command returned non-zero exit status.")
#     print("Output:", e.output)  


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


# Load training data from text file
def load_data(file_path):
    TRAINING_DATA = []
    with open(file_path, "r") as file:
        for line in file:
            line = line.strip()
            if line:
                parts = line.split("@@", 1)
                text = parts[0].strip()
                rest = parts[1].strip() if len(parts) > 1 else ""
                TRAINING_DATA.append((text, rest))
    return TRAINING_DATA

# Function to search 
def search(input_text, data):
    matches = []
    for text, rest in data:
        if input_text.lower() in text.lower():
            matches.append((text, rest))
    return matches


def main():
    file_choice = input("Enter 'P' to search from production file or 'U' to search from user file: ").lower()
    if file_choice == 'p':
        file_path = os.path.join(output_directory, "training_data.txt")
        TRAINING_DATA = load_data(file_path)
        while True:
            user_input = input("Enter Text or Type 'exit' to Quit: ")
            if user_input.lower() == 'exit':
                break
            results = search(user_input, TRAINING_DATA)
            if results:
                print("Matching results:")
                for i, (text, rest) in enumerate(results, 1):
                    print(f"{i}. {rest}")
            else:
                print("No matching results found.")
            
            choice = input("Enter the number corresponding to your action (1: Save, 0: Continue Search): ")
            if choice == '1':  # Save
                new_data = input("Enter new data to save: ")
                TRAINING_DATA.append((user_input, new_data))
                with open(file_path, "a") as file:
                    file.write(f"\n{user_input} @@ {new_data}")
                print("Data saved successfully.")
            elif choice == '0':  # Continue Search
                continue
            else:
                print("Invalid choice. Please enter a valid number.")
    elif file_choice == 'u':
        file_path = os.path.join(output_directory, "usersfile.txt")
        TRAINING_DATA = load_data(file_path)
        while True:
            user_input = input("Enter Text or Type 'exit' to Quit: ")
            if user_input.lower() == 'exit':
                break
            results = search(user_input, TRAINING_DATA)
            if results:
                print("Matching results:")
                for i, (text, rest) in enumerate(results, 1):
                    print(f"{i}. {rest}")
                
                choice = input("Enter the number corresponding to your action (1: Save, 2: Update, 3: Delete, 0: Continue Search): ")
                if choice == '1':  # Save
                    new_data = input("Enter new data to save: ")
                    TRAINING_DATA.append((user_input, new_data))
                    with open(file_path, "a") as file:
                        file.write(f"\n{user_input} @@ {new_data}")
                    print("Data saved successfully.")
                elif choice == '2':  # Update
                    text_to_update = input("Enter the text you want to update: ")
                    matching_results = [r for r in results if r[0] == text_to_update]
                    if matching_results:
                        updated_text = input("Enter the updated text: ")
                        updated_label = input("Enter the updated label: ")
                        TRAINING_DATA.remove((text_to_update, matching_results[0][1]))
                        TRAINING_DATA.append((updated_text, updated_label))
                        with open(file_path, "w") as file:
                            for text, rest in TRAINING_DATA:
                                file.write(f"{text} @@ {rest}\n")
                        print("Data updated successfully.")
                    else:
                        print("Text not found in results.")
                elif choice == '3':  # Delete
                    text_to_delete = input("Enter the text you want to delete: ")
                    matching_results = [r for r in results if r[0] == text_to_delete]
                    if matching_results:
                        TRAINING_DATA = [(text, rest) for text, rest in TRAINING_DATA if text != text_to_delete]
                        with open(file_path, "w") as file:
                            for text, rest in TRAINING_DATA:
                                file.write(f"{text} @@ {rest}\n")
                        print("Data deleted successfully.")
                    else:
                        print("Text not found in results.")
                elif choice == '0':  # Continue Search
                    continue
                else:
                    print("Invalid choice. Please enter a valid number.")
            else:
                print("No matching results found.")
                choice = input("Enter the number corresponding to your action (1: Save, 2: Update, 3: Delete, 0: Continue Search): ")
                if choice == '1':  # Save
                    new_data = input("Enter new data to save: ")
                    TRAINING_DATA.append((user_input, new_data))
                    with open(file_path, "a") as file:
                        file.write(f"\n{user_input} @@ {new_data}")
                    print("Data saved successfully.")
                elif choice == '2':  # Update
                    text_to_update = input("Enter the text you want to update: ")
                    updated_text = input("Enter the updated text: ")
                    updated_label = input("Enter the updated label: ")
                    TRAINING_DATA.append((updated_text, updated_label))
                    with open(file_path, "a") as file:
                        file.write(f"\n{updated_text} @@ {updated_label}")
                    print("Data updated successfully.")
                elif choice == '3':  # Delete
                    text_to_delete = input("Enter the text you want to delete: ")
                    TRAINING_DATA = [(text, rest) for text, rest in TRAINING_DATA if text != text_to_delete]
                    with open(file_path, "w") as file:
                        for text, rest in TRAINING_DATA:
                            file.write(f"{text} @@ {rest}\n")
                    print("Data deleted successfully.")
                elif choice == '0':  # Continue Search
                    continue
                else:
                    print("Invalid choice. Please enter a valid number.")
    else:
        print("Invalid choice. Exiting program.")


if __name__ == "__main__":
    output_directory = os.path.join(os.getenv('USERPROFILE'), 'Searchtool_Web')
    # Train using production file
    train_ner(output_directory+"\\training_data.txt")

    # Train using user file
    train_ner(output_directory+"\\usersfile.txt")

    model_name = "training_model"
    model_path = os.path.join(output_directory, model_name)

    # Load the saved model
    print("Loading model from:", model_path)
    nlp = spacy.load(model_path)
    main()
