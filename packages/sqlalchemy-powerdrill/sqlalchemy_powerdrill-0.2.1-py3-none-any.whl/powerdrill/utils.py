"""Utility functions for PowerDrill SQLAlchemy dialect."""
from typing import List
from sqlalchemy import types
import json

def mysql_to_sqlalchemy_type(mysql_type):
    """Convert MySQL type string to SQLAlchemy type.
    
    Args:
        mysql_type (str): MySQL type string (e.g., 'varchar(255)', 'int', 'datetime')
        
    Returns:
        sqlalchemy.types.TypeEngine: Corresponding SQLAlchemy type
    """
    # Extract base type and parameters
    base_type = mysql_type.lower().split('(')[0].strip()
    
    # String types
    if base_type in ('char', 'varchar', 'text', 'tinytext', 'mediumtext', 'longtext'):
        if '(' in mysql_type:
            length = int(mysql_type.split('(')[1].split(')')[0])
            return types.String(length=length)
        return types.Text
        
    # Numeric types
    if base_type in ('tinyint', 'smallint', 'mediumint', 'int', 'integer'):
        return types.Integer
    if base_type == 'bigint':
        return types.BigInteger
    if base_type == 'float':
        return types.Float
    if base_type in ('double', 'real'):
        return types.Float(precision=53)
    if base_type == 'decimal':
        if '(' in mysql_type:
            precision, scale = map(int, mysql_type.split('(')[1].split(')')[0].split(','))
            return types.Numeric(precision=precision, scale=scale)
        return types.Numeric
        
    # Date and Time types
    if base_type == 'date':
        return types.Date
    if base_type == 'datetime':
        return types.DateTime
    if base_type == 'timestamp':
        return types.TIMESTAMP
    if base_type == 'time':
        return types.Time
    if base_type == 'year':
        return types.Integer
        
    # Binary types
    if base_type in ('binary', 'varbinary'):
        if '(' in mysql_type:
            length = int(mysql_type.split('(')[1].split(')')[0])
            return types.Binary(length=length)
        return types.Binary
    if base_type in ('tinyblob', 'blob', 'mediumblob', 'longblob'):
        return types.LargeBinary
        
    # Boolean type
    if base_type == 'boolean' or base_type == 'bool':
        return types.Boolean
        
    # Enum type
    if base_type == 'enum':
        # Extract enum values
        values = mysql_type.split('(')[1].split(')')[0].split(',')
        values = [v.strip().strip("'").strip('"') for v in values]
        return types.Enum(*values)
        
    # JSON type
    if base_type == 'json':
        return types.JSON
        
    # Default to Text for unknown types
    return types.Text


def parse_and_check_json_markdown(text: str, expected_keys: List[str]) -> dict:
    """Parse JSON objects from markdown text and check for expected keys.
    
    Args:
        text: Markdown text containing JSON objects between ```json blocks
        expected_keys: List of keys that must be present in the JSON object
        
    Returns:
        The last JSON object that contains all expected keys
        
    Raises:
        ValueError: If no JSON object contains all expected keys
    """
    json_blocks = []
    current_block = []
    in_json_block = False
    
    # Split text into lines
    lines = text.split('\n')
    
    # Extract JSON blocks
    for line in lines:
        if line.strip() == '```json':
            in_json_block = True
            current_block = []
        elif line.strip() == '```' and in_json_block:
            in_json_block = False
            if current_block:
                json_blocks.append('\n'.join(current_block))
        elif in_json_block:
            current_block.append(line)
    
    # If we're still in a JSON block at the end, add the final block
    if in_json_block and current_block:
        json_blocks.append('\n'.join(current_block))
    
    # Parse and check each JSON block
    def parse_json(json_str):
        return json.loads(json_str)
    
    last_valid_json = None
    for json_str in json_blocks:
        try:
            json_obj = parse_json(json_str)
            # Check if all expected keys are present
            if all(key in json_obj for key in expected_keys):
                last_valid_json = json_obj
        except ValueError:
            continue
    
    if last_valid_json is None:
        raise ValueError("No JSON object found containing all expected keys")
    
    return last_valid_json