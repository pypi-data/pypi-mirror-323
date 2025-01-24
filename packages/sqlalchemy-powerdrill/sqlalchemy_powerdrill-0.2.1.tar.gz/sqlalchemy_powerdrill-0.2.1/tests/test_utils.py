"""Test utils module."""
import pytest
from powerdrill.utils import parse_and_check_json_markdown

def test_parse_and_check_json_markdown_simple():
    """Test parsing a simple JSON object."""
    markdown_text = '''
Some text before

```json
{
    "columns": [
        {"name": "city", "type": "string"},
        {"name": "code", "type": "string"}
    ],
    "rows": [
        ["Beijing", "010"],
        ["Shanghai", "021"]
    ]
}
```

Some text after
'''
    expected_keys = ['columns', 'rows']
    result = parse_and_check_json_markdown(markdown_text, expected_keys)
    
    assert 'columns' in result
    assert 'rows' in result
    assert len(result['columns']) == 2
    assert len(result['rows']) == 2
    assert result['columns'][0]['name'] == 'city'
    assert result['rows'][0][0] == 'Beijing'

def test_parse_and_check_json_markdown_multiple_blocks():
    """Test parsing multiple JSON blocks."""
    markdown_text = '''
First block:
```json
{
    "test": "data"
}
```

Second block:
```json
{
    "columns": [
        {"name": "city", "type": "string"}
    ],
    "rows": [
        ["Beijing"]
    ]
}
```
'''
    expected_keys = ['columns', 'rows']
    result = parse_and_check_json_markdown(markdown_text, expected_keys)
    
    assert 'columns' in result
    assert 'rows' in result
    assert len(result['columns']) == 1
    assert len(result['rows']) == 1

def test_parse_and_check_json_markdown_missing_keys():
    """Test parsing JSON with missing required keys."""
    markdown_text = '''
```json
{
    "test": "data"
}
```
'''
    expected_keys = ['columns', 'rows']
    
    with pytest.raises(ValueError, match="No JSON object found containing all expected keys"):
        parse_and_check_json_markdown(markdown_text, expected_keys)

def test_parse_and_check_json_markdown_invalid_json():
    """Test parsing invalid JSON."""
    markdown_text = '''
```json
{
    "test": "data",
    invalid json here
}
```
'''
    expected_keys = ['test']
    
    with pytest.raises(ValueError, match="No JSON object found containing all expected keys"):
        parse_and_check_json_markdown(markdown_text, expected_keys)

def test_parse_and_check_json_markdown_no_blocks():
    """Test parsing text with no JSON blocks."""
    markdown_text = "Just some text without any JSON blocks"
    expected_keys = ['test']
    
    with pytest.raises(ValueError, match="No JSON object found containing all expected keys"):
        parse_and_check_json_markdown(markdown_text, expected_keys)
