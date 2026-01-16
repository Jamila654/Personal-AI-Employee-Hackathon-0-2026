import os
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Define the folders to monitor and store new files
# This line finds exactly where THIS script is saved
base_path = os.path.dirname(os.path.abspath(__file__))

# Now we join that path to your folders
INBOX_FOLDER = os.path.join(base_path, "inbox")
NEEDS_ACTION_FOLDER = os.path.join(base_path, "Needs_Action")

# Ensure the directories exist
os.makedirs(INBOX_FOLDER, exist_ok=True)
os.makedirs(NEEDS_ACTION_FOLDER, exist_ok=True)

class NewFileHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory:
            file_name = os.path.basename(event.src_path)
            print(f"New file detected: {file_name}")

            base_name = os.path.splitext(file_name)[0]          # removes last .extension
            markdown_file_path = os.path.join(NEEDS_ACTION_FOLDER, f"{base_name}.md")
            with open(markdown_file_path, "w") as f:
                f.write("New file detected! Please process this.")
            print(f"Created markdown file: {markdown_file_path}")

if __name__ == "__main__":
    event_handler = NewFileHandler()
    observer = Observer()
    observer.schedule(event_handler, INBOX_FOLDER, recursive=False)
    observer.start()
    print(f"Monitoring {INBOX_FOLDER} for new files...")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
