import os


def delete_files_with_pattern(directory, pattern="jpg?version"):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if pattern in file:
                file_path = os.path.join(root, file)
                os.remove(file_path)
                print(f"Deleted: {file_path}")


def delete_files_without_pattern(directory, pattern="wiki_spaces_MPHelpDesk_pages_"):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if pattern not in file:
                file_path = os.path.join(root, file)
                os.remove(file_path)
                print(f"Deleted: {file_path}")


if __name__ == "__main__":
    # current_directory = os.getcwd()
    # delete_files_with_pattern(current_directory)
    # delete_files_with_pattern("text")
    delete_files_without_pattern("text")
