from sqlalchemy.dialects import registry

from powerdrill.base import PowerDrillDialect

registry.register('powerdrill', 'powerdrill.base', 'PowerDrillDialect')
