import os
import shutil
from datetime import datetime, timedelta
import subprocess
from time import sleep


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

    def generate_archive_folder_name(self):
        return f"{self.name}_{self.current_datetime}.7z"

    def is_older_than_30_days(self):
        current_datetime = datetime.now()
        return (current_datetime - self.current_datetime) > timedelta(days=30)

    def is_younger_than_7_days(self):
        current_datetime = datetime.now()
        return (current_datetime - self.current_datetime) < timedelta(days=7)

    def calculate_age_in_days_hours_and_seconds(self):
        # Parse the input date string to a datetime object
        input_date = self.current_datetime

        # Get the current date and time
        current_datetime = datetime.now()

        # Calculate the difference
        difference = current_datetime - input_date
        total_seconds = difference.total_seconds()

        # Calculate days, hours, and seconds
        days = int(total_seconds // (24 * 3600))
        remaining_seconds = total_seconds % (24 * 3600)
        hours = int(remaining_seconds // 3600)
        remaining_seconds %= 3600
        minutes = int(remaining_seconds // 60)
        seconds = int(remaining_seconds % 60)

        return days, hours, minutes, seconds

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
            self.current_datetime = folder_datetime

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


def archive_folder(source_folder: Folder):

    seven_zip_path = r"C:\Program Files\7-Zip\7z.exe"

    # attempting to archive a folder that is not in the specified source path
    if source_folder.parent_path != SOURCE_VMS_FOLDER_PATH:
        raise RuntimeError(
            f"(ERROR) Attempted to archive folder {source_folder.generate_source_full_folder_path()} not in {SOURCE_VMS_FOLDER_PATH}"
        )

    # Ensure the source folder exists
    source_folder_full_path = source_folder.generate_source_full_folder_path()
    print(source_folder_full_path)
    if not os.path.exists(source_folder_full_path):
        raise ValueError(f"Source folder '{source_folder_full_path}' does not exist.")

    # Start the 7-Zip process in the background
    process = subprocess.Popen(
        [
            seven_zip_path,
            "a",
            source_folder.generate_archive_folder_name(),
            source_folder_full_path,
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    print(
        f"Started archiving {source_folder.name} as {source_folder.generate_archive_folder_name()}"
    )

    # Monitor the process
    while process.poll() is None:
        print("Archiving in progress...")
        sleep(5)  # Wait for 5 seconds before checking again

    # Check for errors
    stdout, stderr = process.communicate()
    if process.returncode == 0:
        print(
            f"Successfully archived {source_folder.name} as {source_folder.generate_archive_folder_name()}"
        )
    else:
        print(f"Error archiving {source_folder.name}: {stderr.decode('utf-8')}")

    # # Copy the folder and its contents
    # shutil.copytree(source_folder, destination_folder)
    # print(
    #     f"(COPY) Folder [{source_folder}] has been copied to [{destination_folder}]."
    # )


skip = []

# check the age of already backed up folders.
# skip if they are young.
current_backed_up_folders = get_folders_from_path(DESTINATION_FOLDER_PATH)
for folder in current_backed_up_folders:
    days, hours, minutes, seconds = folder.calculate_age_in_days_hours_and_seconds()
    if folder.is_younger_than_7_days():
        print(
            f"(SKIPPING) [{folder.name}] \t Already backed up {days}days {hours}hrs {minutes}mins {seconds}secs ago."
        )
        skip.append(folder.name)


folders_to_be_backed_up = get_folders_from_path(SOURCE_VMS_FOLDER_PATH)
for folder in folders_to_be_backed_up:
    folder.set_destination_path(DESTINATION_FOLDER_PATH)


for folder in folders_to_be_backed_up:
    if folder.name in skip:
        continue

    folder.set_datetime_to_current_datetime()
    archive_folder(folder)
