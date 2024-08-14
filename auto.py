from os import scandir, rename
from os.path import splitext, exists, join
from shutil import move
from time import sleep
import logging
import os
import time

from watchdog.observers import Observer 
from watchdog.events import FileSystemEventHandler 

# ? supported Image types
image_extensions = [".jpg", ".jpeg", ".jpe", ".jif", ".jfif", ".jfi", ".png", ".gif", ".webp", ".tiff", ".tif", ".psd", ".raw", ".arw", ".cr2", ".nrw",
                    ".k25", ".bmp", ".dib", ".heif", ".heic", ".ind", ".indd", ".indt", ".jp2", ".j2k", ".jpf", ".jpf", ".jpx", ".jpm", ".mj2", ".svg", ".svgz", ".ai", ".eps", ".ico"]
# ? supported Video types
video_extensions = [".webm", ".mpg", ".mp2", ".mpeg", ".mpe", ".mpv", ".ogg",
                    ".mp4", ".mp4v", ".m4v", ".avi", ".wmv", ".mov", ".qt", ".flv", ".swf", ".avchd"]
# ? supported Audio types
audio_extensions = [".m4a", ".flac", "mp3", ".wav", ".wma", ".aac"]
# ? supported Document types
document_extensions = [".doc", ".docx", ".odt",".pdf", ".xls", ".xlsx", ".ppt", ".pptx"]

# Source and Paths
#Source is where it checks for new files
source_dir =r"PATH TO THE SOURCE"
dest_dir_sfx = r"PATH TO SOUND FOLDER" 
dest_dir_musik = r"PATH TO MUSIC FOLDER"
dest_dir_video = r"PATH TO VIDEO FOLDER"
dest_dir_docs = r"PATH TO DOCS FOLDER"
dest_dir_picture = r"PATH TO PICTURE FOLDER"

#Checks if source directory exists
if not os.path.exists(source_dir):
    raise FileNotFoundError(f"The source directory {source_dir} does not exist.")

#Make filename unique
def make_unique(dest, name):
    filename, extension = splitext(name)
    counter = 1
    #If filename already exists, add a number in parentheses to the base name
    while exists(f"{dest}/{name}"):
        name = f"{filename}({str(counter)}){extension}"
        counter += 1

    return name

#Move file to destination directory
def move_file(dest, entry, name):
    #Check if filename already exists in destination directory
    if exists(f"{dest}/{name}"):
        #if filename already exists, make it unique with make_unique function
        unique_name = make_unique(dest, name)
        #Renames the file
        oldName = join(dest, name)
        newName = join(dest, unique_name)
        rename(oldName, newName)
    #Moves the file to the destination directory
    move(entry, dest)


class MoverHandler(FileSystemEventHandler):
    def on_created(self, event):
        # Log the creation of a new file
        print("File created:", event.src_path)
        # Wait for 1 second to ensure the file is fully written
        time.sleep(1)
        # Scan the source directory for new files
        with scandir(source_dir) as entries:
            for entry in entries:
                name = entry.name
                # Check and move files based on their types
                self.check_audio_files(entry, name)
                self.check_video_files(entry, name)
                self.check_image_files(entry, name)
                self.check_doc_files(entry, name)

    def check_audio_files(self, entry, name):
        # Check if the file is an audio file
        for audio_extension in audio_extensions:
            if name.endswith(audio_extension) or name.endswith(audio_extension.upper()):
                # Determine the destination based on file size or name
                if entry.stat().st_size < 10_000_000 or "SFX" in name:
                    dest = dest_dir_sfx
                else:
                    dest = dest_dir_musik
                # Move the file to the appropriate destination
                move_file(dest, entry, name)
                logging.info(f"Moved audio file: {name}")
                return  # Exit the function after moving the file

    def check_video_files(self, entry, name):
        # Check if the file is a video file
        for video_extension in video_extensions:
            if name.endswith(video_extension) or name.endswith(video_extension.upper()):
                dest = dest_dir_video
                # Move the file to the video destination
                move_file(dest, entry, name)
                logging.info(f"Moved video file: {name}")
                return  # Exit the function after moving the file

    def check_image_files(self, entry, name):
        # Check if the file is an image file
        for image_extension in image_extensions:
            if name.endswith(image_extension) or name.endswith(image_extension.upper()):
                dest = dest_dir_picture
                # Move the file to the image destination
                move_file(dest, entry, name)
                logging.info(f"Moved image file: {name}")
                return  # Exit the function after moving the file

    def check_doc_files(self, entry, name):
        # Check if the file is a document file
        for documents_extension in document_extensions:
            if name.endswith(documents_extension) or name.endswith(documents_extension.upper()):
                dest = dest_dir_docs
                # Move the file to the document destination
                move_file(dest, entry, name)
                logging.info(f"Moved document file: {name}")
                return  # Exit the function after moving the file


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    path = source_dir
    event_handler = MoverHandler()
    observer = Observer()
    try:
        # Set up and start the observer
        observer.schedule(event_handler, path, recursive=True)
        logging.info(f"Starting observer for {path}")
        observer.start()
        logging.info("Observer started successfully")
        # Keep the script running
        while True:
            sleep(10)
    except Exception as e:
        # Log any errors that occur
        logging.error(f"Error occurred: {e}")
    finally:
        # Ensure the observer is stopped when the script exits
        logging.info("Stopping observer")
        observer.stop()
        observer.join()
