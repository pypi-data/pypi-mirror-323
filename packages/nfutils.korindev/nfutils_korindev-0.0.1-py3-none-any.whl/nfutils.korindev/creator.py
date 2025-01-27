import re

class NFFormatter:
    def __init__(self):
        self.indent = 4  # Number of spaces for indentation

    def _format_value(self, value):
        """Format a Python value into its NFormat representation."""
        if isinstance(value, bool):
            return "true" if value else "false"
        elif isinstance(value, (int, float)):
            return str(value)
        elif isinstance(value, str):
            return f'"{value}"'  # Add quotes for strings
        elif isinstance(value, list):
            return value  # Lists will be processed separately
        else:
            raise ValueError(f"Unsupported value type: {type(value)}")

    def _write_block(self, key, value, level):
        """Recursively format a block."""
        indent = " " * (self.indent * level)
        lines = []

        if isinstance(value, dict):
            lines.append(f"{indent}{key}->")
            for sub_key, sub_value in value.items():
                lines.extend(self._write_block(sub_key, sub_value, level + 1))
        elif isinstance(value, list):
            lines.append(f"{indent}{key}->")
            for item in value:
                if isinstance(item, (dict, list)):  # Nested structures
                    lines.extend(self._write_block("-", item, level + 1))
                else:
                    formatted_item = self._format_value(item)
                    lines.append(f"{indent}{' ' * self.indent}- {formatted_item}")
        else:
            formatted_value = self._format_value(value)
            lines.append(f"{indent}{key}::{formatted_value}")

        return lines

    def create(self, data):
        """Convert a Python dictionary into an NFormat string."""
        if not isinstance(data, dict):
            raise ValueError("Input data must be a dictionary.")
        lines = []
        for key, value in data.items():
            lines.extend(self._write_block(key, value, level=0))
        return "\n".join(lines)

# Convenience function for creating NFormat files
def create_nformat(data):
    """Create an NFormat string from a dictionary."""
    formatter = NFFormatter()
    return formatter.create(data)