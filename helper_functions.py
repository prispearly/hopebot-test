import json

def get_message_from_json(file_path):
    # Read and return the JSON content from the specified file path
    with open(file_path, 'r') as file:
        message = json.load(file)
    return message