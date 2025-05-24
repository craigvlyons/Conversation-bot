import html
import re
from typing import Dict


class DevOpsWorkItemFormatter:
    @staticmethod
    def strip_html(html_text: str) -> str:
        """Remove HTML tags and decode HTML entities."""
        if not html_text:
            return ""
        # Decode HTML entities like &nbsp;, &gt;, etc.
        text = html.unescape(html_text)
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        # Normalize whitespace
        return re.sub(r'\s+', ' ', text).strip()

    @staticmethod
    def format(work_item: Dict) -> str:
        fields = work_item.get('fields', {})
        id_ = work_item.get('id', 'Unknown ID')
        title = fields.get('System.Title', 'No Title')
        state = fields.get('System.State', 'Unknown State')
        assigned_to = fields.get('System.AssignedTo', {}).get('displayName', 'Unassigned')
        created_date = fields.get('System.CreatedDate', 'Unknown')
        description = DevOpsWorkItemFormatter.strip_html(fields.get('System.Description', ''))
        url = work_item.get('url', '')

        return (
            f"Work Item ID: {id_}\n"
            f"Title: {title}\n"
            f"State: {state}\n"
            f"Assigned To: {assigned_to}\n"
            f"Created: {created_date}\n"
            f"URL: {url}\n"
            f"Description:\n{description}\n"
            f"{'-'*60}\n"
        )
