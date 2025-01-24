# Chinese-Holidays MCP server

Query information about Chinese holidays

### Tools

1. `get-all-holidays`: Get all holidays for a year
2. `is-holiday`: Check if a date is a holiday

## Quickstart

### Install

#### Claude Desktop

On MacOS: `~/Library/Application\ Support/Claude/claude_desktop_config.json`
On Windows: `%APPDATA%/Claude/claude_desktop_config.json`

* Development/Unpublished Servers Configuration

  ```json
  {
    "mcpServers": {
      "chinese-holidays": {
        "command": "uv",
        "args": [
          "--directory",
          "the absolute path of chinese-holidays",
          "run",
          "chinese-holidays"
        ]
      }
    }
  }
  ```

* Published Servers Configuration

  ```json
  {
    "mcpServers": {
      "chinese-holidays": {
        "command": "uvx",
        "args": [
          "chinese-holidays"
        ],
        "env": {
          "PYTHONIOENCODING": "utf-8"
        }
      }
    }
  }
  ```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
