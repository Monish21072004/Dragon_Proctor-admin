from flask import Flask, render_template, jsonify, Response, request
import threading
from io import StringIO
import csv
import time
from mouse_tracker import MouseBehaviorTracker
from window_tracker import WindowTracker
from copy_tracker import CopyTracker

app = Flask(__name__)

def mouse_event_callback(event):
    print("Mouse Event:", event)

def window_event_callback(event):
    print("Window Event:", event)

def copy_event_callback(event):
    print("Copy Event (Python Tracker):", event)

# Initialize trackers
mouse_tracker = MouseBehaviorTracker(speed_threshold=1500, angle_threshold=90, callback=mouse_event_callback)
window_tracker = WindowTracker(poll_interval=0.5, callback=window_event_callback)
copy_tracker = CopyTracker(callback=copy_event_callback)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/copy_test')
def copy_test():
    return render_template('copy_test.html')

@app.route('/api/mouse_events')
def mouse_events():
    return jsonify(mouse_tracker.event_log)

@app.route('/api/window_events')
def window_events():
    return jsonify(window_tracker.event_log)

@app.route('/api/copy_events')
def copy_events():
    return jsonify(copy_tracker.event_log)

@app.route('/api/risk')
def risk():
    return jsonify({"risk_score": mouse_tracker.risk_score})

# New endpoint to register client-side copy events
@app.route('/api/register_copy', methods=['POST'])
def register_copy():
    data = request.json
    if data and 'content' in data:
         content = data['content']
         word_count = len(content.split())
         event = {
             "timestamp": time.time(),
             "event": "Copy-Paste (Client)",
             "content_preview": content[:50],
             "word_count": word_count,
             "full_content": content
         }
         copy_tracker.event_log.append(event)
         print("Registered client copy event:", event)
         return jsonify({"status": "success"}), 200
    return jsonify({"status": "error"}), 400

@app.route('/download/mouse_csv')
def download_mouse_csv():
    si = StringIO()
    cw = csv.writer(si)
    cw.writerow(['timestamp', 'event', 'speed', 'angle_diff', 'risk', 'position'])
    for event in mouse_tracker.event_log:
        cw.writerow([
            event.get('timestamp', ''),
            event.get('event', ''),
            event.get('speed', ''),
            event.get('angle_diff', ''),
            event.get('risk', ''),
            event.get('position', '')
        ])
    output = si.getvalue()
    return Response(output, mimetype="text/csv", headers={"Content-Disposition": "attachment;filename=mouse_events.csv"})

@app.route('/download/window_csv')
def download_window_csv():
    si = StringIO()
    cw = csv.writer(si)
    cw.writerow(['timestamp', 'window', 'duration'])
    for event in window_tracker.event_log:
        cw.writerow([
            event.get('timestamp', ''),
            event.get('window', ''),
            event.get('duration', '')
        ])
    output = si.getvalue()
    return Response(output, mimetype="text/csv", headers={"Content-Disposition": "attachment;filename=window_events.csv"})

@app.route('/download/copy_csv')
def download_copy_csv():
    si = StringIO()
    cw = csv.writer(si)
    cw.writerow(['timestamp', 'event', 'content_preview', 'word_count', 'full_content'])
    for event in copy_tracker.event_log:
        cw.writerow([
            event.get('timestamp', ''),
            event.get('event', ''),
            event.get('content_preview', ''),
            event.get('word_count', ''),
            event.get('full_content', '')
        ])
    output = si.getvalue()
    return Response(output, mimetype="text/csv", headers={"Content-Disposition": "attachment;filename=copy_events.csv"})

if __name__ == '__main__':
    threading.Thread(target=mouse_tracker.start, daemon=True).start()
    threading.Thread(target=window_tracker.start, daemon=True).start()
    threading.Thread(target=copy_tracker.start, daemon=True).start()
    app.run(debug=True)
