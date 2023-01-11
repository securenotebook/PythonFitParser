import sys, os
import time
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
  
class MonitorFolder(FileSystemEventHandler):
    FILE_SIZE=1000
    
    def on_created(self, event):
         print(event.src_path, event.event_type)
         self.checkFolderSize(event.src_path)
   
    def on_modified(self, event):
        print(event.src_path, event.event_type)
        self.checkFolderSize(event.src_path)
    
    def on_deleted(self, event):
        print(event.src_path, event.event_type)
               
    def checkFolderSize(self,src_path):
        if os.path.isdir(src_path):
            if os.path.getsize(src_path) >self.FILE_SIZE:
                print("Time to backup the dir")
        else:
            if os.path.getsize(src_path) >self.FILE_SIZE:
                print("very big file, needs to be backed up")


if __name__ == "__main__":
    src_path = "/home/pi/PythonFitParser/"
    
    event_handler=MonitorFolder()
    observer = Observer()
    observer.schedule(event_handler, path=src_path, recursive=True)
    print("Monitoring started")
    observer.start()
    try:
        while(True):
           time.sleep(1)
           
    except KeyboardInterrupt:
            observer.stop()
            observer.join()