import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class FileHandler(FileSystemEventHandler):
    def __init__(self, directory, suffix, document_handler):
        self.directory = directory
        self.suffix = suffix
        self.document_handler = document_handler

    def on_created(self, event):
        if event.is_directory:
            return
        elif event.src_path.endswith(self.suffix):
            print(f"文件生成: {event.src_path}")
            self.document_handler(self.directory)

class FileWatcher(FileHandler):
    def __init__(self, directory, suffix, document_handler):
        FileHandler.__init__(self, directory, suffix, document_handler)
        event_handler = FileHandler(self.directory, self.suffix, self.document_handler)
        observer = Observer()
        observer.schedule(event_handler, path=directory, recursive=False)
        observer.start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
