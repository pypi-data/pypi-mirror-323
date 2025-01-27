import re
from .exceptions import InvalidFormatError

class NFParser:
    def __init__(self):
        self.comment_pattern = re.compile(r'^\s*-#.*?-#\s*$')  # Matches full-line comments

    def _strip_comments(self, text):
        """Remove full-line comments from the input text."""
        return '\n'.join(
            line for line in text.splitlines() if not self.comment_pattern.match(line)
        )

    def _parse_value(self, value):
        """Parse a value into its appropriate type."""
        value = value.strip()
        if value.lower() == 'true':
            return True
        elif value.lower() == 'false':
            return False
        try:
            # Attempt to parse as integer or float
            if '.' in value:
                return float(value)
            return int(value)
        except ValueError:
            # Fallback to string (strip surrounding quotes if present)
            return value.strip('"')

    def _parse_line(self, line):
        """Parse a single line into a key-value pair."""
        if '::' not in line:
            raise InvalidFormatError(f"Invalid line format: {line}")
        key, value = map(str.strip, line.split('::', 1))
        return key, self._parse_value(value)

    def _parse_block(self, lines, index, indent_level):
        """Recursively parse a block starting at the given index."""
        block = {}
        while index < len(lines):
            line = lines[index]
            stripped_line = line.lstrip()
            current_indent = len(line) - len(stripped_line)

            if current_indent < indent_level:  # Block ends when indentation decreases
                break
            elif not stripped_line:  # Skip empty lines
                index += 1
                continue

            if '::' in stripped_line:
                key, value = self._parse_line(stripped_line)
                block[key] = value
            elif '->' in stripped_line:
                key = stripped_line.split('->')[0].strip()
                sub_block, index = self._parse_block(lines, index + 1, current_indent + 1)
                block[key] = sub_block
            else:
                raise InvalidFormatError(f"Invalid line format: {line}")

            index += 1

        return block, index

    def parse(self, text):
        """Parse the entire text into a dictionary."""
        text = self._strip_comments(text)
        lines = text.splitlines()
        result, _ = self._parse_block(lines, 0, 0)  # Start parsing with initial indentation 0
        return result

# Convenience function for parsing .nformat files
def parse_nformat(text):
    """Parse a generic NFormat file into a dictionary."""
    parser = NFParser()
    return parser.parse(text)
