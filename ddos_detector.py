#!/usr/bin/env python3
"""
Real-Time DDoS Detection System
Complete pipeline: FlowMeter → ML Classifier → iptables Filter → JSON Logger

Components:
1. FlowMeter: Captures packets and extracts flow features
2. Classifier: Uses trained ML model (or heuristics if no model)
3. Filter: Blocks malicious IPs using iptables
4. Logger: Saves all detections to JSON file
"""

import os
import sys
import time
import signal
import threading
import subprocess
import argparse
import pickle
import json
from datetime import datetime
from collections import defaultdict

try:
    from scapy.all import sniff, IP, TCP, UDP, ICMP
except ImportError:
    print("Error: Scapy not installed. Run: pip3 install scapy --break-system-packages")
    sys.exit(1)

try:
    import numpy as np
except ImportError:
    print("Error: NumPy not installed. Run: pip3 install numpy --break-system-packages")
    sys.exit(1)


# Global variables
running = True
blocked_ips = set()
detection_logs = []


class Flow:
    """Represents a network flow with statistics for feature extraction"""
    
    def __init__(self, src_ip, dst_ip, src_port, dst_port, protocol):
        self.src_ip = src_ip
        self.dst_ip = dst_ip
        self.src_port = src_port
        self.dst_port = dst_port
        self.protocol = protocol
        
        # Timestamps
        self.start_time = None
        self.last_time = None
        
        # Packet counts
        self.fwd_packets = 0
        self.bwd_packets = 0
        
        # Byte counts
        self.fwd_bytes = 0
        self.bwd_bytes = 0
        
        # Packet sizes
        self.fwd_packet_sizes = []
        self.bwd_packet_sizes = []
        
        # Inter-arrival times
        self.fwd_iat = []
        self.bwd_iat = []
        self.last_fwd_time = None
        self.last_bwd_time = None
        
        # TCP flags
        self.syn_count = 0
        self.ack_count = 0
        self.fin_count = 0
        self.rst_count = 0
        self.psh_count = 0
        self.urg_count = 0
    
    def add_packet(self, packet, timestamp, is_forward):
        """Add packet to flow and update statistics"""
        if self.start_time is None:
            self.start_time = timestamp
        self.last_time = timestamp
        
        pkt_size = len(packet)
        
        if is_forward:
            self.fwd_packets += 1
            self.fwd_bytes += pkt_size
            self.fwd_packet_sizes.append(pkt_size)
            
            if self.last_fwd_time is not None:
                iat = (timestamp - self.last_fwd_time).total_seconds() * 1000000
                self.fwd_iat.append(iat)
            self.last_fwd_time = timestamp
        else:
            self.bwd_packets += 1
            self.bwd_bytes += pkt_size
            self.bwd_packet_sizes.append(pkt_size)
            
            if self.last_bwd_time is not None:
                iat = (timestamp - self.last_bwd_time).total_seconds() * 1000000
                self.bwd_iat.append(iat)
            self.last_bwd_time = timestamp
        
        # Count TCP flags
        if packet.haslayer(TCP):
            flags = packet[TCP].flags
            if flags & 0x02: self.syn_count += 1
            if flags & 0x10: self.ack_count += 1
            if flags & 0x01: self.fin_count += 1
            if flags & 0x04: self.rst_count += 1
            if flags & 0x08: self.psh_count += 1
            if flags & 0x20: self.urg_count += 1
    
    def get_duration(self):
        """Get flow duration in microseconds"""
        if self.start_time and self.last_time:
            return (self.last_time - self.start_time).total_seconds() * 1000000
        return 0
    
    def extract_features(self):
        """Extract features as numpy array for ML model"""
        duration = self.get_duration()
        duration_sec = duration / 1000000 if duration > 0 else 0.001
        
        total_packets = self.fwd_packets + self.bwd_packets
        total_bytes = self.fwd_bytes + self.bwd_bytes
        
        all_sizes = self.fwd_packet_sizes + self.bwd_packet_sizes
        all_iat = self.fwd_iat + self.bwd_iat
        
        features = {
            'flow_duration': duration,
            'total_fwd_packets': self.fwd_packets,
            'total_bwd_packets': self.bwd_packets,
            'total_packets': total_packets,
            'total_fwd_bytes': self.fwd_bytes,
            'total_bwd_bytes': self.bwd_bytes,
            'total_bytes': total_bytes,
            'fwd_pkt_len_min': min(self.fwd_packet_sizes) if self.fwd_packet_sizes else 0,
            'fwd_pkt_len_max': max(self.fwd_packet_sizes) if self.fwd_packet_sizes else 0,
            'fwd_pkt_len_mean': np.mean(self.fwd_packet_sizes) if self.fwd_packet_sizes else 0,
            'fwd_pkt_len_std': np.std(self.fwd_packet_sizes) if len(self.fwd_packet_sizes) > 1 else 0,
            'bwd_pkt_len_min': min(self.bwd_packet_sizes) if self.bwd_packet_sizes else 0,
            'bwd_pkt_len_max': max(self.bwd_packet_sizes) if self.bwd_packet_sizes else 0,
            'bwd_pkt_len_mean': np.mean(self.bwd_packet_sizes) if self.bwd_packet_sizes else 0,
            'bwd_pkt_len_std': np.std(self.bwd_packet_sizes) if len(self.bwd_packet_sizes) > 1 else 0,
            'pkt_len_min': min(all_sizes) if all_sizes else 0,
            'pkt_len_max': max(all_sizes) if all_sizes else 0,
            'pkt_len_mean': np.mean(all_sizes) if all_sizes else 0,
            'pkt_len_std': np.std(all_sizes) if len(all_sizes) > 1 else 0,
            'pkt_len_var': np.var(all_sizes) if len(all_sizes) > 1 else 0,
            'flow_bytes_per_sec': total_bytes / duration_sec,
            'flow_packets_per_sec': total_packets / duration_sec,
            'fwd_packets_per_sec': self.fwd_packets / duration_sec,
            'bwd_packets_per_sec': self.bwd_packets / duration_sec,
            'fwd_iat_total': sum(self.fwd_iat) if self.fwd_iat else 0,
            'fwd_iat_mean': np.mean(self.fwd_iat) if self.fwd_iat else 0,
            'fwd_iat_std': np.std(self.fwd_iat) if len(self.fwd_iat) > 1 else 0,
            'fwd_iat_min': min(self.fwd_iat) if self.fwd_iat else 0,
            'fwd_iat_max': max(self.fwd_iat) if self.fwd_iat else 0,
            'bwd_iat_total': sum(self.bwd_iat) if self.bwd_iat else 0,
            'bwd_iat_mean': np.mean(self.bwd_iat) if self.bwd_iat else 0,
            'bwd_iat_std': np.std(self.bwd_iat) if len(self.bwd_iat) > 1 else 0,
            'bwd_iat_min': min(self.bwd_iat) if self.bwd_iat else 0,
            'bwd_iat_max': max(self.bwd_iat) if self.bwd_iat else 0,
            'flow_iat_mean': np.mean(all_iat) if all_iat else 0,
            'flow_iat_std': np.std(all_iat) if len(all_iat) > 1 else 0,
            'flow_iat_min': min(all_iat) if all_iat else 0,
            'flow_iat_max': max(all_iat) if all_iat else 0,
            'syn_flag_count': self.syn_count,
            'ack_flag_count': self.ack_count,
            'fin_flag_count': self.fin_count,
            'rst_flag_count': self.rst_count,
            'psh_flag_count': self.psh_count,
            'urg_flag_count': self.urg_count,
            'down_up_ratio': self.bwd_packets / self.fwd_packets if self.fwd_packets > 0 else 0,
            'avg_pkt_size': total_bytes / total_packets if total_packets > 0 else 0,
            'fwd_seg_size_avg': self.fwd_bytes / self.fwd_packets if self.fwd_packets > 0 else 0,
            'bwd_seg_size_avg': self.bwd_bytes / self.bwd_packets if self.bwd_packets > 0 else 0,
        }
        
        return features


class FlowMeter:
    """Manages network flows and extracts features"""
    
    def __init__(self, timeout=120):
        self.flows = {}
        self.timeout = timeout
    
    def get_flow_key(self, packet):
        """Generate bidirectional flow key"""
        if not packet.haslayer(IP):
            return None
        
        ip = packet[IP]
        src_ip, dst_ip = ip.src, ip.dst
        protocol = ip.proto
        
        if packet.haslayer(TCP):
            src_port, dst_port = packet[TCP].sport, packet[TCP].dport
        elif packet.haslayer(UDP):
            src_port, dst_port = packet[UDP].sport, packet[UDP].dport
        else:
            src_port, dst_port = 0, 0
        
        # Bidirectional key
        if (src_ip, src_port) < (dst_ip, dst_port):
            return (src_ip, dst_ip, src_port, dst_port, protocol)
        else:
            return (dst_ip, src_ip, dst_port, src_port, protocol)
    
    def is_forward(self, packet, flow_key):
        """Check if packet is in forward direction"""
        if not packet.haslayer(IP):
            return True
        return packet[IP].src == flow_key[0]
    
    def process_packet(self, packet):
        """Process packet and return flow if ready for classification"""
        flow_key = self.get_flow_key(packet)
        if flow_key is None:
            return None, None
        
        timestamp = datetime.now()
        is_fwd = self.is_forward(packet, flow_key)
        
        # Get or create flow
        if flow_key not in self.flows:
            src_ip, dst_ip, src_port, dst_port, protocol = flow_key
            self.flows[flow_key] = Flow(src_ip, dst_ip, src_port, dst_port, protocol)
        
        flow = self.flows[flow_key]
        flow.add_packet(packet, timestamp, is_fwd)
        
        return flow_key, flow
    
    def cleanup_old_flows(self):
        """Remove expired flows"""
        now = datetime.now()
        expired = []
        
        for key, flow in self.flows.items():
            if flow.last_time:
                age = (now - flow.last_time).total_seconds()
                if age > self.timeout:
                    expired.append(key)
        
        for key in expired:
            del self.flows[key]
        
        return len(expired)


class MLClassifier:
    """ML-based DDoS classifier"""
    
    def __init__(self, model_path=None):
        self.model = None
        self.scaler = None
        self.label_encoder = None
        self.feature_columns = None
        self.use_heuristics = True
        
        if model_path and os.path.exists(model_path):
            self.load_model(model_path)
    
    def load_model(self, model_path):
        """Load trained model"""
        try:
            with open(model_path, 'rb') as f:
                model_data = pickle.load(f)
            
            self.model = model_data['model']
            self.scaler = model_data['scaler']
            self.label_encoder = model_data['label_encoder']
            self.feature_columns = model_data['feature_columns']
            self.use_heuristics = False
            
            print(f"✓ Loaded ML model from: {model_path}")
            print(f"  Model type: {model_data.get('model_type', 'unknown')}")
            print(f"  Features: {len(self.feature_columns)}")
            print(f"  Accuracy: {model_data['metrics'].get('accuracy', 0)*100:.1f}%")
            
        except Exception as e:
            print(f"⚠ Could not load model: {e}")
            print("  Using heuristic detection instead")
            self.use_heuristics = True
    
    def predict(self, flow_features):
        """Predict if flow is malicious"""
        if self.use_heuristics:
            return self.heuristic_detection(flow_features)
        
        try:
            # Prepare feature vector
            feature_vector = []
            for col in self.feature_columns:
                feature_vector.append(flow_features.get(col, 0))
            
            # Scale and predict
            X = np.array([feature_vector])
            X_scaled = self.scaler.transform(X)
            prediction = self.model.predict(X_scaled)[0]
            
            # Get probability if available
            confidence = 0.0
            if hasattr(self.model, 'predict_proba'):
                proba = self.model.predict_proba(X_scaled)[0]
                confidence = max(proba)
            
            # Check if prediction is malicious (not BENIGN)
            label = self.label_encoder.inverse_transform([prediction])[0]
            is_malicious = label.upper() != 'BENIGN'
            
            return is_malicious, label, confidence
            
        except Exception as e:
            print(f"⚠ Prediction error: {e}")
            return self.heuristic_detection(flow_features)
    
    def heuristic_detection(self, features):
        """Rule-based detection when no ML model"""
        reasons = []
        
        # Rule 1: High packet rate (>1000 pps)
        pps = features.get('flow_packets_per_sec', 0)
        if pps > 1000:
            reasons.append(f"High packet rate: {pps:.0f} pps")
        
        # Rule 2: SYN flood indicator (many SYNs, few ACKs)
        syn = features.get('syn_flag_count', 0)
        ack = features.get('ack_flag_count', 0)
        if syn > 50 and (ack == 0 or syn / (ack + 1) > 10):
            reasons.append(f"SYN flood pattern: {syn} SYNs, {ack} ACKs")
        
        # Rule 3: High bandwidth (>10 MB/s)
        bps = features.get('flow_bytes_per_sec', 0)
        if bps > 10_000_000:
            reasons.append(f"High bandwidth: {bps/1_000_000:.1f} MB/s")
        
        # Rule 4: Small packets + high rate (amplification attack)
        avg_size = features.get('avg_pkt_size', 0)
        if avg_size < 100 and pps > 500:
            reasons.append(f"Small packets ({avg_size:.0f}B) + high rate")
        
        # Rule 5: Asymmetric traffic (many forward, few backward)
        fwd = features.get('total_fwd_packets', 0)
        bwd = features.get('total_bwd_packets', 0)
        if fwd > 100 and (bwd == 0 or fwd / (bwd + 1) > 20):
            reasons.append(f"Asymmetric: {fwd} fwd, {bwd} bwd")
        
        is_malicious = len(reasons) > 0
        label = "DDoS" if is_malicious else "BENIGN"
        confidence = min(len(reasons) / 3, 1.0)  # More reasons = higher confidence
        
        return is_malicious, label, confidence, reasons if is_malicious else []


class IPTablesFilter:
    """Manages iptables rules for blocking IPs"""
    
    def __init__(self):
        self.blocked_ips = set()
    
    def block_ip(self, ip_address):
        """Block an IP using iptables"""
        if ip_address in self.blocked_ips:
            return True
        
        # Skip localhost and private ranges if needed
        if ip_address.startswith('127.') or ip_address == '0.0.0.0':
            return False
        
        try:
            cmd = ['iptables', '-A', 'INPUT', '-s', ip_address, '-j', 'DROP']
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0:
                self.blocked_ips.add(ip_address)
                print(f"   ✓ Blocked {ip_address} via iptables")
                return True
            else:
                print(f"   ⚠ Failed to block {ip_address}: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"   ✗ Error blocking {ip_address}: {e}")
            return False
    
    def unblock_ip(self, ip_address):
        """Remove block for an IP"""
        try:
            cmd = ['iptables', '-D', 'INPUT', '-s', ip_address, '-j', 'DROP']
            subprocess.run(cmd, capture_output=True, timeout=5)
            self.blocked_ips.discard(ip_address)
            return True
        except:
            return False
    
    def list_blocked(self):
        """List all blocked IPs"""
        return list(self.blocked_ips)
    
    def clear_all(self):
        """Remove all blocks"""
        for ip in list(self.blocked_ips):
            self.unblock_ip(ip)


class JSONLogger:
    """Logs detections to JSON file"""
    
    def __init__(self, output_file=None):
        if output_file is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = f'detection_log_{timestamp}.json'
        
        self.output_file = output_file
        self.logs = []
    
    def log_detection(self, flow_features, prediction_label, confidence, action, reasons=None):
        """Log a detection event"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'src_ip': flow_features.get('src_ip', 'unknown'),
            'dst_ip': flow_features.get('dst_ip', 'unknown'),
            'src_port': flow_features.get('src_port', 0),
            'dst_port': flow_features.get('dst_port', 0),
            'protocol': flow_features.get('protocol', 0),
            'prediction': prediction_label,
            'confidence': round(confidence, 4),
            'action': action,
            'features': {
                'flow_duration': flow_features.get('flow_duration', 0),
                'total_packets': flow_features.get('total_packets', 0),
                'total_bytes': flow_features.get('total_bytes', 0),
                'packets_per_sec': round(flow_features.get('flow_packets_per_sec', 0), 2),
                'bytes_per_sec': round(flow_features.get('flow_bytes_per_sec', 0), 2),
                'avg_packet_size': round(flow_features.get('avg_pkt_size', 0), 2),
                'syn_count': flow_features.get('syn_flag_count', 0),
                'ack_count': flow_features.get('ack_flag_count', 0),
            }
        }
        
        if reasons:
            log_entry['reasons'] = reasons
        
        self.logs.append(log_entry)
        return log_entry
    
    def save(self):
        """Save logs to file"""
        with open(self.output_file, 'w') as f:
            json.dump(self.logs, f, indent=2)
        return self.output_file
    
    def get_stats(self):
        """Get detection statistics"""
        return {
            'total_detections': len(self.logs),
            'unique_ips': len(set(log['src_ip'] for log in self.logs)),
            'log_file': self.output_file
        }


class DDoSDetectionSystem:
    """Main detection system orchestrating all components"""
    
    def __init__(self, interface='eth0', model_path=None, log_file=None):
        self.interface = interface
        
        # Initialize components
        self.flowmeter = FlowMeter(timeout=120)
        self.classifier = MLClassifier(model_path)
        self.filter = IPTablesFilter()
        self.logger = JSONLogger(log_file)
        
        # Statistics
        self.packet_count = 0
        self.flow_count = 0
        self.detection_count = 0
        self.malicious_ips = set()
        
        # Settings
        self.check_interval = 10  # Check flow every N packets
        self.min_packets_for_detection = 5  # Minimum packets before classification
    
    def process_packet(self, packet):
        """Process a single packet"""
        global running
        
        if not running:
            return
        
        self.packet_count += 1
        
        # Update flow
        flow_key, flow = self.flowmeter.process_packet(packet)
        if flow_key is None:
            return
        
        # Only classify periodically (not every packet)
        total_pkts = flow.fwd_packets + flow.bwd_packets
        if total_pkts < self.min_packets_for_detection:
            return
        
        if total_pkts % self.check_interval != 0:
            return
        
        # Extract features
        features = flow.extract_features()
        features['src_ip'] = flow.src_ip
        features['dst_ip'] = flow.dst_ip
        features['src_port'] = flow.src_port
        features['dst_port'] = flow.dst_port
        features['protocol'] = flow.protocol
        
        # Classify
        result = self.classifier.predict(features)
        
        if len(result) == 4:  # Heuristic mode
            is_malicious, label, confidence, reasons = result
        else:  # ML mode
            is_malicious, label, confidence = result
            reasons = []
        
        if is_malicious:
            src_ip = flow.src_ip
            
            if src_ip not in self.malicious_ips:
                self.malicious_ips.add(src_ip)
                self.detection_count += 1
                
                # Print alert
                print(f"\n{'='*60}")
                print(f"🚨 MALICIOUS TRAFFIC DETECTED!")
                print(f"{'='*60}")
                print(f"   Source IP:    {src_ip}")
                print(f"   Destination:  {flow.dst_ip}:{flow.dst_port}")
                print(f"   Protocol:     {'TCP' if flow.protocol == 6 else 'UDP' if flow.protocol == 17 else flow.protocol}")
                print(f"   Prediction:   {label}")
                print(f"   Confidence:   {confidence*100:.1f}%")
                print(f"   Packets/sec:  {features['flow_packets_per_sec']:.2f}")
                print(f"   Bytes/sec:    {features['flow_bytes_per_sec']:.2f}")
                
                if reasons:
                    print(f"   Reasons:")
                    for reason in reasons:
                        print(f"      - {reason}")
                
                # Block IP
                blocked = self.filter.block_ip(src_ip)
                action = 'blocked' if blocked else 'detected'
                
                # Log detection
                self.logger.log_detection(features, label, confidence, action, reasons)
                
                print(f"{'='*60}\n")
        
        # Print status periodically
        if self.packet_count % 200 == 0:
            self.print_status()
    
    def print_status(self):
        """Print current status"""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] "
              f"Packets: {self.packet_count} | "
              f"Flows: {len(self.flowmeter.flows)} | "
              f"Detections: {self.detection_count} | "
              f"Blocked: {len(self.filter.blocked_ips)}")
    
    def cleanup_thread(self):
        """Background cleanup of old flows"""
        while running:
            time.sleep(30)
            removed = self.flowmeter.cleanup_old_flows()
            if removed > 0:
                print(f"   [Cleanup] Removed {removed} expired flows")
    
    def start(self):
        """Start the detection system"""
        global running
        
        print("\n" + "=" * 60)
        print("🛡️  Real-Time DDoS Detection System")
        print("=" * 60)
        print(f"Interface:   {self.interface}")
        print(f"Classifier:  {'ML Model' if not self.classifier.use_heuristics else 'Heuristic Rules'}")
        print(f"Filter:      iptables")
        print(f"Log File:    {self.logger.output_file}")
        print("=" * 60)
        
        # Start cleanup thread
        cleanup = threading.Thread(target=self.cleanup_thread, daemon=True)
        cleanup.start()
        
        print("\n🎯 Starting packet capture... (Press Ctrl+C to stop)\n")
        
        try:
            sniff(
                iface=self.interface,
                prn=self.process_packet,
                store=False,
                stop_filter=lambda x: not running
            )
        except KeyboardInterrupt:
            print("\n\n⚠ Interrupted by user")
        except Exception as e:
            print(f"\n\n❌ Error: {e}")
        finally:
            self.stop()
    
    def stop(self):
        """Stop the system and save logs"""
        global running
        running = False
        
        print("\n" + "=" * 60)
        print("Shutting down...")
        print("=" * 60)
        
        # Save logs
        log_file = self.logger.save()
        stats = self.logger.get_stats()
        
        print(f"\n📊 Session Summary:")
        print(f"   Total Packets:     {self.packet_count}")
        print(f"   Total Flows:       {self.flow_count + len(self.flowmeter.flows)}")
        print(f"   Detections:        {self.detection_count}")
        print(f"   Blocked IPs:       {len(self.filter.blocked_ips)}")
        
        if self.filter.blocked_ips:
            print(f"\n   Blocked IP List:")
            for ip in list(self.filter.blocked_ips)[:10]:
                print(f"      - {ip}")
            if len(self.filter.blocked_ips) > 10:
                print(f"      ... and {len(self.filter.blocked_ips) - 10} more")
        
        print(f"\n✓ Logs saved to: {log_file}")
        print(f"✓ Total detections logged: {stats['total_detections']}")
        print("=" * 60)


def signal_handler(sig, frame):
    """Handle Ctrl+C"""
    global running
    running = False
    print("\n\nReceived interrupt signal...")


def main():
    parser = argparse.ArgumentParser(
        description='Real-Time DDoS Detection System',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Run with heuristic detection
  sudo python3 ddos_detector.py -i eth0
  
  # Run with trained ML model
  sudo python3 ddos_detector.py -i eth0 -m ddos_model.pkl
  
  # Specify output log file
  sudo python3 ddos_detector.py -i eth0 -o detections.json
        '''
    )
    
    parser.add_argument('-i', '--interface', default='eth0',
                        help='Network interface (default: eth0)')
    parser.add_argument('-m', '--model', type=str, default=None,
                        help='Path to trained ML model (.pkl)')
    parser.add_argument('-o', '--output', type=str, default=None,
                        help='Output JSON log file')
    
    args = parser.parse_args()
    
    # Check root privileges
    if os.geteuid() != 0:
        print("❌ This script requires root privileges")
        print("Please run: sudo python3 ddos_detector.py ...")
        sys.exit(1)
    
    # Setup signal handler
    signal.signal(signal.SIGINT, signal_handler)
    
    # Create and start system
    system = DDoSDetectionSystem(
        interface=args.interface,
        model_path=args.model,
        log_file=args.output
    )
    
    system.start()


if __name__ == '__main__':
    main()
