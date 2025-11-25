#!/usr/bin/env python3
"""
FlowMeter - Network Flow Feature Extractor
Captures packets and extracts flow-based features for ML classification

Features extracted (similar to CICFlowMeter):
- Flow duration
- Total packets (forward/backward)
- Total bytes (forward/backward)
- Packet rate
- Byte rate
- Packet size statistics (min, max, mean, std)
- Inter-arrival time statistics
- TCP flags counts
- Protocol type
"""

import os
import sys
import time
import signal
import threading
import argparse
from datetime import datetime
from collections import defaultdict
import csv
import json

try:
    from scapy.all import sniff, IP, TCP, UDP, ICMP, Raw
    from scapy.layers.inet import IP, TCP, UDP
except ImportError:
    print("Error: Scapy not installed. Run: pip3 install scapy --break-system-packages")
    sys.exit(1)

try:
    import numpy as np
except ImportError:
    print("Error: NumPy not installed. Run: pip3 install numpy --break-system-packages")
    sys.exit(1)


class Flow:
    """Represents a single network flow with statistics"""
    
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
        self.fwd_packets = 0  # Forward packets (src -> dst)
        self.bwd_packets = 0  # Backward packets (dst -> src)
        
        # Byte counts
        self.fwd_bytes = 0
        self.bwd_bytes = 0
        
        # Packet sizes
        self.fwd_packet_sizes = []
        self.bwd_packet_sizes = []
        
        # Inter-arrival times
        self.fwd_iat = []  # Forward inter-arrival times
        self.bwd_iat = []  # Backward inter-arrival times
        self.last_fwd_time = None
        self.last_bwd_time = None
        
        # TCP flags (if TCP)
        self.syn_count = 0
        self.ack_count = 0
        self.fin_count = 0
        self.rst_count = 0
        self.psh_count = 0
        self.urg_count = 0
        
        # Flow state
        self.is_active = True
        
    def add_packet(self, packet, timestamp, is_forward):
        """Add a packet to the flow and update statistics"""
        
        # Update timestamps
        if self.start_time is None:
            self.start_time = timestamp
        self.last_time = timestamp
        
        # Get packet size
        pkt_size = len(packet)
        
        if is_forward:
            self.fwd_packets += 1
            self.fwd_bytes += pkt_size
            self.fwd_packet_sizes.append(pkt_size)
            
            # Calculate inter-arrival time
            if self.last_fwd_time is not None:
                iat = (timestamp - self.last_fwd_time).total_seconds() * 1000000  # microseconds
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
            tcp = packet[TCP]
            flags = tcp.flags
            if flags & 0x02:  # SYN
                self.syn_count += 1
            if flags & 0x10:  # ACK
                self.ack_count += 1
            if flags & 0x01:  # FIN
                self.fin_count += 1
            if flags & 0x04:  # RST
                self.rst_count += 1
            if flags & 0x08:  # PSH
                self.psh_count += 1
            if flags & 0x20:  # URG
                self.urg_count += 1
    
    def get_duration(self):
        """Get flow duration in microseconds"""
        if self.start_time and self.last_time:
            return (self.last_time - self.start_time).total_seconds() * 1000000
        return 0
    
    def extract_features(self):
        """Extract all features as a dictionary"""
        duration = self.get_duration()
        duration_sec = duration / 1000000 if duration > 0 else 0.001
        
        total_packets = self.fwd_packets + self.bwd_packets
        total_bytes = self.fwd_bytes + self.bwd_bytes
        
        all_packet_sizes = self.fwd_packet_sizes + self.bwd_packet_sizes
        all_iat = self.fwd_iat + self.bwd_iat
        
        features = {
            # Basic flow info
            'src_ip': self.src_ip,
            'dst_ip': self.dst_ip,
            'src_port': self.src_port,
            'dst_port': self.dst_port,
            'protocol': self.protocol,
            
            # Duration
            'flow_duration': duration,
            
            # Packet counts
            'total_fwd_packets': self.fwd_packets,
            'total_bwd_packets': self.bwd_packets,
            'total_packets': total_packets,
            
            # Byte counts
            'total_fwd_bytes': self.fwd_bytes,
            'total_bwd_bytes': self.bwd_bytes,
            'total_bytes': total_bytes,
            
            # Packet size statistics - Forward
            'fwd_pkt_len_min': min(self.fwd_packet_sizes) if self.fwd_packet_sizes else 0,
            'fwd_pkt_len_max': max(self.fwd_packet_sizes) if self.fwd_packet_sizes else 0,
            'fwd_pkt_len_mean': np.mean(self.fwd_packet_sizes) if self.fwd_packet_sizes else 0,
            'fwd_pkt_len_std': np.std(self.fwd_packet_sizes) if len(self.fwd_packet_sizes) > 1 else 0,
            
            # Packet size statistics - Backward
            'bwd_pkt_len_min': min(self.bwd_packet_sizes) if self.bwd_packet_sizes else 0,
            'bwd_pkt_len_max': max(self.bwd_packet_sizes) if self.bwd_packet_sizes else 0,
            'bwd_pkt_len_mean': np.mean(self.bwd_packet_sizes) if self.bwd_packet_sizes else 0,
            'bwd_pkt_len_std': np.std(self.bwd_packet_sizes) if len(self.bwd_packet_sizes) > 1 else 0,
            
            # Packet size statistics - All
            'pkt_len_min': min(all_packet_sizes) if all_packet_sizes else 0,
            'pkt_len_max': max(all_packet_sizes) if all_packet_sizes else 0,
            'pkt_len_mean': np.mean(all_packet_sizes) if all_packet_sizes else 0,
            'pkt_len_std': np.std(all_packet_sizes) if len(all_packet_sizes) > 1 else 0,
            'pkt_len_var': np.var(all_packet_sizes) if len(all_packet_sizes) > 1 else 0,
            
            # Flow rates
            'flow_bytes_per_sec': total_bytes / duration_sec,
            'flow_packets_per_sec': total_packets / duration_sec,
            'fwd_packets_per_sec': self.fwd_packets / duration_sec,
            'bwd_packets_per_sec': self.bwd_packets / duration_sec,
            
            # Inter-arrival time statistics - Forward
            'fwd_iat_total': sum(self.fwd_iat) if self.fwd_iat else 0,
            'fwd_iat_mean': np.mean(self.fwd_iat) if self.fwd_iat else 0,
            'fwd_iat_std': np.std(self.fwd_iat) if len(self.fwd_iat) > 1 else 0,
            'fwd_iat_min': min(self.fwd_iat) if self.fwd_iat else 0,
            'fwd_iat_max': max(self.fwd_iat) if self.fwd_iat else 0,
            
            # Inter-arrival time statistics - Backward
            'bwd_iat_total': sum(self.bwd_iat) if self.bwd_iat else 0,
            'bwd_iat_mean': np.mean(self.bwd_iat) if self.bwd_iat else 0,
            'bwd_iat_std': np.std(self.bwd_iat) if len(self.bwd_iat) > 1 else 0,
            'bwd_iat_min': min(self.bwd_iat) if self.bwd_iat else 0,
            'bwd_iat_max': max(self.bwd_iat) if self.bwd_iat else 0,
            
            # Inter-arrival time statistics - All
            'flow_iat_mean': np.mean(all_iat) if all_iat else 0,
            'flow_iat_std': np.std(all_iat) if len(all_iat) > 1 else 0,
            'flow_iat_min': min(all_iat) if all_iat else 0,
            'flow_iat_max': max(all_iat) if all_iat else 0,
            
            # TCP flags
            'syn_flag_count': self.syn_count,
            'ack_flag_count': self.ack_count,
            'fin_flag_count': self.fin_count,
            'rst_flag_count': self.rst_count,
            'psh_flag_count': self.psh_count,
            'urg_flag_count': self.urg_count,
            
            # Derived features
            'down_up_ratio': self.bwd_packets / self.fwd_packets if self.fwd_packets > 0 else 0,
            'avg_pkt_size': total_bytes / total_packets if total_packets > 0 else 0,
            'fwd_seg_size_avg': self.fwd_bytes / self.fwd_packets if self.fwd_packets > 0 else 0,
            'bwd_seg_size_avg': self.bwd_bytes / self.bwd_packets if self.bwd_packets > 0 else 0,
            
            # Timestamp
            'timestamp': self.start_time.isoformat() if self.start_time else None,
        }
        
        return features


class FlowMeter:
    """
    Captures network packets and extracts flow features
    Similar to CICFlowMeter functionality
    """
    
    def __init__(self, interface='eth0', timeout=120, output_file='flows.csv'):
        self.interface = interface
        self.timeout = timeout  # Flow timeout in seconds
        self.output_file = output_file
        
        self.flows = {}  # Active flows
        self.completed_flows = []  # Flows ready for export
        
        self.running = False
        self.packet_count = 0
        self.flow_count = 0
        
        # CSV writer
        self.csv_file = None
        self.csv_writer = None
        self.header_written = False
        
    def _get_flow_key(self, packet):
        """Generate flow key from packet (5-tuple)"""
        if not packet.haslayer(IP):
            return None
            
        ip = packet[IP]
        src_ip = ip.src
        dst_ip = ip.dst
        protocol = ip.proto
        
        if packet.haslayer(TCP):
            src_port = packet[TCP].sport
            dst_port = packet[TCP].dport
        elif packet.haslayer(UDP):
            src_port = packet[UDP].sport
            dst_port = packet[UDP].dport
        else:
            src_port = 0
            dst_port = 0
        
        # Bidirectional flow key (sorted to match forward/backward)
        if (src_ip, src_port) < (dst_ip, dst_port):
            return (src_ip, dst_ip, src_port, dst_port, protocol)
        else:
            return (dst_ip, src_ip, dst_port, src_port, protocol)
    
    def _is_forward(self, packet, flow_key):
        """Determine if packet is forward or backward"""
        if not packet.haslayer(IP):
            return True
        
        ip = packet[IP]
        return ip.src == flow_key[0]
    
    def _process_packet(self, packet):
        """Process a captured packet"""
        self.packet_count += 1
        
        flow_key = self._get_flow_key(packet)
        if flow_key is None:
            return
        
        timestamp = datetime.now()
        is_forward = self._is_forward(packet, flow_key)
        
        # Get or create flow
        if flow_key not in self.flows:
            src_ip, dst_ip, src_port, dst_port, protocol = flow_key
            self.flows[flow_key] = Flow(src_ip, dst_ip, src_port, dst_port, protocol)
            self.flow_count += 1
        
        # Add packet to flow
        self.flows[flow_key].add_packet(packet, timestamp, is_forward)
        
        # Print progress
        if self.packet_count % 100 == 0:
            print(f"[{timestamp.strftime('%H:%M:%S')}] "
                  f"Packets: {self.packet_count} | "
                  f"Active Flows: {len(self.flows)} | "
                  f"Completed Flows: {len(self.completed_flows)}")
    
    def _cleanup_flows(self):
        """Move expired flows to completed list"""
        now = datetime.now()
        expired = []
        
        for flow_key, flow in self.flows.items():
            if flow.last_time:
                age = (now - flow.last_time).total_seconds()
                if age > self.timeout:
                    expired.append(flow_key)
        
        for flow_key in expired:
            flow = self.flows.pop(flow_key)
            self._export_flow(flow)
    
    def _export_flow(self, flow):
        """Export flow features to CSV"""
        features = flow.extract_features()
        
        # Initialize CSV if not done
        if self.csv_writer is None:
            self.csv_file = open(self.output_file, 'w', newline='')
            self.csv_writer = csv.DictWriter(self.csv_file, fieldnames=features.keys())
            self.csv_writer.writeheader()
        
        self.csv_writer.writerow(features)
        self.csv_file.flush()
        self.completed_flows.append(features)
    
    def _cleanup_thread(self):
        """Background thread for flow cleanup"""
        while self.running:
            time.sleep(10)  # Check every 10 seconds
            self._cleanup_flows()
    
    def start(self, duration=None, packet_count=None):
        """Start capturing packets"""
        print("=" * 60)
        print("FlowMeter - Network Flow Feature Extractor")
        print("=" * 60)
        print(f"Interface: {self.interface}")
        print(f"Flow Timeout: {self.timeout} seconds")
        print(f"Output File: {self.output_file}")
        print("=" * 60)
        print("\n🎯 Starting packet capture... (Press Ctrl+C to stop)\n")
        
        self.running = True
        
        # Start cleanup thread
        cleanup = threading.Thread(target=self._cleanup_thread, daemon=True)
        cleanup.start()
        
        try:
            # Build sniff arguments
            sniff_kwargs = {
                'iface': self.interface,
                'prn': self._process_packet,
                'store': False,
            }
            
            if duration:
                sniff_kwargs['timeout'] = duration
            if packet_count:
                sniff_kwargs['count'] = packet_count
            
            sniff(**sniff_kwargs)
            
        except KeyboardInterrupt:
            print("\n\n⚠ Capture interrupted by user")
        except Exception as e:
            print(f"\n\n❌ Error: {e}")
        finally:
            self.stop()
    
    def stop(self):
        """Stop capturing and export remaining flows"""
        self.running = False
        
        print("\n" + "=" * 60)
        print("Stopping FlowMeter...")
        print("=" * 60)
        
        # Export all remaining flows
        for flow in self.flows.values():
            self._export_flow(flow)
        
        if self.csv_file:
            self.csv_file.close()
        
        print(f"\n✓ Capture complete!")
        print(f"  Total Packets: {self.packet_count}")
        print(f"  Total Flows: {len(self.completed_flows)}")
        print(f"  Output File: {self.output_file}")
        print("=" * 60)


def main():
    parser = argparse.ArgumentParser(
        description='FlowMeter - Network Flow Feature Extractor',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Capture packets for 60 seconds
  sudo python3 flowmeter.py -i eth0 -d 60 -o flows.csv
  
  # Capture 1000 packets
  sudo python3 flowmeter.py -i eth0 -c 1000 -o flows.csv
  
  # Continuous capture (Ctrl+C to stop)
  sudo python3 flowmeter.py -i eth0 -o flows.csv
        '''
    )
    
    parser.add_argument('-i', '--interface', default='eth0',
                        help='Network interface (default: eth0)')
    parser.add_argument('-o', '--output', default='flows.csv',
                        help='Output CSV file (default: flows.csv)')
    parser.add_argument('-d', '--duration', type=int, default=None,
                        help='Capture duration in seconds')
    parser.add_argument('-c', '--count', type=int, default=None,
                        help='Number of packets to capture')
    parser.add_argument('-t', '--timeout', type=int, default=120,
                        help='Flow timeout in seconds (default: 120)')
    
    args = parser.parse_args()
    
    # Check root privileges
    if os.geteuid() != 0:
        print("❌ This script requires root privileges")
        print("Please run: sudo python3 flowmeter.py ...")
        sys.exit(1)
    
    # Create and start FlowMeter
    fm = FlowMeter(
        interface=args.interface,
        timeout=args.timeout,
        output_file=args.output
    )
    
    fm.start(duration=args.duration, packet_count=args.count)


if __name__ == '__main__':
    main()
