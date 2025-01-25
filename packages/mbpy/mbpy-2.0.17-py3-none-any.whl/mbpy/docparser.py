import re
from typing import List, Dict

class Node:
    def __init__(self, type: str, content: str):
        self.type = type
        self.content = content
        self.children = []

    def to_dict(self) -> Dict:
        """Convert the node to a dictionary."""
        result = {"type": self.type, "content": self.content}
        if self.children:
            result["children"] = [child.to_dict() for child in self.children]
        return result


class UniversalParserIndentAware:
    def __init__(self):
        self.root = Node("root", "root")
        self.stack = [self.root]

    def get_indent(self, line: str) -> int:
        """Calculate the indentation level of a line."""
        return len(line) - len(line.lstrip())

    def classify_line(self, line: str) -> str:
        """Classify a line based on its content."""
        stripped = line.lstrip()

        # Markdown-like headings
        if stripped.startswith("#"):
            return "heading"

        # Bulleted or numbered list items
        if re.match(r"^([-*+]|[0-9]+\.)\s", stripped):
            return "list_item"

        # Uppercase section names
        if stripped.isupper() and len(stripped.split()) < 10:
            return "section"

        # Plain text
        if stripped:
            return "text"

        return "empty"

    def parse(self, text: str) -> Dict:
        """Parse the text into a hierarchical structure."""
        lines = text.splitlines()

        for line in lines:
            if not line.strip():
                continue  # Skip empty lines

            indent = self.get_indent(line)
            line_type = self.classify_line(line)
            node = Node(line_type, line.strip())

            # Adjust stack based on indentation
            while len(self.stack) > 1 and self.get_indent(self.stack[-1].content) >= indent:
                self.stack.pop()

            # Append node as child or sibling based on indentation
            if self.stack and indent > self.get_indent(self.stack[-1].content):
                self.stack[-1].children.append(node)
            elif self.stack:
                self.stack[-1].children.append(node)

            # Push the node to stack for further nesting
            self.stack.append(node)

        return self.root.to_dict()