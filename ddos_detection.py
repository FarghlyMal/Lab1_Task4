#!/usr/bin/env python3
"""
Task 2: Real-time DDoS Detection and Mitigation System
This implements: Packet Capture → Flowmeter → Classifier → Filtration
"""

import sys
import os
import time
import signal
import threading
import subprocess
from scapy.all import sniff, IP, TCP, UDP, ICMP
from collections import defaultdict
import pickle
import numpy as np
from datetime import datetime
import json

# Global variables
running = True
flow_stats = defaultdict(lambda: {
    'packet_count': 0,
    'byte_count': 0,
    'start_time': None,
    'last_seen': None,
    'protocol': None,
    'flags': set()
})

malicious_ips = set()
blocked_ips = set()

class FlowMeter:
    """Extract flow features from packets"""
    
    def __init__(self, timeout=60):
        self.timeout = timeout
        self.flows = flow_stats
        
    def extract_features(self, flow_key, flow_data):
        """Extract features for ML classification"""
        duration = (flow_data['last_seen'] - flow_data['start_time']).total_seconds()
        if duration == 0:
            duration = 0.001
            
        features = {
            'duration': duration,
            'packet_count': flow_data['packet_count'],
            'byte_count': flow_data['byte_count'],
            'packets_per_second': flow_data['packet_count'] / duration,
            'bytes_per_second': flow_data['byte_count'] / duration,
            'avg_packet_size': flow_data['byte_count'] / flow_data['packet_count'],
            'protocol': flow_data['protocol']
        }
        return features
    
    def update_flow(self, packet):
        """Update flow statistics"""
        if not packet.haslayer(IP):
            return None
            
        ip_layer = packet[IP]
        src_ip = ip_layer.src
        dst_ip = ip_layer.dst
        
        # Create flow key
        if packet.haslayer(TCP):
            protocol = 6
            sport = packet[TCP].sport
            dport = packet[TCP].dport
            flags = packet[TCP].flags
        elif packet.haslayer(UDP):
            protocol = 17
            sport = packet[UDP].sport
            dport = packet[UDP].dport
            flags = None
        else:
            protocol = ip_layer.proto
            sport = 0
            dport = 0
            flags = None
            
        flow_key = (src_ip, dst_ip, sport, dport, protocol)
        
        # Update flow stats
        now = datetime.now()
        if self.flows[flow_key]['start_time'] is None:
            self.flows[flow_key]['start_time'] = now
            
        self.flows[flow_key]['last_seen'] = now
        self.flows[flow_key]['packet_count'] += 1
        self.flows[flow_key]['byte_count'] += len(packet)
        self.flows[flow_key]['protocol'] = protocol
        
        if flags:
            self.flows[flow_key]['flags'].add(str(flags))
            
        return flow_key
    
    def cleanup_old_flows(self):
        """Remove old flows"""
        now = datetime.now()
        to_remove = []
        for flow_key, flow_data in self.flows.items():
            if flow_data['last_seen']:
                age = (now - flow_data['last_seen']).total_seconds()
                if age > self.timeout:
                    to_remove.append(flow_key)
        
        for key in to_remove:
            del self.flows[key]

class DDoSClassifier:
    """Machine Learning classifier for DDoS detection"""
    
    def __init__(self, model_path=None):
        self.model = None
        self.threshold = 0.5
        
        # Try to load pre-trained model from Lab 2/3
        if model_path and os.path.exists(model_path):
            try:
                with open(model_path, 'rb') as f:
                    self.model = pickle.load(f)
                print(f"✓ Loaded model from {model_path}")
            except Exception as e:
                print(f"⚠ Could not load model: {e}")
                self.model = None
        
    def predict(self, features):
        """Predict if traffic is malicious"""
        # If no model is loaded, use heuristic rules
        if self.model is None:
            return self.heuristic_detection(features)
        
        # Prepare features for model
        try:
            feature_vector = self._prepare_features(features)
            prediction = self.model.predict([feature_vector])[0]
            return prediction == 1  # Assuming 1 = malicious
        except Exception as e:
            print(f"⚠ Prediction error: {e}")
            return self.heuristic_detection(features)
    
    def heuristic_detection(self, features):
        """Simple rule-based detection when ML model unavailable"""
        # High packet rate
        if features['packets_per_second'] > 1000:
            return True
            
        # Very small packets (potential SYN flood)
        if features['avg_packet_size'] < 60 and features['packets_per_second'] > 100:
            return True
            
        # High bandwidth usage
        if features['bytes_per_second'] > 10_000_000:  # 10 MB/s
            return True
            
        return False
    
    def _prepare_features(self, features):
        """Convert features dict to numpy array"""
        # Feature order should match your trained model
        return np.array([
            features['duration'],
            features['packet_count'],
            features['byte_count'],
            features['packets_per_second'],
            features['bytes_per_second'],
            features['avg_packet_size'],
            features['protocol']
        ])

class XDPFilter:
    """Interface to XDP filtering (kernel-level)"""
    
    def __init__(self, interface='eth0'):
        self.interface = interface
        self.enabled = False
        self.check_xdp_availability()
        
    def check_xdp_availability(self):
        """Check if XDP is available"""
        try:
            result = subprocess.run(['which', 'xdp-filter'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print("✓ xdp-filter available")
                return True
            else:
                print("⚠ xdp-filter not found, using iptables fallback")
                return False
        except Exception as e:
            print(f"⚠ Error checking XDP: {e}")
            return False
    
    def load(self):
        """Load XDP program"""
        try:
            cmd = ['xdp-filter', 'load', self.interface]
            result = subprocess.run(cmd, capture_output=True, text=True, 
                                  check=True, timeout=5)
            self.enabled = True
            print(f"✓ XDP filter loaded on {self.interface}")
            return True
        except subprocess.TimeoutExpired:
            print("⚠ XDP load timeout - may not be supported on WSL")
            return False
        except subprocess.CalledProcessError as e:
            print(f"⚠ Could not load XDP: {e.stderr}")
            return False
        except Exception as e:
            print(f"⚠ XDP load error: {e}")
            return False
    
    def block_ip(self, ip_address):
        """Block an IP address"""
        if ip_address in blocked_ips:
            return True
            
        # Try XDP first
        if self.enabled:
            try:
                cmd = ['xdp-filter', 'ip', self.interface, 
                       '-m', 'src', '-a', 'deny', ip_address]
                subprocess.run(cmd, capture_output=True, text=True, 
                             check=True, timeout=5)
                blocked_ips.add(ip_address)
                print(f"✓ Blocked {ip_address} via XDP")
                return True
            except Exception as e:
                print(f"⚠ XDP block failed: {e}")
        
        # Fallback to iptables
        return self.block_ip_iptables(ip_address)
    
    def block_ip_iptables(self, ip_address):
        """Fallback: Block IP using iptables"""
        try:
            cmd = ['iptables', '-A', 'INPUT', '-s', ip_address, '-j', 'DROP']
            subprocess.run(cmd, check=True, timeout=5)
            blocked_ips.add(ip_address)
            print(f"✓ Blocked {ip_address} via iptables")
            return True
        except Exception as e:
            print(f"✗ Failed to block {ip_address}: {e}")
            return False
    
    def unload(self):
        """Unload XDP program"""
        if self.enabled:
            try:
                cmd = ['xdp-filter', 'unload', self.interface]
                subprocess.run(cmd, check=True, timeout=5)
                print(f"✓ XDP filter unloaded from {self.interface}")
            except Exception as e:
                print(f"⚠ Could not unload XDP: {e}")

class RealTimeDetectionSystem:
    """Main system orchestrating all components"""
    
    def __init__(self, interface='eth0', model_path=None):
        self.interface = interface
        self.flowmeter = FlowMeter()
        self.classifier = DDoSClassifier(model_path)
        self.xdp_filter = XDPFilter(interface)
        self.packet_count = 0
        self.detection_count = 0
        self.log_file = f"detection_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        self.logs = []
        
    def packet_handler(self, packet):
        """Handle each captured packet"""
        global running
        
        if not running:
            return
            
        self.packet_count += 1
        
        # Update flow statistics
        flow_key = self.flowmeter.update_flow(packet)
        
        if flow_key is None:
            return
            
        flow_data = self.flowmeter.flows[flow_key]
        
        # Only classify flows with sufficient packets
        if flow_data['packet_count'] % 10 == 0:  # Check every 10 packets
            features = self.flowmeter.extract_features(flow_key, flow_data)
            
            # Classify traffic
            is_malicious = self.classifier.predict(features)
            
            if is_malicious:
                src_ip = flow_key[0]
                
                if src_ip not in malicious_ips:
                    malicious_ips.add(src_ip)
                    self.detection_count += 1
                    
                    print(f"\n🚨 MALICIOUS TRAFFIC DETECTED!")
                    print(f"   Source IP: {src_ip}")
                    print(f"   Packets/sec: {features['packets_per_second']:.2f}")
                    print(f"   Bytes/sec: {features['bytes_per_second']:.2f}")
                    
                    # Log detection
                    log_entry = {
                        'timestamp': datetime.now().isoformat(),
                        'src_ip': src_ip,
                        'dst_ip': flow_key[1],
                        'src_port': flow_key[2],
                        'dst_port': flow_key[3],
                        'protocol': flow_key[4],
                        'features': {k: float(v) if isinstance(v, (int, float)) else v 
                                   for k, v in features.items()},
                        'action': 'blocked'
                    }
                    self.logs.append(log_entry)
                    
                    # Block the IP
                    self.xdp_filter.block_ip(src_ip)
        
        # Periodic status update
        if self.packet_count % 100 == 0:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] "
                  f"Packets: {self.packet_count} | "
                  f"Flows: {len(self.flowmeter.flows)} | "
                  f"Detections: {self.detection_count} | "
                  f"Blocked IPs: {len(blocked_ips)}")
    
    def start(self):
        """Start the detection system"""
        print("="*60)
        print("Real-Time DDoS Detection & Mitigation System")
        print("="*60)
        print(f"Interface: {self.interface}")
        print(f"Classifier: {'ML Model' if self.classifier.model else 'Heuristic'}")
        print(f"Filter: XDP + iptables fallback")
        print("="*60)
        
        # Load XDP filter
        self.xdp_filter.load()
        
        # Start cleanup thread
        cleanup_thread = threading.Thread(target=self.periodic_cleanup)
        cleanup_thread.daemon = True
        cleanup_thread.start()
        
        print("\n🎯 Starting packet capture... (Press Ctrl+C to stop)\n")
        
        try:
            # Start packet capture
            sniff(iface=self.interface, prn=self.packet_handler, 
                  store=False, stop_filter=lambda x: not running)
        except KeyboardInterrupt:
            print("\n\nStopping...")
        finally:
            self.stop()
    
    def periodic_cleanup(self):
        """Periodic cleanup of old flows"""
        while running:
            time.sleep(30)
            self.flowmeter.cleanup_old_flows()
    
    def stop(self):
        """Stop the system and save logs"""
        global running
        running = False
        
        print("\n" + "="*60)
        print("Shutting down...")
        print("="*60)
        
        # Save logs
        if self.logs:
            with open(self.log_file, 'w') as f:
                json.dump(self.logs, f, indent=2)
            print(f"✓ Saved {len(self.logs)} detections to {self.log_file}")
        
        # Unload XDP
        self.xdp_filter.unload()
        
        # Print summary
        print(f"\nSummary:")
        print(f"  Total packets processed: {self.packet_count}")
        print(f"  Malicious flows detected: {self.detection_count}")
        print(f"  IPs blocked: {len(blocked_ips)}")
        if blocked_ips:
            print(f"  Blocked IPs: {', '.join(list(blocked_ips)[:10])}")

def signal_handler(sig, frame):
    """Handle Ctrl+C"""
    global running
    running = False
    print("\n\nReceived interrupt signal...")

if __name__ == '__main__':
    # Set up signal handler
    signal.signal(signal.SIGINT, signal_handler)
    
    # Parse arguments
    interface = sys.argv[1] if len(sys.argv) > 1 else 'eth0'
    model_path = sys.argv[2] if len(sys.argv) > 2 else None
    
    # Check if running as root
    if os.geteuid() != 0:
        print("⚠ This script requires root privileges")
        print("Please run: sudo python3 ddos_detection.py [interface] [model_path]")
        sys.exit(1)
    
    # Start system
    system = RealTimeDetectionSystem(interface, model_path)
    system.start()
