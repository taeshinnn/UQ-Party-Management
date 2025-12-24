import time
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from typing import Callable, Optional
from queue_manager import QueueManager


class LogFileWatcher(FileSystemEventHandler):
    def __init__(self, log_file_path: str, queue_manager: QueueManager, callback: Callable):
        self.log_file_path = os.path.abspath(log_file_path)
        self.queue_manager = queue_manager
        self.callback = callback
        self.last_position = 0
        
        if os.path.exists(self.log_file_path):
            with open(self.log_file_path, 'r', encoding='utf-8') as f:
                f.seek(0, os.SEEK_END)
                self.last_position = f.tell()
    
    def on_modified(self, event):
        if os.path.abspath(event.src_path) != self.log_file_path:
            return
        
        self.read_new_lines()
    
    def read_new_lines(self):
        try:
            with open(self.log_file_path, 'r', encoding='utf-8') as f:
                f.seek(self.last_position)
                new_lines = f.readlines()
                self.last_position = f.tell()
                
                for line in new_lines:
                    line = line.strip()
                    if not line:
                        continue
                    
                    parsed = QueueManager.parse_log_line(line)
                    if parsed:
                        timestamp, player_name, count, names = parsed
                        
                        result = self.queue_manager.add_multiple_players(names, source="log")
                        
                        self.callback({
                            "type": "player_joined",
                            "data": result,
                            "log_line": line
                        })
        except Exception as e:
            print(f"Error reading log file: {e}")


class FileWatcher:
    def __init__(self, log_file_path: str, queue_manager: QueueManager, callback: Callable):
        self.log_file_path = log_file_path
        self.queue_manager = queue_manager
        self.callback = callback
        self.observer: Optional[Observer] = None
        self.event_handler: Optional[LogFileWatcher] = None
    
    def start(self):
        log_dir = os.path.dirname(os.path.abspath(self.log_file_path))
        
        if not os.path.exists(log_dir):
            print(f"Warning: Directory {log_dir} does not exist")
            return False
        
        self.event_handler = LogFileWatcher(self.log_file_path, self.queue_manager, self.callback)
        self.observer = Observer()
        self.observer.schedule(self.event_handler, log_dir, recursive=False)
        self.observer.start()
        
        print(f"📂 Monitoring: {self.log_file_path}")
        return True
    
    def stop(self):
        if self.observer:
            self.observer.stop()
            self.observer.join()
            print("File watcher stopped")
    
    def read_existing_log(self):
        if not os.path.exists(self.log_file_path):
            print(f"Log file not found: {self.log_file_path}")
            return
        
        print("Reading existing log entries...")
        try:
            with open(self.log_file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
                for line in lines:
                    line = line.strip()
                    if not line:
                        continue
                    
                    parsed = QueueManager.parse_log_line(line)
                    if parsed:
                        timestamp, player_name, count, names = parsed
                        self.queue_manager.add_multiple_players(names, source="log")
                
                if self.event_handler:
                    self.event_handler.last_position = f.tell()
                
                print(f"Loaded {len(lines)} lines from log")
        except Exception as e:
            print(f"Error reading existing log: {e}")

