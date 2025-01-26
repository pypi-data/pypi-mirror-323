# ApexBase

🚀 A lightning-fast, feature-rich embedded database designed for modern Python applications.

## Features

✨ **High Performance**
- Built on SQLite with optimized configurations
- Efficient batch operations support
- Automatic performance optimization
- Concurrent access support

🔍 **Powerful Query Capabilities**
- SQL-like query syntax
- Full-text search with case-insensitive support
- Complex queries with multiple conditions
- JSON field support

📊 **Data Framework Integration**
- Seamless integration with Pandas
- Native support for PyArrow
- Built-in Polars compatibility

🎯 **Multi-table Support**
- Multiple table management
- Easy table switching
- Automatic table creation and deletion

🛡️ **Data Integrity**
- ACID compliance
- Transaction support
- Automatic error handling
- Data consistency guarantees

🔧 **Developer Friendly**
- Simple and intuitive API
- Minimal configuration required
- Comprehensive documentation
- Extensive test coverage

## Installation

```bash
pip install apexbase
```

## Quick Start

```python
from apexbase import ApexClient

# Initialize the database
client = ApexClient("my_database")

# Store single record
record = {"name": "John", "age": 30, "tags": ["python", "rust"]}
id_ = client.store(record)

# Store multiple records
records = [
    {"name": "Jane", "age": 25},
    {"name": "Bob", "age": 35}
]
ids = client.store(records)

# Query records
results = client.query("age > 25")
for record in results:
    print(record)

# Full-text search
client.set_searchable("name", True)
results = client.search_text("John")

# Import from Pandas
import pandas as pd
df = pd.DataFrame({"name": ["Alice", "Bob"], "age": [28, 32]})
client.from_pandas(df)
```

## Advanced Usage

### Multi-table Operations

```python
# Create and switch tables
client.create_table("users")
client.create_table("orders")
client.use_table("users")

# Store user data
user = {"name": "John", "email": "john@example.com"}
user_id = client.store(user)

# Switch to orders table
client.use_table("orders")
order = {"user_id": user_id, "product": "Laptop"}
client.store(order)
```

### Complex Queries

```python
# Multiple conditions
results = client.query("age > 25 AND city = 'New York'")

# Range queries
results = client.query("score >= 85.0 AND score <= 90.0")

# LIKE queries
results = client.query("name LIKE 'J%'")
```

### Performance Optimization

```python
# Disable automatic FTS updates for batch operations
client.set_auto_update_fts(False)

# Store large batch of records
records = [{"id": i, "value": i * 2} for i in range(10000)]
ids = client.store(records)

# Manually rebuild search index
client.rebuild_search_index()
```

## Requirements

- Python >= 3.9
- Dependencies:
  - orjson
  - pandas
  - pyarrow
  - polars
  - numpy
  - psutil

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
