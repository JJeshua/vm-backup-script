import os
import shutil
from datetime import datetime, timedelta


SOURCE_VMS_FOLDER_PATH = r"C:\Users\admin\Desktop\Start"
DESTINATION_FOLDER_PATH = r"C:\Users\admin\Desktop\Destination"


class Folder:
    def __init__(self, name, parent_path, destination_path=None):
        self.name = name
        self.parent_path = parent_path
        self.destination_path = destination_path
        self.current_datetime = None

        self.parse_folder_name_and_datetime()

    def generate_destination_full_folder_path(self):
        if not self.name or not self.current_datetime:
            raise ValueError("Folder name or datetime is null")
        return f"{self.destination_path}\\{self.name}_{self.current_datetime}"

    def generate_source_full_folder_path(self):
        if not self.name:
            raise ValueError("Folder name or datetime is null")
        return f"{self.parent_path}\\{self.name}"

    def is_older_than_30_days(self):
        current_datetime = datetime.now()
        return (current_datetime - self.current_datetime) > timedelta(days=30)

    def set_datetime_to_current_datetime(self):
        current_datetime = datetime.now()
        formatted_datetime = current_datetime.strftime("%Y%m%d%H%M%S")
        self.current_datetime = formatted_datetime

    def set_destination_path(self, path):
        self.destination_path = path

    def parse_folder_name_and_datetime(self):
        try:
            # Split the folder name by the last underscore
            base_name, datetime_str = self.name.rsplit("_", 1)
            # Convert the datetime string to a datetime object
            folder_datetime = datetime.strptime(datetime_str, "%Y%m%d%H%M%S")
            self.name = base_name
            self.current_datetime = datetime_str

            return

        # If the folder does not have a datetime suffix, do nothing
        except (IndexError, ValueError):
            return

    def get_datetime_of_folder(self):
        return self.current_datetime

    def __str__(self):
        return f"Name: {self.name}\nParent Path: {self.parent_path}\nDestination Path: {self.destination_path}\nFolder Datetime: {self.current_datetime}"


def get_folders_from_path(directory):
    try:
        # List to store folder names
        folders = []

        # Iterate through the items in the given directory
        for item in os.listdir(directory):
            # Create the full path to the item
            item_path = os.path.join(directory, item)
            # Check if the item is a directory
            if os.path.isdir(item_path):
                folders.append(Folder(item, directory))

        return folders

    except Exception as e:
        print(f"An error occurred: {e}")
        return []


def copy_folder_with_datetime(source_folder, destination_folder):
    try:
        # Ensure the source folder exists
        if not os.path.exists(source_folder):
            raise ValueError(f"Source folder '{source_folder}' does not exist.")

        # Copy the folder and its contents
        shutil.copytree(source_folder, destination_folder)
        print(f"Folder '{source_folder}' has been copied to '{destination_folder}'.")

    except Exception as e:
        print(f"An error occurred: {e}")


folders_to_be_backed_up = get_folders_from_path(SOURCE_VMS_FOLDER_PATH)
for folder in folders_to_be_backed_up:
    folder.set_destination_path(DESTINATION_FOLDER_PATH)


for folder in folders_to_be_backed_up:
    folder.set_datetime_to_current_datetime()
    copy_folder_with_datetime(
        folder.generate_source_full_folder_path(),
        folder.generate_destination_full_folder_path(),
    )
