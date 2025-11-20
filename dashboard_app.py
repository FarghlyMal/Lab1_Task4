#!/usr/bin/env python3
"""
Task 3: Web Dashboard for DDoS Detection System
Flask backend that provides real-time monitoring interface
"""

from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import json
import os
from datetime import datetime
import threading
import time
from collections import deque

app = Flask(__name__)
CORS(app)

# Store recent detections in memory
recent_detections = deque(maxlen=100)
stats = {
    'total_packets': 0,
    'malicious_flows': 0,
    'blocked_ips': 0,
    'start_time': datetime.now().isoformat()
}

# Thread-safe lock
data_lock = threading.Lock()

class DetectionMonitor:
    """Monitor detection log file for updates"""
    
    def __init__(self, log_file='detection_log.json'):
        self.log_file = log_file
        self.last_position = 0
        self.running = True
        
    def start(self):
        """Start monitoring in background thread"""
        thread = threading.Thread(target=self.monitor_loop)
        thread.daemon = True
        thread.start()
        
    def monitor_loop(self):
        """Continuously monitor log file"""
        while self.running:
            self.check_updates()
            time.sleep(2)  # Check every 2 seconds
            
    def check_updates(self):
        """Check for new entries in log file"""
        if not os.path.exists(self.log_file):
            # Try to find the latest log file
            log_files = [f for f in os.listdir('.') if f.startswith('detection_log_')]
            if log_files:
                self.log_file = max(log_files)  # Get most recent
            else:
                return
        
        try:
            with open(self.log_file, 'r') as f:
                data = json.load(f)
                
            with data_lock:
                for entry in data:
                    if entry not in recent_detections:
                        recent_detections.append(entry)
                        stats['malicious_flows'] = len(recent_detections)
                        
        except (json.JSONDecodeError, FileNotFoundError):
            pass

# Initialize monitor
monitor = DetectionMonitor()
monitor.start()

@app.route('/')
def index():
    """Serve main dashboard page"""
    return render_template('dashboard.html')

@app.route('/api/detections')
def get_detections():
    """API endpoint for detection data"""
    with data_lock:
        return jsonify({
            'detections': list(recent_detections),
            'count': len(recent_detections)
        })

@app.route('/api/stats')
def get_stats():
    """API endpoint for statistics"""
    with data_lock:
        # Count unique blocked IPs
        unique_ips = set(d['src_ip'] for d in recent_detections)
        stats['blocked_ips'] = len(unique_ips)
        
        return jsonify(stats)

@app.route('/api/add_detection', methods=['POST'])
def add_detection():
    """API endpoint to manually add detection (for testing)"""
    data = request.json
    
    with data_lock:
        recent_detections.append(data)
        stats['malicious_flows'] += 1
        
    return jsonify({'success': True})

@app.route('/api/clear')
def clear_data():
    """Clear all detection data"""
    with data_lock:
        recent_detections.clear()
        stats['malicious_flows'] = 0
        stats['blocked_ips'] = 0
        
    return jsonify({'success': True})

if __name__ == '__main__':
    print("="*60)
    print("DDoS Detection Dashboard")
    print("="*60)
    print("Starting Flask server on http://localhost:5000")
    print("Open this URL in your web browser")
    print("="*60)
    
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)
