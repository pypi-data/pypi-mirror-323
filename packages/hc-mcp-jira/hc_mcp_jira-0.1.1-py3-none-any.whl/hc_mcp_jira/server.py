import asyncio
import os
from typing import Optional

from jira import JIRA
from mcp.server.models import InitializationOptions
import mcp.types as types
from mcp.server import NotificationOptions, Server
import mcp.server.stdio

# Initialize Jira client
JIRA_URL = os.getenv("JIRA_URL")
JIRA_USERNAME = os.getenv("JIRA_USERNAME")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")

if not all([JIRA_URL, JIRA_USERNAME, JIRA_API_TOKEN]):
    raise ValueError("Missing required Jira environment variables")

jira_client = JIRA(
    server=JIRA_URL,
    basic_auth=(JIRA_USERNAME, JIRA_API_TOKEN)
)

server = Server("hc-mcp-jira")

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """List available Jira tools."""
    return [
        types.Tool(
            name="get_current_user",
            description="Get information about the currently authenticated user",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        types.Tool(
            name="create_issue",
            description="Create a new Jira issue",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_key": {"type": "string", "description": "Project key where the issue will be created"},
                    "summary": {"type": "string", "description": "Issue summary/title"},
                    "description": {"type": "string", "description": "Issue description"},
                    "issue_type": {"type": "string", "description": "Type of issue (e.g., 'Bug', 'Task', 'Story')"},
                    "priority": {"type": "string", "description": "Issue priority"},
                    "assignee": {"type": "string", "description": "Account ID of the assignee"},
                    "parent_key": {"type": "string", "description": "Parent issue key for subtasks"},
                },
                "required": ["project_key", "summary", "issue_type"],
            },
        ),
        types.Tool(
            name="update_issue",
            description="Update an existing Jira issue",
            inputSchema={
                "type": "object",
                "properties": {
                    "issue_key": {"type": "string", "description": "Key of the issue to update"},
                    "summary": {"type": "string", "description": "New summary/title"},
                    "description": {"type": "string", "description": "New description"},
                    "status": {"type": "string", "description": "New status"},
                    "priority": {"type": "string", "description": "New priority"},
                    "assignee": {"type": "string", "description": "Account ID of the assignee"},
                    "sprint": {"type": "string", "description": "Sprint name to move the issue to"},
                },
                "required": ["issue_key"],
            },
        ),
        types.Tool(
            name="get_issue",
            description="Get complete issue details",
            inputSchema={
                "type": "object",
                "properties": {
                    "issue_key": {"type": "string", "description": "Issue key (e.g., PROJ-123)"},
                },
                "required": ["issue_key"],
            },
        ),
        types.Tool(
            name="search_issues",
            description="Search for issues in a project using JQL",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_key": {"type": "string", "description": "Project key to search in"},
                    "jql": {"type": "string", "description": "JQL filter statement"},
                },
                "required": ["project_key", "jql"],
            },
        ),
        types.Tool(
            name="add_comment",
            description="Add a comment to a Jira issue",
            inputSchema={
                "type": "object",
                "properties": {
                    "issue_key": {"type": "string", "description": "Key of the issue to comment on"},
                    "comment": {"type": "string", "description": "Comment text content"},
                },
                "required": ["issue_key", "comment"],
            },
        ),
        types.Tool(
            name="list_projects",
            description="List all accessible Jira projects",
            inputSchema={
                "type": "object",
                "properties": {
                    "max_results": {"type": "integer", "description": "Maximum number of projects to return"},
                },
            },
        ),
        types.Tool(
            name="delete_issue",
            description="Delete a Jira issue",
            inputSchema={
                "type": "object",
                "properties": {
                    "issue_key": {"type": "string", "description": "Key of the issue to delete"},
                },
                "required": ["issue_key"],
            },
        ),
        types.Tool(
            name="create_issue_link",
            description="Create a link between two issues",
            inputSchema={
                "type": "object",
                "properties": {
                    "inward_issue": {"type": "string", "description": "Key of the inward issue"},
                    "outward_issue": {"type": "string", "description": "Key of the outward issue"},
                    "link_type": {"type": "string", "description": "Type of link (e.g., 'blocks')"},
                },
                "required": ["inward_issue", "outward_issue", "link_type"],
            },
        ),
    ]

@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """Handle Jira tool execution requests."""
    if not arguments and name != "get_current_user" and name != "list_projects":
        raise ValueError("Missing arguments")

    try:
        if name == "get_current_user":
            user = jira_client.current_user()
            return [types.TextContent(type="text", text=str(user))]

        elif name == "create_issue":
            fields = {
                "project": {"key": arguments["project_key"]},
                "summary": arguments["summary"],
                "issuetype": {"name": arguments["issue_type"]},
            }
            
            if "description" in arguments:
                fields["description"] = arguments["description"]
            if "priority" in arguments:
                fields["priority"] = {"name": arguments["priority"]}
            if "assignee" in arguments:
                fields["assignee"] = {"accountId": arguments["assignee"]}
            if "parent_key" in arguments:
                fields["parent"] = {"key": arguments["parent_key"]}

            issue = jira_client.create_issue(fields=fields)
            return [types.TextContent(type="text", text=f"Created issue: {issue.key}")]

        elif name == "update_issue":
            issue = jira_client.issue(arguments["issue_key"])
            update_fields = {}

            if "summary" in arguments:
                update_fields["summary"] = arguments["summary"]
            if "description" in arguments:
                update_fields["description"] = arguments["description"]
            if "priority" in arguments:
                update_fields["priority"] = {"name": arguments["priority"]}
            if "assignee" in arguments:
                update_fields["assignee"] = {"accountId": arguments["assignee"]}

            if update_fields:
                issue.update(fields=update_fields)

            if "status" in arguments:
                transitions = jira_client.transitions(issue)
                for t in transitions:
                    if t["name"].lower() == arguments["status"].lower():
                        jira_client.transition_issue(issue, t["id"])
                        break

            return [types.TextContent(type="text", text=f"Updated issue: {issue.key}")]

        elif name == "get_issue":
            issue = jira_client.issue(arguments["issue_key"])
            return [types.TextContent(type="text", text=str(issue.raw))]

        elif name == "search_issues":
            jql = f"project = {arguments['project_key']} AND {arguments['jql']}"
            issues = jira_client.search_issues(jql)
            return [types.TextContent(type="text", text=str([i.key for i in issues]))]

        elif name == "add_comment":
            issue = jira_client.issue(arguments["issue_key"])
            comment = jira_client.add_comment(issue, arguments["comment"])
            return [types.TextContent(type="text", text=f"Added comment: {comment.id}")]

        elif name == "list_projects":
            max_results = arguments.get("max_results", 50) if arguments else 50
            projects = jira_client.projects()
            project_list = [{"key": p.key, "name": p.name} for p in projects[:max_results]]
            return [types.TextContent(type="text", text=str(project_list))]

        elif name == "delete_issue":
            issue = jira_client.issue(arguments["issue_key"])
            issue.delete()
            return [types.TextContent(type="text", text=f"Deleted issue: {arguments['issue_key']}")]

        elif name == "create_issue_link":
            jira_client.create_issue_link(
                type=arguments["link_type"],
                inwardIssue=arguments["inward_issue"],
                outwardIssue=arguments["outward_issue"]
            )
            return [types.TextContent(
                type="text",
                text=f"Created {arguments['link_type']} link between {arguments['inward_issue']} and {arguments['outward_issue']}"
            )]

        else:
            raise ValueError(f"Unknown tool: {name}")

    except Exception as e:
        return [types.TextContent(type="text", text=f"Error: {str(e)}")]

async def main():
    # Run the server using stdin/stdout streams
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="hc-mcp-jira",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )
