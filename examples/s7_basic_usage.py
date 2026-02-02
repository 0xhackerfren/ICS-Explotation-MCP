#!/usr/bin/env python3
"""
Basic S7comm Usage Example

Demonstrates core functionality for Siemens S7 PLC communication:
1. Connect to PLC
2. Get CPU information
3. List blocks
4. Read from data blocks
5. Disconnect

Usage:
    python s7_basic_usage.py --ip 192.168.1.1 --port 102
"""

import sys
import os
import argparse

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ics_exploitation_mcp import ICSExploitationMCP


def main():
    parser = argparse.ArgumentParser(description="S7comm Basic Usage Example")
    parser.add_argument("--ip", required=True, help="PLC IP address")
    parser.add_argument("--port", type=int, default=102, help="S7comm port (default: 102)")
    parser.add_argument("--rack", type=int, default=0, help="Rack number (default: 0)")
    parser.add_argument("--slot", type=int, default=0, help="Slot number (default: 0)")
    args = parser.parse_args()
    
    print("=" * 50)
    print("S7comm Toolkit - Basic Usage Example")
    print("=" * 50)
    
    # Initialize
    mcp = ICSExploitationMCP()
    toolkit = mcp.s7
    
    # Check installation
    print("\n[1] Checking installation...")
    check = toolkit.check_installation()
    if check.get('installed'):
        print(f"    snap7 version: {check.get('version')}")
    else:
        print("    ERROR: python-snap7 not installed")
        print("    Run: pip install python-snap7")
        return
    
    # Connect
    print(f"\n[2] Connecting to {args.ip}:{args.port}...")
    result = toolkit.connect(args.ip, rack=args.rack, slot=args.slot, port=args.port)
    
    if not result.get('success'):
        print(f"    ERROR: {result.get('error')}")
        if result.get('hints'):
            for hint in result['hints']:
                print(f"    Hint: {hint}")
        return
    
    print(f"    Connected!")
    print(f"    CPU: {result.get('cpu_type', 'Unknown')}")
    
    # Get CPU info
    print("\n[3] CPU Information...")
    info = toolkit.get_cpu_info()
    if info.get('success'):
        print(f"    Module: {info.get('module_type')}")
        print(f"    Serial: {info.get('serial_number')}")
        print(f"    Name: {info.get('as_name')}")
    else:
        print(f"    Note: {info.get('error', 'Could not get CPU info')}")
    
    # Get CPU state
    print("\n[4] CPU State...")
    state = toolkit.get_cpu_state()
    if state.get('success'):
        print(f"    State: {state.get('state_name')}")
    
    # List blocks
    print("\n[5] Enumerating blocks...")
    blocks = toolkit.list_blocks()
    if blocks.get('success'):
        for block_type, count in blocks.get('blocks', {}).items():
            if count > 0:
                print(f"    {block_type}: {count}")
        if blocks.get('db_numbers'):
            print(f"    DB numbers: {blocks.get('db_numbers')}")
    
    # Read DB1 (if exists)
    print("\n[6] Reading Data Block 1...")
    
    # First get size
    size_result = toolkit.db_get_size(1)
    if size_result.get('success'):
        db_size = size_result.get('size', 100)
        print(f"    DB1 size: {db_size} bytes")
    else:
        db_size = 64
        print(f"    Could not get DB1 size, trying {db_size} bytes")
    
    # Read data
    data = toolkit.db_read(db_number=1, offset=0, size=min(db_size, 64))
    if data.get('success'):
        print(f"    Size read: {data.get('size')} bytes")
        print(f"    Non-zero bytes: {data.get('non_zero_count')}")
        hex_preview = data.get('data_hex', '')[:64]
        print(f"    Data (hex): {hex_preview}{'...' if len(data.get('data_hex', '')) > 64 else ''}")
    else:
        print(f"    Note: {data.get('error', 'DB1 may not exist')}")
    
    # Disconnect
    print("\n[7] Disconnecting...")
    toolkit.disconnect()
    print("    Done!")
    
    print("\n" + "=" * 50)
    print("Example complete. See README.md for more tools.")
    print("=" * 50)


if __name__ == "__main__":
    main()
