import os


def get_prompt(name):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, name)
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()
