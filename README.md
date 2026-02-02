# ICS Exploitation MCP

An **MCP (Model Context Protocol) server** that gives AI assistants (like Cursor or Claude) the ability to interact with Industrial Control Systems (ICS) for security assessment. Instead of writing Python scripts, you can just ask your AI assistant to "scan the OPC-UA server" or "connect to the Siemens PLC" and it will use these tools automatically.

## What is This?

This is an **MCP server** - think of it as a plugin that adds 56 specialized tools to your AI assistant. Once configured, you can have conversations like:

- "Connect to the OPC-UA server at 192.168.1.100 and find all writable variables"
- "Scan the Siemens S7 PLC and map which memory offsets control which equipment"
- "Perform a sustained attack on the BACnet system to bypass thermostat resets"

The AI assistant uses these tools automatically - no Python coding required.

## Quick Setup (MCP Server Mode)

### 1. Install Dependencies

```bash
git clone https://github.com/0xhackerfren/ICS-Explotation-MCP.git
cd ICS-Explotation-MCP
pip install -r requirements.txt
```

### 2. Configure Cursor IDE

Add to `.cursor/mcp.json` (create it if it doesn't exist):

```json
{
  "mcpServers": {
    "ics-exploitation": {
      "command": "python",
      "args": ["D:/MCP's/ICS-Explotation-MCP/ics_exploitation_mcp.py"]
    }
  }
}
```

**Important**: Update the path to match your actual installation location.

### 3. Restart Cursor

Restart Cursor IDE completely. The MCP server will load automatically.

### 4. Use It!

Now you can ask your AI assistant things like:
- "What ICS protocols are available?"
- "Connect to the OPC-UA server at opc.tcp://192.168.1.100:4840"
- "List all available tools for S7comm"

The AI will automatically use the appropriate tools from this MCP server.

### Alternative: Claude Desktop

Add to `claude_desktop_config.json`:

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

## Supported Protocols

| Protocol | What It's For | Example Targets |
|----------|---------------|-----------------|
| **OPC-UA** | Universal PLC communication | Siemens, ABB, Rockwell PLCs, SCADA systems |
| **S7comm** | Siemens-specific PLCs | S7-300/400/1200/1500 series |
| **BACnet** | Building automation | HVAC systems, lighting, access control |
| **Modbus** | Generic industrial devices | Water systems, power grids, sensors |
| **EtherNet/IP** | Allen-Bradley/Rockwell | Industrial automation controllers |

## What Can It Do?

### OPC-UA Tools (9 tools)
- Discover server security requirements
- Generate certificates for trust list bypass
- Enumerate nodes and find writable variables
- Read/write PLC variables

### S7comm Tools (17 tools)
- Connect to Siemens PLCs
- Read/write data blocks
- Memory area operations
- Sustained attack mode (maintains faults even when system resets)
- Memory mapping to correlate offsets with equipment effects

### BACnet Tools (9 tools)
- Connect to building automation systems
- List/enumerate objects (thermostats, sensors, alarms)
- Persistent write attacks (bypasses auto-reset)
- Alarm threshold manipulation

### Modbus Tools (10 tools)
- Connect to Modbus devices
- Read/write coils and registers
- Raw command injection
- Coil scanning for attack surface discovery

### EtherNet/IP Tools (8 tools)
- Connect to Allen-Bradley controllers
- Read/write tags by name
- CIP object enumeration
- Device identity retrieval

**Total: 56 tools** available to your AI assistant.

## Example Usage (via AI Assistant)

Once configured, you can have conversations like:

```
You: Connect to the OPC-UA server at opc.tcp://192.168.1.100:4840 and 
     enumerate all endpoints to see what security policies it supports.

AI: [Uses opcua_enumerate_endpoints tool]
    The server supports Basic256Sha256, Basic256, and None security policies.
    Recommendation: Use Basic256Sha256 with SignAndEncrypt mode.

You: Generate a self-signed certificate and connect with encryption.

AI: [Uses opcua_generate_cert, then opcua_connect]
    Connected successfully. Certificate generated at ./certs/client_cert.pem

You: Find all writable variables that might be interesting for exploitation.

AI: [Uses opcua_find_writable]
    Found 23 writable variables. Here are the most interesting ones...
```

## Installation Requirements

### Core
- Python 3.8+
- `mcp` library (for MCP server mode)

### Protocol-Specific (Optional)
Install only what you need:

```bash
# OPC-UA support
pip install opcua cryptography

# S7comm support (Siemens)
pip install python-snap7

# EtherNet/IP support (Allen-Bradley)
pip install pycomm3

# Status monitoring (for sustained attacks)
pip install requests
```

Or install everything:
```bash
pip install -r requirements.txt
```

## Example Scripts

The `examples/` directory contains Python scripts that demonstrate how the underlying toolkits work. These are for reference/testing purposes only - the primary way to use this project is via the MCP server with your AI assistant.

## Documentation

- **[commands.md](commands.md)** - Complete reference for all 56 tools with parameters
- **[SKILL.md](SKILL.md)** - Step-by-step workflows for common attack patterns
- **[rules.mdc](rules.mdc)** - Cursor rule file for AI agent guidance

## Troubleshooting

**MCP server not loading?**
- Check the path in `mcp.json` is correct
- Make sure Python is in your PATH
- Restart Cursor completely (not just reload window)
- Check that `mcp` library is installed: `pip install mcp`

**Protocol not available?**
- Install the required library (e.g., `pip install opcua` for OPC-UA)
- Use `ics_check_installation` tool to see what's installed

**Connection issues?**
- Verify network connectivity to target
- Check firewall settings
- Some systems use non-standard ports (especially S7comm)

## Security & Ethics

⚠️ **WARNING**: This toolkit is for **authorized security testing only**.

- Only use on systems you own or have explicit written permission to test
- Unauthorized access to industrial control systems is illegal
- Misuse can cause physical damage or safety hazards

Intended for:
- Authorized penetration testing
- Security competitions and exercises  
- Security research
- Educational purposes

## License

MIT License - See [LICENSE](LICENSE) file.

## Credits

Built on:
- [python-opcua](https://github.com/FreeOpcUa/python-opcua) - OPC-UA protocol
- [python-snap7](https://github.com/gijzelaerr/python-snap7) - S7comm protocol
- [pycomm3](https://github.com/ottowayi/pycomm3) - EtherNet/IP protocol
- [MCP](https://github.com/anthropics/mcp) - Model Context Protocol
