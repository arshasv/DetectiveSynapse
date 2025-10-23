import json
import re
from typing import Optional


class JSONCleaner:
    """Utility class for cleaning and validating JSON content"""

    @staticmethod
    def clean_json_content(raw_content: str) -> str:
        """
        Extract valid JSON object from raw LLM output, removing instructions, explanations,
        markdown code fences, and whitespace.
        """
        # Remove markdown fences
        content = re.sub(r'```json', '', raw_content, flags=re.IGNORECASE)
        content = re.sub(r'```', '', content)

        # Try to find JSON object by matching braces
        match = re.search(r'(\{.*\}|\[.*\])', content, flags=re.DOTALL)
        if not match:
            # fallback: return stripped content if no JSON found
            return content.strip()

        json_str = match.group(0).strip()

        # Try parsing to validate JSON
        try:
            parsed_json = json.loads(json_str)
            # return pretty-printed JSON
            return json.dumps(parsed_json, indent=2)
        except json.JSONDecodeError:
            # fallback: return what we extracted
            return json_str

    @staticmethod
    def is_valid_json(content: str) -> bool:
        """Check if the content is valid JSON"""
        try:
            json.loads(content)
            return True
        except json.JSONDecodeError:
            return False

    @staticmethod
    def format_json(content: str, indent: int = 2) -> Optional[str]:
        """Format JSON content with specified indentation"""
        try:
            parsed_json = json.loads(content)
            return json.dumps(parsed_json, indent=indent)
        except json.JSONDecodeError:
            return None
