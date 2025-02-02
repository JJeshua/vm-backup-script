import os
import shutil
from datetime import datetime, timedelta
import subprocess
from time import sleep


SOURCE_VMS_FOLDER_PATH = r"C:\Users\admin\Desktop\Start"
DESTINATION_FOLDER_PATH = r"C:\Users\admin\Desktop\Destination"
SEVEN_ZIP_PATH = r"C:\Program Files\7-Zip\7z.exe"
YOUNGEST_AGE_THRESHOLD = 7
OLDEST_AGE_THRESHOLD = 30


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
        return f"{self.destination_path}\\{self.name}_{self.export_folder_datetime_to_string()}"

    def generate_source_full_folder_path(self):
        if not self.name:
            raise ValueError("Folder name or datetime is null")
        return f"{self.parent_path}\\{self.name}"

    def generate_archive_folder_name(self):
        return f"{self.name}_{self.export_folder_datetime_to_string()}.7z"

    def generate_archive_full_path(self):
        return f"{self.parent_path}\\{self.generate_archive_folder_name()}"

    def is_older_than_old_age_threshold(self):
        current_datetime = datetime.now()
        return (current_datetime - self.current_datetime) > timedelta(days=30)

    def is_younger_than_young_age_threshold(self):
        current_datetime = datetime.now()
        return (current_datetime - self.current_datetime) < timedelta(days=7)

    def calculate_age_in_days_hours_and_seconds(self):
        # Parse the input date string to a datetime object
        input_date = self.current_datetime
        if not input_date:
            raise RuntimeError(f"\n(ERROR) {self} does not have a datetime")

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
        self.current_datetime = current_datetime

    def export_folder_datetime_to_string(self):
        return self.current_datetime.strftime("%Y%m%d%H%M%S")

    def set_destination_path(self, path):
        self.destination_path = path

    def parse_folder_name_and_datetime(self):
        # Check if the name ends with .7z
        if "_" not in self.name:
            return
        elif self.name.endswith(".7z"):
            # Remove the .7z extension
            base_name_with_datetime = self.name[:-3]
        else:
            base_name_with_datetime = self.name

        # Split the folder name by the last underscore
        base_name, datetime_str = base_name_with_datetime.rsplit("_", 1)

        # Convert the datetime string to a datetime object
        folder_datetime = datetime.strptime(datetime_str, "%Y%m%d%H%M%S")

        # Update the name and datetime attributes
        self.name = base_name
        self.current_datetime = folder_datetime

    def get_datetime_of_folder(self):
        return self.current_datetime

    def __str__(self):
        return f"Name: {self.name}\nParent Path: {self.parent_path}\nDestination Path: {self.destination_path}\nFolder Datetime: {self.current_datetime}\n"


def get_folders_from_path(directory):
    # List to store folder names
    folders = []

    # Iterate through the items in the given directory
    for item in os.listdir(directory):
        # Create the full path to the item
        item_path = os.path.join(directory, item)
        # Check if the item is a directory
        if os.path.isdir(item_path) or item.lower().endswith("7z"):
            folders.append(Folder(item, directory))

    return folders


def validate_folder(source_folder: Folder):
    source_folder_full_path = source_folder.generate_source_full_folder_path()
    if source_folder.parent_path != SOURCE_VMS_FOLDER_PATH:
        raise RuntimeError(
            f"Attempted to archive folder {source_folder_full_path} not in {SOURCE_VMS_FOLDER_PATH}"
        )
    if not os.path.exists(source_folder_full_path):
        raise ValueError(f"Source folder '{source_folder_full_path}' does not exist.")
    return source_folder_full_path


def start_archive_process(seven_zip_path, source_folder: Folder):
    process = subprocess.Popen(
        [
            seven_zip_path,
            "a",
            source_folder.generate_destination_full_folder_path(),
            source_folder.generate_source_full_folder_path(),
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    print(
        f"Started archiving {source_folder.name} as {source_folder.generate_archive_folder_name()}"
    )
    return process


def monitor_archive_process(process, source_folder: Folder):
    while process.poll() is None:
        print("Archiving in progress...")
        sleep(5)  # Wait for 5 seconds before checking again
    stdout, stderr = process.communicate()
    if process.returncode == 0:
        print(
            f"Successfully archived {source_folder.name} as {source_folder.generate_archive_folder_name()}"
        )
    else:
        print(f"Error archiving {source_folder.name}: {stderr.decode('utf-8')}")


def backup_folder(source_folder: Folder):
    validate_folder(source_folder)
    process = start_archive_process(SEVEN_ZIP_PATH, source_folder)
    monitor_archive_process(process, source_folder)


def delete_archive(folder: Folder):
    """
    Delete a .7z archive given the full path to the archive.

    Parameters:
    file_path (str): The full path to the .7z archive.
    """
    archive_folder_name = folder.generate_archive_folder_name()
    archive_path = folder.generate_archive_full_path()
    if not os.path.exists(archive_path) or not archive_folder_name.endswith(".7z"):
        print(f"File {archive_path} does not exist or is not a .7z archive")

    try:
        os.remove(archive_path)
        print(f"Deletion initiated for: {archive_path}")

        while os.path.exists(archive_path):
            sleep(5)

        print(f"Successfully deleted: {archive_path}")
    except Exception as e:
        print(f"Error deleting file: {archive_path}\n{e}")


def main():
    skip = []

    # check the age of already backed up folders
    # folder will be backed up if it is not too young
    current_backed_up_folders = get_folders_from_path(DESTINATION_FOLDER_PATH)
    for folder in current_backed_up_folders:
        days, hours, minutes, seconds = folder.calculate_age_in_days_hours_and_seconds()

        # add the folder to the skip list if it is younger than the minimum age threshold
        if folder.is_younger_than_young_age_threshold():
            print(
                f"Skipping [{folder.name}] \t\t Already backed up {days}days {hours}hrs {minutes}mins {seconds}secs ago."
            )
            skip.append(folder.name)

        # delete the folder if it is older than oldest age threshold
        elif folder.is_older_than_old_age_threshold():
            delete_archive(folder)

    # backup each of the folders in the source directory.
    # skip the folder if it is in the skip list.
    # we first archive the folder with 7 zip.
    folders_to_be_backed_up = get_folders_from_path(SOURCE_VMS_FOLDER_PATH)
    for folder in folders_to_be_backed_up:
        folder.set_destination_path(DESTINATION_FOLDER_PATH)

        if folder.name in skip:
            continue

        folder.set_datetime_to_current_datetime()
        backup_folder(folder)


if __name__ == "__main__":
    main()
