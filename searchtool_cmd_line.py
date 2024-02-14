import re

# Function to read training data from a text file
def read_training_data(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
        training_data = {}
        for line in lines:
            key, value = line.strip().split(':')
            training_data[key.strip()] = value.strip()
    return training_data

# Function to convert input question to command
def convert_to_command(question, training_data):
    matching_commands = []
    
    for key, value in training_data.items():
        for keyword in key.split():
            if keyword.lower() in question.lower():
                matching_commands.append(value)
                break
    
    return matching_commands if matching_commands else ["Command not found for the given question."]


# Function to handle Unix file paths
def convert_unix_path(path):
    return path.replace("/etx/", "File:\\mount\\").replace("/", "\\")

# Main function
def main():
    # Specify the path to the text file containing training data
    training_data_file = "training_data.txt"
    training_data = read_training_data(training_data_file)

    while True:
        user_input = input("Enter your question (type 'exit' to quit): ")

        if user_input.lower() == 'exit':
            break

        matching_commands = convert_to_command(user_input, training_data)
        
        print("\n".join(matching_commands))

if __name__ == "__main__":
    main()
