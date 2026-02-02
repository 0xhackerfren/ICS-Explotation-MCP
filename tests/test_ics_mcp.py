#!/usr/bin/env python3
"""
Test Suite for ICS Exploitation MCP

Tests basic functionality without requiring live PLC connections.
For live testing, use --live flag with target parameters.

Usage:
    # Basic tests (no connection required)
    python test_ics_mcp.py
    
    # Live OPC-UA tests
    python test_ics_mcp.py --live-opcua --opcua-url opc.tcp://target:4840
    
    # Live S7 tests
    python test_ics_mcp.py --live-s7 --s7-ip 192.168.1.1 --s7-port 102
    
    # All tests
    python test_ics_mcp.py --all --opcua-url opc.tcp://target:4840 --s7-ip 192.168.1.1 --s7-port 102
"""

import sys
import os
import json
import argparse

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ics_exploitation_mcp import ICSExploitationMCP, OPCUA_AVAILABLE, SNAP7_AVAILABLE


def print_result(name: str, result: dict, indent: int = 2):
    """Pretty print a test result"""
    print(f"\n[TEST] {name}")
    print("-" * 50)
    print(json.dumps(result, indent=indent, default=str))


def test_mcp_initialization():
    """Test MCP initialization"""
    print("\n" + "=" * 60)
    print("MCP INITIALIZATION TESTS")
    print("=" * 60)
    
    mcp = ICSExploitationMCP()
    
    # Test basic attributes
    assert mcp.name == "ics-exploitation-mcp", "Should have correct name"
    assert mcp.version == "1.0.0", "Should have correct version"
    assert mcp.opcua is not None, "Should have OPC-UA toolkit"
    assert mcp.s7 is not None, "Should have S7 toolkit"
    
    print("[PASS] MCP initialization")
    return True


def test_installation_check():
    """Test installation check functionality"""
    print("\n" + "=" * 60)
    print("INSTALLATION CHECK TESTS")
    print("=" * 60)
    
    mcp = ICSExploitationMCP()
    
    # Test combined check
    result = mcp.check_installation()
    print_result("check_installation()", result)
    
    assert "protocols" in result, "Should have protocols key"
    assert "opcua" in result["protocols"], "Should have OPC-UA status"
    assert "s7comm" in result["protocols"], "Should have S7comm status"
    assert "any_protocol_ready" in result, "Should have any_protocol_ready flag"
    
    print("[PASS] Installation check")
    return True


def test_capabilities_listing():
    """Test capabilities listing"""
    print("\n" + "=" * 60)
    print("CAPABILITIES LISTING TESTS")
    print("=" * 60)
    
    mcp = ICSExploitationMCP()
    
    # Test combined capabilities
    result = mcp.list_capabilities()
    print_result("list_capabilities()", result)
    
    assert "protocols" in result, "Should have protocols"
    assert "tool_count" in result, "Should have tool_count"
    
    print(f"\n[INFO] Tool counts:")
    print(f"  OPC-UA: {result['tool_count']['opcua']}")
    print(f"  S7comm: {result['tool_count']['s7comm']}")
    print(f"  General: {result['tool_count']['general']}")
    
    print("[PASS] Capabilities listing")
    return True


def test_documentation():
    """Test documentation retrieval"""
    print("\n" + "=" * 60)
    print("DOCUMENTATION TESTS")
    print("=" * 60)
    
    mcp = ICSExploitationMCP()
    
    # Test general documentation
    result = mcp.get_documentation("general")
    print_result("get_documentation('general')", result)
    assert "overview" in result, "Should have overview"
    
    # Test OPC-UA documentation
    if OPCUA_AVAILABLE:
        result = mcp.get_documentation("opcua")
        print_result("get_documentation('opcua')", result)
        assert "tools" in result, "Should have tools list"
    
    # Test S7 documentation
    if SNAP7_AVAILABLE:
        result = mcp.get_documentation("s7comm")
        print_result("get_documentation('s7comm')", result)
        assert "quick_reference" in result, "Should have quick_reference"
    
    print("[PASS] Documentation retrieval")
    return True


def test_tool_definitions():
    """Test MCP tool definitions"""
    print("\n" + "=" * 60)
    print("TOOL DEFINITIONS TESTS")
    print("=" * 60)
    
    mcp = ICSExploitationMCP()
    
    tools = mcp.get_tools()
    print(f"\n[INFO] Total tools defined: {len(tools)}")
    
    # Group by prefix
    opcua_tools = [t for t in tools if t['function']['name'].startswith('opcua_')]
    s7_tools = [t for t in tools if t['function']['name'].startswith('s7_')]
    ics_tools = [t for t in tools if t['function']['name'].startswith('ics_')]
    
    print(f"  OPC-UA tools: {len(opcua_tools)}")
    print(f"  S7comm tools: {len(s7_tools)}")
    print(f"  General tools: {len(ics_tools)}")
    
    # List all tool names
    print("\n[INFO] Tool names:")
    for tool in tools:
        name = tool['function']['name']
        desc = tool['function']['description'][:50] + "..." if len(tool['function']['description']) > 50 else tool['function']['description']
        print(f"  - {name}: {desc}")
    
    # Validate tool structure
    for tool in tools:
        assert "type" in tool, f"Tool missing type: {tool}"
        assert tool["type"] == "function", f"Tool has wrong type: {tool}"
        assert "function" in tool, f"Tool missing function: {tool}"
        assert "name" in tool["function"], f"Tool missing name: {tool}"
        assert "description" in tool["function"], f"Tool missing description: {tool}"
        assert "parameters" in tool["function"], f"Tool missing parameters: {tool}"
    
    print("[PASS] Tool definitions")
    return True


def test_opcua_toolkit_basic():
    """Test OPC-UA toolkit basic functionality"""
    print("\n" + "=" * 60)
    print("OPC-UA TOOLKIT BASIC TESTS")
    print("=" * 60)
    
    if not OPCUA_AVAILABLE:
        print("[SKIP] OPC-UA not installed")
        return True
    
    mcp = ICSExploitationMCP()
    toolkit = mcp.opcua
    
    # Test check_installation
    result = toolkit.check_installation()
    print_result("opcua.check_installation()", result)
    assert "ready" in result, "Should have ready flag"
    
    # Test list_capabilities
    result = toolkit.list_capabilities()
    print_result("opcua.list_capabilities()", result)
    assert "tools" in result, "Should have tools"
    assert len(result["tools"]) >= 10, "Should have at least 10 tools"
    
    # Test connection status (should be disconnected)
    assert not toolkit.is_connected, "Should not be connected"
    assert toolkit.current_url is None, "Should have no current URL"
    
    # Test disconnect without connection (should not error)
    result = toolkit.disconnect()
    assert result.get("success"), "Disconnect should succeed even when not connected"
    
    print("[PASS] OPC-UA toolkit basic tests")
    return True


def test_snap7_toolkit_basic():
    """Test S7comm toolkit basic functionality"""
    print("\n" + "=" * 60)
    print("S7COMM TOOLKIT BASIC TESTS")
    print("=" * 60)
    
    if not SNAP7_AVAILABLE:
        print("[SKIP] python-snap7 not installed")
        return True
    
    mcp = ICSExploitationMCP()
    toolkit = mcp.s7
    
    # Test check_installation
    result = toolkit.check_installation()
    print_result("s7.check_installation()", result)
    assert "installed" in result, "Should have installed flag"
    
    # Test list_capabilities
    result = toolkit.list_capabilities()
    print_result("s7.list_capabilities()", result)
    assert "tools" in result, "Should have tools"
    assert len(result["tools"]) >= 14, "Should have at least 14 tools"
    
    # Test get_documentation
    result = toolkit.get_documentation("general")
    print_result("s7.get_documentation('general')", result)
    assert "quick_reference" in result, "Should have quick_reference"
    
    # Test connection status (should be disconnected)
    result = toolkit.is_connected()
    assert not result["connected"], "Should not be connected"
    
    # Test disconnect without connection
    result = toolkit.disconnect()
    assert result.get("success"), "Disconnect should succeed"
    
    # Test payload generation
    result = toolkit.generate_payload("all_max", 64)
    print_result("s7.generate_payload('all_max', 64)", result)
    assert result.get("success"), "Should generate payload"
    assert len(result["payload"]) == 128, "Should generate 64 bytes (128 hex chars)"
    assert result["payload"] == "FF" * 64, "Should be all 0xFF"
    
    # Test other patterns
    result = toolkit.generate_payload("all_min", 32)
    assert result["payload"] == "00" * 32, "Should be all 0x00"
    
    result = toolkit.generate_payload("alternating", 8)
    assert result["payload"] == "FF00FF00FF00FF00", "Should alternate (8 bytes = 16 hex chars)"
    
    print("[PASS] S7comm toolkit basic tests")
    return True


def test_error_handling():
    """Test error handling"""
    print("\n" + "=" * 60)
    print("ERROR HANDLING TESTS")
    print("=" * 60)
    
    mcp = ICSExploitationMCP()
    
    # Test OPC-UA operations without connection
    if OPCUA_AVAILABLE:
        result = mcp.opcua.enumerate_nodes()
        print_result("opcua.enumerate_nodes() without connection", result)
        assert "error" in result, "Should return error"
        assert "Not connected" in result["error"], "Should say not connected"
        
        result = mcp.opcua.read_variable("ns=2;i=1")
        assert "error" in result, "Should return error"
        
        result = mcp.opcua.write_variable("ns=2;i=1", "test")
        assert "error" in result, "Should return error"
        
        print("[PASS] OPC-UA error handling")
    
    # Test S7comm operations without connection
    if SNAP7_AVAILABLE:
        result = mcp.s7.db_read(1, 0, 100)
        print_result("s7.db_read() without connection", result)
        assert not result.get("success"), "Should fail"
        assert "Not connected" in result.get("error", ""), "Should say not connected"
        
        result = mcp.s7.db_write(1, 0, "FF00")
        assert not result.get("success"), "Should fail"
        
        result = mcp.s7.get_cpu_info()
        assert not result.get("success"), "Should fail"
        
        print("[PASS] S7comm error handling")
    
    # Test invalid tool call
    import asyncio
    try:
        asyncio.run(mcp.call_tool("invalid_tool_name", {}))
        assert False, "Should raise ValueError"
    except ValueError as e:
        assert "Unknown tool" in str(e), "Should say unknown tool"
        print("[PASS] Invalid tool error handling")
    
    print("[PASS] Error handling tests")
    return True


def test_live_opcua(url: str):
    """Test live OPC-UA connection"""
    print("\n" + "=" * 60)
    print(f"LIVE OPC-UA TESTS - {url}")
    print("=" * 60)
    
    if not OPCUA_AVAILABLE:
        print("[SKIP] OPC-UA not installed")
        return True
    
    mcp = ICSExploitationMCP()
    toolkit = mcp.opcua
    
    # Test endpoint enumeration
    print("\n[TEST] Enumerating endpoints...")
    result = toolkit.enumerate_endpoints(url)
    print_result("enumerate_endpoints()", result)
    
    if "error" in result:
        print(f"[FAIL] Could not connect: {result['error']}")
        return False
    
    print(f"[PASS] Found {result['endpoint_count']} endpoints")
    print(f"[INFO] Security policies: {result['security_policies']}")
    
    # Test certificate generation
    print("\n[TEST] Generating certificate...")
    certs = toolkit.generate_self_signed_cert("./test_certs_opcua")
    print_result("generate_self_signed_cert()", certs)
    
    if "error" in certs:
        print(f"[FAIL] Certificate generation failed")
        return False
    print("[PASS] Certificate generated")
    
    # Test connection
    print("\n[TEST] Connecting...")
    policy = result['security_policies'][0] if result['security_policies'] else "None"
    mode = "SignAndEncrypt" if policy != "None" else "None"
    
    conn_result = toolkit.connect(
        url=url,
        cert_path=certs['cert_path'] if policy != "None" else None,
        key_path=certs['key_path'] if policy != "None" else None,
        security_policy=policy,
        security_mode=mode
    )
    print_result("connect()", conn_result)
    
    if "error" in conn_result:
        print(f"[FAIL] Connection failed: {conn_result['error']}")
        return False
    print("[PASS] Connected")
    
    # Test node enumeration
    print("\n[TEST] Enumerating nodes...")
    nodes = toolkit.enumerate_nodes(max_depth=3)
    print(f"[INFO] Found {nodes.get('total_count', 0)} nodes, {nodes.get('writable_count', 0)} writable")
    
    # Cleanup
    toolkit.disconnect()
    print("[PASS] Disconnected")
    
    print("\n[PASS] All live OPC-UA tests passed")
    return True


def test_live_s7(ip: str, port: int, rack: int = 0, slot: int = 0):
    """Test live S7comm connection"""
    print("\n" + "=" * 60)
    print(f"LIVE S7COMM TESTS - {ip}:{port}")
    print("=" * 60)
    
    if not SNAP7_AVAILABLE:
        print("[SKIP] python-snap7 not installed")
        return True
    
    mcp = ICSExploitationMCP()
    toolkit = mcp.s7
    
    # Test connection
    print("\n[TEST] Connecting...")
    result = toolkit.connect(ip, rack, slot, port)
    print_result("connect()", result)
    
    if not result.get("success"):
        print(f"[FAIL] Connection failed: {result.get('error')}")
        return False
    print(f"[PASS] Connected to {result.get('cpu_type', 'PLC')}")
    
    # Test CPU info
    print("\n[TEST] Getting CPU info...")
    info = toolkit.get_cpu_info()
    print_result("get_cpu_info()", info)
    if info.get("success"):
        print(f"[PASS] CPU: {info.get('module_type')}")
    
    # Test CPU state
    print("\n[TEST] Getting CPU state...")
    state = toolkit.get_cpu_state()
    print_result("get_cpu_state()", state)
    if state.get("success"):
        print(f"[PASS] State: {state.get('state_name')}")
    
    # Test block listing
    print("\n[TEST] Listing blocks...")
    blocks = toolkit.list_blocks()
    print_result("list_blocks()", blocks)
    if blocks.get("success"):
        print(f"[PASS] DB count: {blocks['blocks'].get('DB', 0)}")
    
    # Test DB read
    print("\n[TEST] Reading DB1...")
    data = toolkit.db_read(1, 0, 64)
    if data.get("success"):
        print(f"[PASS] Read {data['size']} bytes, {data['non_zero_count']} non-zero")
    else:
        print(f"[INFO] DB1 read: {data.get('error', 'failed')}")
    
    # Cleanup
    toolkit.disconnect()
    print("\n[PASS] Disconnected")
    
    print("\n[PASS] All live S7comm tests passed")
    return True


def main():
    parser = argparse.ArgumentParser(description="ICS Exploitation MCP Test Suite")
    parser.add_argument("--live-opcua", action="store_true", help="Run live OPC-UA tests")
    parser.add_argument("--live-s7", action="store_true", help="Run live S7 tests")
    parser.add_argument("--all", action="store_true", help="Run all tests including live")
    parser.add_argument("--opcua-url", type=str, default="opc.tcp://localhost:4840", help="OPC-UA target URL")
    parser.add_argument("--s7-ip", type=str, default="127.0.0.1", help="S7 target IP")
    parser.add_argument("--s7-port", type=int, default=102, help="S7 target port")
    parser.add_argument("--s7-rack", type=int, default=0, help="S7 rack")
    parser.add_argument("--s7-slot", type=int, default=0, help="S7 slot")
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("ICS EXPLOITATION MCP TEST SUITE")
    print("=" * 60)
    
    # Always run basic tests
    test_mcp_initialization()
    test_installation_check()
    test_capabilities_listing()
    test_documentation()
    test_tool_definitions()
    test_opcua_toolkit_basic()
    test_snap7_toolkit_basic()
    test_error_handling()
    
    # Live tests
    if args.live_opcua or args.all:
        test_live_opcua(args.opcua_url)
    
    if args.live_s7 or args.all:
        test_live_s7(args.s7_ip, args.s7_port, args.s7_rack, args.s7_slot)
    
    print("\n" + "=" * 60)
    print("ALL TESTS COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()
