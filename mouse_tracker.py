import time, math, logging
from pynput import mouse

class MouseBehaviorTracker:
    def __init__(self, speed_threshold=1500, angle_threshold=90, callback=None):
        self.prev_time = None
        self.prev_pos = None
        self.speed_threshold = speed_threshold
        self.angle_threshold = angle_threshold
        self.prev_direction = None
        self.risk_score = 0
        self.event_log = []
        self.callback = callback
        self.logger = logging.getLogger("MouseBehaviorTracker")
        self.logger.setLevel(logging.DEBUG)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter("[%(levelname)s] %(asctime)s - %(name)s: %(message)s")
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

    def on_move(self, x, y):
        current_time = time.time()
        if self.prev_pos is not None:
            dt = current_time - self.prev_time
            dx = x - self.prev_pos[0]
            dy = y - self.prev_pos[1]
            distance = math.sqrt(dx * dx + dy * dy)
            if dt > 0:
                speed = distance / dt
                if speed > self.speed_threshold:
                    risk = 5
                    self.risk_score += risk
                    event = {"timestamp": current_time, "event": "High speed", "speed": speed, "risk": risk, "position": (x, y)}
                    self.event_log.append(event)
                    self.logger.warning("High speed: %.2f px/sec, risk added: %d, total risk: %d", speed, risk, self.risk_score)
                    if self.callback:
                        self.callback(event)
            current_direction = math.degrees(math.atan2(dy, dx)) if distance > 0 else None
            if self.prev_direction is not None and current_direction is not None:
                angle_diff = abs(current_direction - self.prev_direction)
                if angle_diff > 180:
                    angle_diff = 360 - angle_diff
                if angle_diff > self.angle_threshold:
                    risk = 3
                    self.risk_score += risk
                    event = {"timestamp": current_time, "event": "Abrupt direction change", "angle_diff": angle_diff, "risk": risk, "position": (x, y)}
                    self.event_log.append(event)
                    self.logger.warning("Abrupt direction change: %.2f°, risk added: %d, total risk: %d", angle_diff, risk, self.risk_score)
                    if self.callback:
                        self.callback(event)
            if current_direction is not None:
                self.prev_direction = current_direction
        self.prev_time = current_time
        self.prev_pos = (x, y)

    def start(self):
        self.listener = mouse.Listener(on_move=self.on_move)
        self.listener.start()
        self.logger.info("MouseBehaviorTracker started.")

    def stop(self):
        self.listener.stop()
        self.logger.info("MouseBehaviorTracker stopped.")

if __name__ == "__main__":
    def event_callback(event):
        print(event)
    tracker = MouseBehaviorTracker(callback=event_callback)
    tracker.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        tracker.stop()
