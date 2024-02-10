##############################
# Created by: João Rodrigues #
# Date: 10/02/2024           #
##############################
import sys
import re
import os
import hashlib
from config import *
from time import sleep


def read_commands() -> dict:
    """
    This function is responsible for reading command line arguments
    and validate them according to business logic.
    Returns a dictionary containing the commands information
    """

    commands = sys.argv
    logger.info(f"Commands read: {commands}.")

    if len(commands) != 5:
        logger.error("The number of arguments provided is invalid.")
        logger.info("Usage: main.py <source> <replica> <sync_interval> <log_file_path>.")
        return None
    
    source = commands[1]
    replica = commands[2]
    sync_interval = commands[3]
    log_file_path = commands[4]
    sync_interval_pattern = r'^\d+[smhdSMHD]$'

    if source == replica:
        logger.error("Source folder path should not be the same as replica folder path.")
        return None
    
    if not re.match(sync_interval_pattern, sync_interval):
        message = (
            "\n"
            "The <sync_interval> argument should be provided in the format <integer number><letter>.\n"
            "<integer number> can be any integer number.\n"
            "<letter> should be s (second), m (minute), h (hour), d (day) not case sensitive.\n"
            "Example: 1d | 1D | 30s | 5m | 12H.")
        logger.error(message)
        return None
    
    if not log_file_path.endswith('.log'):
        logger.error("Invalid logger extension. Use .log extension.")
        return None
    
    return {'source': source, 'replica': replica, 'sync_interval': sync_interval, 'log_file_path': log_file_path}


def calculate_file_hash(filepath: str) -> str:
    """
    This function is responsible for calculating the file hash
    of the specified file as an argument.
    filepath(str): The filepath to calculate the hash
    Returns the file hash as a string
    """

    try:
        with open(filepath, 'rb') as file:
            file_hash = hashlib.md5()
            while chunk := file.read(CHUNK_SIZE):
                file_hash.update(chunk)
            return file_hash.hexdigest()
    except OSError as e:
        logger.error(f"Failed to open file {filepath}. Reason - {e}.")
    except Exception as e:
        logger.error(f"Failed to calculate file hash. Reason {e}.")


def set_logger_file(filepath: str) -> None:
    """
    This function is responsible for setting the logger file.
    filepath(str): The filepath to the logger file
    """

    file_handler = logging.FileHandler(filepath)
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(module)s:%(funcName)s - %(message)s")
    file_handler.setLevel(LOG_LEVEL)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)


def start_sync(sync_interval: str, source: str, replica: str) -> None:
    """
    This function is responsible for starting the periodic folder
    synchronization between the source and replica folders.
    sync_interval(str): The interval in which the sync should occur
    source(str): The source folder name
    replica(str): The replica folder name
    """

    interval = sync_interval[-1]
    value = int(sync_interval[:-1])
    interval_to_seconds = {'s': 1, 'm': 60, 'h': 3600, 'd': 86400}[interval.lower()]
    conversion = {'s': "seconds", 'm': "minutes", 'h': "hours", 'd': "days"}
    logger.info(f"Sync interval set to {value} {conversion[interval]}")
    while True:
        logger.info(f"Synchronizing folders {source} and {replica}.")
        result = synchronize_folders(source, replica)
        if result == False:
            break
        sleep(value * interval_to_seconds)


def delete_item(itempath: str) -> None:
    """
    This function is responsible for recursively deleting the folder
    specified by the argument folderpath.
    folderpath(str) - The folderpath of the folder to be deleted
    """

    if os.path.isfile(itempath):
        try:
            os.remove(itempath)
            logger.info(f"Deleting file {itempath}")
        except OSError as e:
            logger.error(f"Failed to delete {itempath}")
    else:
        for item in os.listdir(itempath):
            new_item_path = os.path.join(itempath, item)
            delete_item(new_item_path)
        try:
            os.rmdir(itempath)
            logger.info(f"Deleting folder {itempath}")
        except OSError as e:
            logger.error(f"Failed to delete folder {itempath}")


def synchronize_folders(source: str, replica: str) -> bool:
    """
    This function is responsible for synchronizing the source and replica folders.
    It is also used recursively to synchronize subfolders
    source(str): The source folder name
    replica(str): The replica folder name
    Returns True or False if the sync is successful or not, respectively
    """

    if not os.path.exists(source):
        logger.error("Source folder does not exist.")
        return False
    
    if not os.path.exists(replica):
        try:
            os.mkdir(replica)
            logger.info(f"Synchronizing folder {replica}")
        except OSError as e:
            logger.error(f"Failed to create replica folder. Reason - {e}.")
            return False
        
    if not os.path.isdir(source):
        logger.error("Source folder path is not a folder.")
        return False
    
    if not os.path.isdir(replica):
        logger.error("Replica folder path is not a folder.")
        return False
    
    for item in os.listdir(source):
        source_item_path = os.path.join(source, item)
        replica_item_path = os.path.join(replica, item)
        
        if os.path.isdir(source_item_path):
            synchronize_folders(source_item_path, replica_item_path)

        else:
            try:
                if os.path.exists(replica_item_path):
                    source_hash = calculate_file_hash(source_item_path)
                    replica_hash = calculate_file_hash(replica_item_path)
                    if source_hash == replica_hash:
                        message = f"Source and replica hash match for file {item}. No need to sync."
                        logger.info(message)
                        continue

                with open(source_item_path, 'rb') as source_file:                        
                    with open(replica_item_path, 'wb') as replica_file:
                        replica_file.write(source_file.read())
                        logger.info(f"Synchronizing file {replica_item_path}.")

            except OSError as e:
                message = (
                    "Failed to synchronize source file "
                    f"{source_item_path} with replica {replica_item_path}. Reason - {e}."

                )
                logger.error(message)
                continue

    for item in os.listdir(replica):
        replica_item_path = os.path.join(replica, item)
        source_item_path = os.path.join(source, item)
        if not os.path.exists(source_item_path):
            delete_item(replica_item_path)

    return True


def main():
    """
    The main program execution
    """

    commands = read_commands()
    if commands == None:
        return
    set_logger_file(commands['log_file_path'])
    start_sync(commands['sync_interval'],commands['source'], commands['replica'])


if __name__ == "__main__":
    main()