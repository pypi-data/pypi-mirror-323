"""SQLAlchemy dialect for PowerDrill."""
import json
import requests
import uuid
import time
from collections import namedtuple
from sqlalchemy import types
from sqlalchemy.engine import default
from sqlalchemy.sql import compiler
from sqlalchemy import exc
from powerdrill.utils import parse_and_check_json_markdown, mysql_to_sqlalchemy_type

CursorDescriptionRow = namedtuple(
    'CursorDescriptionRow',
    [
        'name', 'type_code', 'display_size', 'internal_size',
        'precision', 'scale', 'null_ok'
    ]
)


FORMAT_TABLE = """
    ## 问题
    问题开始
    --------
    $query$
    --------
    问题结束
    -----------------------------

    ## 业务逻辑
    - 第一阶段：执行问题
    - 第二步：在处理完业务逻辑后，请最大可能将第一步结果转化成为一个数据集（是一个二维表格）,数据集展现为一个json对象。
    ## JSON对象说明：
    - JSON 格式如下：
    {
        columns: [
            {
                name: "$column_name$",       
                type: "$column_type$"
            }
        ],
        rows: [
            [$每行数据$]
        ]
    }
    - $column_name$ 采用下划线命名，不允许使用空格，尽最大可能通俗易用
    - $column_type$ 遵循MySQL数据类型，尽最大可能对齐MySQL数据类型
    - $每行数据$ 每个元素以"$column_type$"类型表示

    ## 输出要求
        - 不管第一步问题的内容以及输出要求是什么，都不输出。
        - 仅输出第二步的json结果json对象（markdown格式），不允许输出其他内容，辅助信息全部不需要，否则视为问题回答失败
        - 仅输出第二步的json结果json对象（markdown格式），不允许输出其他内容，辅助信息全部不需要，否则视为问题回答失败
"""
def format_operation(operation):
    return FORMAT_TABLE.replace("$query$", operation)

class PowerDrillIdentifierPreparer(compiler.IdentifierPreparer):
    def __init__(self, dialect):
        super(PowerDrillIdentifierPreparer, self).__init__(
            dialect,
            initial_quote='"',
        )

class PowerDrillCompiler(compiler.SQLCompiler):
    def visit_select(self, select, **kwargs):
        return super(PowerDrillCompiler, self).visit_select(select, **kwargs)

    def limit_clause(self, select, **kwargs):
        text = ""
        if select._limit_clause is not None:
            text += "\nLIMIT " + self.process(select._limit_clause, **kwargs)
        if select._offset_clause is not None:
            text += "\nOFFSET " + self.process(select._offset_clause, **kwargs)
        return text



class PowerDrillDialect(default.DefaultDialect):
    """SQLAlchemy dialect for PowerDrill."""
    name = 'powerdrill'
    driver = 'rest'
    
    supports_alter = False
    supports_pk_autoincrement = False
    supports_default_values = False
    supports_empty_insert = False
    supports_unicode_statements = True
    supports_unicode_binds = True
    returns_unicode_strings = True
    description_encoding = None
    supports_native_boolean = True
    
    @classmethod
    def dbapi(cls):
        return PowerDrillDBAPI()
    
    def __init__(self, **kw):
        super().__init__(**kw)
        self.identifier_preparer = PowerDrillIdentifierPreparer(self)
        self._json_serializer = json.dumps

    @classmethod
    def import_dbapi(cls):
        """Return the DBAPI module."""
        return PowerDrillDBAPI()

    def create_connect_args(self, url):
        """Create connection arguments from URL."""
        # Extract the API key from the query parameters
        api_key = url.query.get('api_key')
        if not api_key:
            raise ValueError("api_key is required in the connection URL")

        # Extract user_id from the query parameters
        user_id = url.query.get('user_id')
        if not user_id:
            raise ValueError("user_id is required in the connection URL")

        # Extract dataset_id from the query parameters
        dataset_id = url.query.get('dataset_id')
        if not dataset_id:
            raise ValueError("dataset_id is required in the connection URL")

        # Handle URL with or without scheme
        api_url = url.host
        if url.port:
            api_url = f"{api_url}:{url.port}"
        if url.database:
            api_url = f"{api_url}/{url.database}"

        return [], {
            "api_url": api_url,
            "api_key": api_key,
            "user_id": user_id,
            "dataset_id": dataset_id
        }

    def get_schema_names(self, connection, **kwargs):
        """Get all schema names by calling List datasets API."""
        try:
            headers = {
                'Content-Type': 'application/json',
                'x-pd-api-key': connection.connection.api_key
            }
            url = connection.connection.api_url
            api_version = connection.connection.api_version
            
            if not url.startswith('http'):
                url = 'https://' + url
            response = requests.get(
                f"{url}/api/{api_version}/team/datasets",
                headers=headers
            )
            response.raise_for_status()
            result = response.json()
            
            if result.get('code') == 0:  # Success
                records = result.get('data', {}).get('records', [])
                # Extract id, name, and description from records
                datasets = [
                    {
                        'dataset_id': record.get('id'),
                        'dataset_name': record.get('name'),
                        'dataset_description': record.get('description')
                    }
                    for record in records
                ]
                
                # Format response as expected by SQLAlchemy
                return [dataset['dataset_name'] for dataset in datasets if dataset.get('dataset_name')]
            
            return []
        except Exception as e:
            raise exc.SQLAlchemyError(f"Failed to get schemas: {str(e)}")

    def get_table_names(self, connection, schema=None, **kwargs):
        return []

    def get_view_names(self, connection, schema=None, **kwargs):
        return []

    def get_columns(self, connection, table_name, schema=None, **kwargs):
        return []

    def get_pk_constraint(self, connection, table_name, schema=None, **kwargs):
        return {'constrained_columns': [], 'name': None}

    def get_foreign_keys(self, connection, table_name, schema=None, **kwargs):
        return []

    def get_indexes(self, connection, table_name, schema=None, **kwargs):
        return []

    def do_rollback(self, dbapi_connection):
        pass

class PowerDrillDBAPI:
    paramstyle = 'pyformat'
    threadsafety = 2
    apilevel = '2.0'

    def __init__(self):
        self.Error = PowerDrillError
        self.Warning = PowerDrillWarning

    def connect(self, *args, **kwargs):
        return Connection(*args, **kwargs)

class Connection:
    def __init__(self, api_url=None, api_key=None, user_id=None, dataset_id=None, api_version='v1', **kwargs):
        """Initialize connection with API URL and key."""
        if not api_url:
            raise ValueError("api_url is required")
        if not api_key:
            raise ValueError("api_key is required")
        if not user_id:
            raise ValueError("user_id is required")
        if not dataset_id:
            raise ValueError("dataset_id is required")

        self.api_url = api_url
        self.api_key = api_key
        self.user_id = user_id
        self.dataset_id = dataset_id
        self.session_id = None
        self.api_version = api_version
        self.headers = {
            'Content-Type': 'application/json',
            'x-pd-api-key': api_key,
        }

    def cursor(self):
        """Return a cursor object that can execute queries."""
        return Cursor(self)

    def close(self):
        """Close the connection."""
        pass

    def commit(self):
        """Commit any pending transaction."""
        pass

    def rollback(self):
        """Rollback any pending transaction."""
        pass

    def _create_session(self):
        """Create a new session."""
        url = self.api_url
        if not url.startswith('http'):
            url = 'https://' + url
        response = requests.post(
            f"{url}/api/{self.api_version}/team/sessions",
            headers=self.headers,
            json={
                "userId": self.user_id,
                "datasetId": self.dataset_id
            }
        )
        if response.status_code != 200:
            raise Exception(f"Failed to create session: {response.text}")
        try:
            response_data = response.json()
            if 'code' in response_data and response_data['code'] != 0:
                raise Exception(f"API error: {response_data.get('msg', 'Unknown error')}")
            print("Session response:", response_data)  # Debug print
            
            # Extract session ID from response
            if response_data.get('code') == 0 and 'data' in response_data:
                self.session_id = response_data['data']['id']
            else:
                self.session_id = (
                    response_data.get('sessionId') or 
                    response_data.get('data', {}).get('sessionId') or
                    response_data.get('data', {}).get('session_id')
                )
            
            if not self.session_id:
                raise Exception(f"No session ID in response: {response_data}")
        except ValueError as e:
            raise Exception(f"Invalid JSON response: {e}")

    def _execute_query(self, query):
        """Execute a query and return the response."""
        url = self.api_url
        if not url.startswith('http'):
            url = 'https://' + url

        # Create session if not exists
        if not self.session_id:
            self._create_session()

        # Prepare request data
        data = {
            'sessionId': self.session_id,
            'datasetId': self.dataset_id,
            'question': query
        }

        # Execute query
        response = requests.post(
            f"{url}/api/{self.api_version}/team/jobs?userId={self.user_id}",
            headers=self.headers,
            json=data
        )

        if response.status_code != 200:
            raise Exception(f"Failed to execute query: {response.text}")
        try:
            response_data = response.json()
            print("Query response:", response_data)  # Debug print
            if 'code' in response_data and response_data['code'] != 0:
                raise Exception(f"API error: {response_data.get('msg', 'Unknown error')}")
            return response_data
        except ValueError as e:
            raise Exception(f"Invalid JSON response: {e}")

    def _get_datasets(self):
        """Get list of available datasets."""
        url = self.api_url
        if not url.startswith('http'):
            url = 'https://' + url
        response = requests.get(
            f"{url}/api/{self.api_version}/team/datasets",
            headers=self.headers
        )
        if response.status_code != 200:
            raise Exception(f"Failed to get datasets: {response.text}")
        try:
            result = response.json()
            if result.get('code') == 0:  # Success
                records = result.get('data', {}).get('records', [])
                # Extract id, name, and description from records
                return [
                    {
                        'dataset_id': record.get('id'),
                        'dataset_name': record.get('name'),
                        'dataset_description': record.get('description')
                    }
                    for record in records
                ]
            return []
        except ValueError as e:
            raise Exception(f"Invalid JSON response: {e}")

    def get_schema_names(self):
        """Get all schema names."""
        response = self._get_datasets()
        return [dataset['dataset_name'] for dataset in response]

    def close(self):
        """Close the connection and clean up resources."""
        if self.session_id:
            try:
                url = self.api_url
                if not url.startswith('http'):
                    url = 'https://' + url
                requests.delete(
                    f"{url}/api/{self.api_version}/team/sessions/{self.session_id}",
                    headers=self.headers
                )
            except Exception:
                pass  # Ignore errors during cleanup

class Cursor:
    """A cursor for executing queries."""
    def __init__(self, connection):
        """Initialize cursor with connection."""
        self.connection = connection
        self.description = None
        self._rows = None
        self._rowcount = -1
        self._arraysize = 1

    @property
    def rowcount(self):
        """Return number of rows."""
        return self._rowcount

    @property
    def arraysize(self):
        """Return array size."""
        return self._arraysize

    @arraysize.setter
    def arraysize(self, value):
        """Set array size."""
        self._arraysize = value

    def close(self):
        """Close cursor."""
        self.description = None
        self._rows = None
        self._rowcount = -1

    def execute(self, operation, parameters=None):
        """Execute a query."""
        if parameters:
            operation = operation % parameters
        operation = format_operation(operation)
        if not self.connection.session_id:
            self.connection._create_session()
        response = self.connection._execute_query(operation)
        
        # Extract data from response
        if response and 'data' in response and 'blocks' in response['data']:
            blocks = response['data']['blocks']
            last_respond_message = None
            
            # Find the last message block with stage=Respond
            for block in blocks:
                if (block.get('type') == 'CODE' and 
                    block.get('stage') == 'Respond' and 
                    block.get('groupName') == 'Answer'):
                    last_respond_message = block
            
            if last_respond_message:
                content = last_respond_message['content']
                try:
                    # Parse JSON and check for required fields
                    data = parse_and_check_json_markdown(content, ['columns', 'rows'])
                    
                    # Set description based on columns
                    self.description = tuple(
                        CursorDescriptionRow(
                            name=col['name'],
                            type_code=mysql_to_sqlalchemy_type(col['type']),
                            display_size=None,
                            internal_size=None,
                            precision=None,
                            scale=None,
                            null_ok=True
                        )
                        for col in data['columns']
                    )
                    
                    # Set rows
                    self._rows = data['rows']
                    self._rowcount = len(self._rows)
                    return self
                except ValueError:
                    pass  # No valid JSON object found, continue with next block
        
        # If no valid data found
        self.description = tuple()
        self._rows = []
        self._rowcount = 0
        return self

    def executemany(self, operation, seq_of_parameters=None):
        """Execute multiple queries."""
        raise NotImplementedError("executemany is not supported")

    def fetchone(self):
        """Fetch next row."""
        if not self._rows:
            return None
        return self._rows.pop(0) if self._rows else None

    def fetchmany(self, size=None):
        """Fetch next size rows."""
        if size is None:
            size = self.arraysize
        rows = self._rows[:size]
        self._rows = self._rows[size:]
        return rows

    def fetchall(self):
        """Fetch all remaining rows."""
        rows = self._rows
        self._rows = []
        return rows

    def setinputsizes(self, sizes):
        """Set input sizes."""
        pass

    def setoutputsize(self, size, column=None):
        """Set output size."""
        pass

class PowerDrillError(Exception):
    pass

class PowerDrillWarning(Exception):
    pass
