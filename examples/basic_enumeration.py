#!/usr/bin/env python3
"""
Basic OPC-UA Enumeration Example

Demonstrates how to:
1. Enumerate server endpoints
2. Generate certificates
3. Connect securely
4. Browse the node hierarchy
5. Find writable variables

Usage:
    python basic_enumeration.py opc.tcp://target:4840
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ics_exploitation_mcp import ICSExploitationMCP


def main():
    # Target OPC-UA server
    TARGET = sys.argv[1] if len(sys.argv) > 1 else "opc.tcp://localhost:4840"
    
    print("=" * 60)
    print("OPC-UA Security Toolkit - Basic Enumeration")
    print("=" * 60)
    
    mcp = ICSExploitationMCP()
    toolkit = mcp.opcua
    
    # Check installation
    print("\n[*] Checking installation...")
    status = toolkit.check_installation()
    if not status['ready']:
        print("[!] Missing dependencies:")
        for dep, info in status['dependencies'].items():
            if not info['installed']:
                print(f"    {dep}: {info['install']}")
        return
    print("[+] All dependencies installed")
    
    # Step 1: Enumerate endpoints
    print(f"\n[*] Enumerating endpoints: {TARGET}")
    endpoints = toolkit.enumerate_endpoints(TARGET)
    
    if "error" in endpoints:
        print(f"[!] Error: {endpoints['error']}")
        print(f"    Hint: {endpoints.get('hint', 'Check target connectivity')}")
        return
    
    print(f"[+] Found {endpoints['endpoint_count']} endpoint(s)")
    print(f"[+] Security policies: {endpoints['security_policies']}")
    print(f"[+] Recommendation: {endpoints['recommendation']}")
    
    for ep in endpoints['endpoints']:
        print(f"\n    Endpoint {ep['index']}:")
        print(f"      Policy: {ep['security_policy']}")
        print(f"      Mode: {ep['security_mode']}")
        print(f"      Tokens: {ep['user_tokens']}")
    
    # Step 2: Generate certificates if needed
    needs_certs = "None" not in endpoints['security_policies']
    
    if needs_certs:
        print("\n[*] Server requires encryption, generating certificates...")
        certs = toolkit.generate_self_signed_cert("./test_certs")
        
        if "error" in certs:
            print(f"[!] Error: {certs['error']}")
            return
        
        print(f"[+] Certificate: {certs['cert_path']}")
        print(f"[+] Private key: {certs['key_path']}")
        print(f"[+] Thumbprint: {certs['thumbprint']}")
        
        # Connect with security
        policy = endpoints['security_policies'][0]  # Use first available
        mode = "SignAndEncrypt" if policy != "None" else "None"
        
        print(f"\n[*] Connecting with {policy} / {mode}...")
        result = toolkit.connect(
            url=TARGET,
            cert_path=certs['cert_path'],
            key_path=certs['key_path'],
            security_policy=policy,
            security_mode=mode
        )
    else:
        print("\n[*] Connecting without encryption...")
        result = toolkit.connect(url=TARGET)
    
    if "error" in result:
        print(f"[!] Connection failed: {result['error']}")
        return
    
    print("[+] Connected successfully!")
    
    # Step 3: Enumerate nodes
    print("\n[*] Enumerating nodes (max depth 5)...")
    nodes = toolkit.enumerate_nodes(max_depth=5)
    
    if "error" in nodes:
        print(f"[!] Error: {nodes['error']}")
    else:
        print(f"[+] Found {nodes['total_count']} nodes")
        print(f"[+] Writable variables: {nodes['writable_count']}")
    
    # Step 4: Find writable variables (attack surface)
    print("\n[*] Finding writable variables...")
    writable = toolkit.find_writable_variables()
    
    if "error" not in writable and writable['count'] > 0:
        print(f"[+] Attack Surface ({writable['count']} variables):")
        print(writable['attack_notes'])
    else:
        print("[*] No writable variables found")
    
    # Cleanup
    print("\n[*] Disconnecting...")
    toolkit.disconnect()
    print("[+] Done!")


if __name__ == "__main__":
    main()
