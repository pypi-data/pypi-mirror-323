import unittest
from unittest.mock import patch, MagicMock
from sqlalchemy import create_engine, text, MetaData, Table, Column, Integer, String
from sqlalchemy.sql import select
import json
import requests_mock

class TestPowerDrillDriver(unittest.TestCase):
    def setUp(self):
        """Set up test environment before each test."""
        self.api_url = "ai.data.cloud"  # Simple domain without scheme
        self.api_key = "proj_sk_eJxLzNZNzjWtKDQsKiy2yDWqMDAvSsmuSjYvys7MszI0NzazNDYxM7UwMrKwsnSrCs9w968MC3KsKLWoDPLJdEnJj0osDTYurtT3ck_3s0zL8w9KNPTOcAUAyIgcDQ"
        self.mock_adapter = requests_mock.Adapter()
        
        self.engine = create_engine(
            f'powerdrill://{self.api_url}?api_key={self.api_key}'
        )
        self.connection = self.engine.connect()

    def tearDown(self):
        """Clean up after each test."""
        self.connection.close()
        self.engine.dispose()
        self.patcher.stop()

    def test_execute_select_query(self):
        """Test executing a SELECT query."""
        # Execute a test query
        result = self.connection.execute(text("一个全国城市名称以及区号的表格"))
        print(result)

    @requests_mock.Mocker()
    def test_get_schema_names(self, m):
        result = self.connection.execute(text("输出所有表"))
        print(result)

if __name__ == '__main__':
    unittest.main()
