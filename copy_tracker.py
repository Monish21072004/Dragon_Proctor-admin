import time
import threading
import logging
import pyperclip

class CopyTracker:
    def __init__(self, poll_interval=1.0, callback=None):
        self.poll_interval = poll_interval
        self.callback = callback
        self.event_log = []
        self.last_clipboard = ""
        self.running = False
        self.logger = logging.getLogger("CopyTracker")
        self.logger.setLevel(logging.DEBUG)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter("[%(levelname)s] %(asctime)s - %(name)s: %(message)s")
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

    def poll_clipboard(self):
        while self.running:
            try:
                text = pyperclip.paste()
            except Exception as e:
                self.logger.error("Error reading clipboard: %s", e)
                text = ""
            if text != self.last_clipboard and text.strip() != "":
                self.last_clipboard = text
                word_count = len(text.split())
                event = {
                    "timestamp": time.time(),
                    "event": "Copy-Paste Detected",
                    "content_preview": text[:50],
                    "word_count": word_count,
                    "full_content": text
                }
                self.event_log.append(event)
                self.logger.info("Copy detected. Word Count: %d, Preview: %s", word_count, text[:50])
                if self.callback:
                    self.callback(event)
            time.sleep(self.poll_interval)

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self.poll_clipboard, daemon=True)
        self.thread.start()
        self.logger.info("CopyTracker started.")

    def stop(self):
        self.running = False
        self.thread.join()
        self.logger.info("CopyTracker stopped.")

if __name__ == "__main__":
    def event_callback(event):
        print("Copy Event:", event)
    tracker = CopyTracker(callback=event_callback)
    tracker.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        tracker.stop()
