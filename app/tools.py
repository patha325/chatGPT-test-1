from typing import Any, List, Dict


def get_tools() -> List[Dict[str, Any]]:
    return [
        {
            "type": "function",
            "function": {
                "name": "search_gmail",
                "description": "Search the user's Gmail with Gmail search syntax and return matching message snippets.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": (
                                "Gmail search query, e.g. "
                                "'from:alice@example.com subject:\"pipeline\" newer_than:7d'."
                            ),
                        },
                        "max_results": {
                            "type": "integer",
                            "description": "Maximum number of messages to return (default 10).",
                            "default": 10,
                        },
                    },
                    "required": ["query"],
                },
            },
        },
    ]
