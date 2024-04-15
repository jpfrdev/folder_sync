# Folder Sync Program
The project consists of a program, written in Python, that synchronizes two folders: **source** and **replica**. The program should maintain a full and identical copy of the source folder at the replica folder. To accomplish this, the following criteria should be considered:

1. The content of the replica folder should be modified to match exactly the content of the source folder.
2. The synchronization should be performed periodically.
3. The file creation, copying and removal operations should be logged to a file and to the console output.
4. The folder paths, synchronization interval and log file path should be provided using command line arguments.
5. No third-party libraries that implement folder synchronization should be used.
6. It is allowed to use external libraries that implement well known algorithms like calculating MD5.

## Example Test
Run `python3 main.py source replica 30s log.log` to test the program. It will create a folder called 'replica' if it's not created and a file called log.log containing the program logs. Every 30 seconds the replica folder will synchronize its content with the source folder, so in that time try to create or delete folders and files in the replica folder.
