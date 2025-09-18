import json
import re
from typing import Optional


class JSONCleaner:
    """Utility class for cleaning and validating JSON content"""
    
    @staticmethod
    def clean_json_content(raw_content: str) -> str:
        """Clean the raw content by removing markdown code blocks and extracting valid JSON"""
        # Remove markdown code block syntax
        content = re.sub(r'^```json\s*', '', raw_content, flags=re.MULTILINE)
        content = re.sub(r'^```\s*$', '', content, flags=re.MULTILINE)
        
        # Try to parse and reformat as valid JSON to ensure it's clean
        try:
            parsed_json = json.loads(content.strip())
            return json.dumps(parsed_json, indent=2)
        except json.JSONDecodeError:
            # If parsing fails, return the cleaned content as-is
            return content.strip()
    
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
