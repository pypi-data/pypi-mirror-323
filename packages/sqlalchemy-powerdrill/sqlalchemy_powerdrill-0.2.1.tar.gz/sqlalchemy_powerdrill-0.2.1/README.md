# PowerDrill SQLAlchemy Dialect

SQLAlchemy dialect for PowerDrill AI, enabling natural language queries through SQLAlchemy's ORM interface. This dialect allows you to interact with PowerDrill's AI-powered data analysis capabilities using familiar SQLAlchemy patterns.

## Installation

```bash
pip install sqlalchemy-powerdrill
```

## Quick Start

```python
from sqlalchemy import create_engine, text, inspect

# Create engine with credentials
engine = create_engine(
    'powerdrill://ai.data.cloud'
    '?api_key=your-api-key'
    '&user_id=your-user-id'
    '&dataset_id=your-dataset-id'
)

# Execute natural language queries
with engine.connect() as connection:
    # Natural language query
    result = connection.execute(text("四个直辖市的全称、区号"))
    for row in result:
        print(row)
    
    # List available datasets
    inspector = inspect(engine)
    datasets = inspector.get_schema_names()
    print("Available datasets:", datasets)
```

## Features

- **Natural Language Queries**: Write queries in natural language
- **Dataset Management**: List and explore available datasets
- **SQLAlchemy Integration**: Seamless integration with SQLAlchemy ORM patterns
- **Streaming Support**: Handle large result sets efficiently
- **JSON Response Format**: Structured JSON output for easy data processing

## Connection URL Format

The PowerDrill SQLAlchemy dialect uses the following connection URL format:

```
powerdrill://[host]?api_key=[api_key]&user_id=[user_id]&dataset_id=[dataset_id]
```

Required Parameters:
- `host`: PowerDrill API host (default: ai.data.cloud)
- `api_key`: Your PowerDrill API key
- `user_id`: Your PowerDrill user ID
- `dataset_id`: Target dataset ID

## Requirements

- Python >= 3.7
- SQLAlchemy >= 1.4.0, < 2.0.0
- requests >= 2.31.0

## Response Format

The PowerDrill dialect returns results in a structured JSON format:

```json
{
    "columns": [
        {
            "name": "column_name",
            "type": "column_type"
        }
    ],
    "rows": [
        [row_data]
    ]
}
```

- Column names use snake_case format
- Column types align with MySQL data types
- Row data is formatted according to the specified column types

## License

MIT License

## Support

For support or bug reports, please contact dev@powerdrill.ai.
