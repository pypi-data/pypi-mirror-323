# hc-mcp-jira MCP server

MCP server for Jira integration, providing tools to interact with Jira through Cline.

## Features

The server provides the following Jira integration tools:

- `get_current_user`: Get information about the currently authenticated user
- `create_issue`: Create a new Jira issue with customizable fields
- `update_issue`: Update an existing Jira issue's fields and status
- `get_issue`: Get complete issue details
- `search_issues`: Search for issues in a project using JQL
- `add_comment`: Add a comment to a Jira issue
- `list_projects`: List all accessible Jira projects
- `delete_issue`: Delete a Jira issue
- `create_issue_link`: Create a link between two issues

## Installation

The package is available on PyPI and can be installed using:

```bash
pip install hc-mcp-jira
```

## Configuration

The server requires the following environment variables:

- `JIRA_URL`: Your Jira instance URL (e.g., "https://your-domain.atlassian.net")
- `JIRA_USERNAME`: Your Jira username/email
- `JIRA_API_TOKEN`: Your Jira API token

### Claude Desktop Configuration

Add the following to your Claude Desktop configuration file:

On MacOS: `~/Library/Application\ Support/Claude/claude_desktop_config.json`
On Windows: `%APPDATA%/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "hc-mcp-jira": {
      "command": "uvx",
      "args": [
        "hc-mcp-jira"
      ],
      "env": {
        "JIRA_URL": "your-jira-url",
        "JIRA_USERNAME": "your-username",
        "JIRA_API_TOKEN": "your-api-token"
      }
    }
  }
}
```

## Development

### Building and Publishing

1. Clean previous builds:
```bash
make clean
```

2. Build and publish to PyPI:
```bash
make all
```

### Debugging

Since MCP servers run over stdio, debugging can be challenging. For the best debugging
experience, we strongly recommend using the [MCP Inspector](https://github.com/modelcontextprotocol/inspector).

You can launch the MCP Inspector via [`npm`](https://docs.npmjs.com/downloading-and-installing-node-js-and-npm) with this command:

```bash
npx @modelcontextprotocol/inspector uvx hc-mcp-jira
```

Upon launching, the Inspector will display a URL that you can access in your browser to begin debugging.

## Example Usage

Here are some example tasks you can ask Cline to perform using this MCP server:

1. Create a new issue:
   "Create a Jira issue in project KEY with title 'Implement feature X' and type 'Task'"

2. Search for issues:
   "Find all open bugs in project KEY"

3. Update an issue:
   "Update issue KEY-123 to add the comment 'Work in progress'"

4. Link issues:
   "Create a 'blocks' link between KEY-123 and KEY-456"
