import time, threading, logging
import win32gui

class WindowTracker:
    def __init__(self, poll_interval=0.5, callback=None):
        self.poll_interval = poll_interval
        self.callback = callback
        self.current_window = None
        self.current_start_time = None
        self.event_log = []
        self.running = False
        self.logger = logging.getLogger("WindowTracker")
        self.logger.setLevel(logging.DEBUG)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter("[%(levelname)s] %(asctime)s - %(name)s: %(message)s")
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

    def get_active_window(self):
        hwnd = win32gui.GetForegroundWindow()
        return win32gui.GetWindowText(hwnd)

    def _poll(self):
        while self.running:
            window_title = self.get_active_window()
            if window_title != self.current_window:
                now = time.time()
                if self.current_window is not None:
                    duration = now - self.current_start_time
                    event = {
                        "timestamp": self.current_start_time,
                        "window": self.current_window,
                        "duration": duration
                    }
                    self.event_log.append(event)
                    self.logger.info("Window changed: '%s' was active for %.2f seconds", self.current_window, duration)
                    if self.callback:
                        self.callback(event)
                self.current_window = window_title
                self.current_start_time = now
            time.sleep(self.poll_interval)

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._poll, daemon=True)
        self.thread.start()
        self.logger.info("WindowTracker started.")

    def stop(self):
        self.running = False
        self.thread.join()
        self.logger.info("WindowTracker stopped.")
