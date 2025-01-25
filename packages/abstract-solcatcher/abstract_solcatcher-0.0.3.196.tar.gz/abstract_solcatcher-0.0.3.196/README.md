---

# Abstract Solcatcher

The `abstract_solcatcher` package provides a comprehensive solution for making HTTP requests specifically tailored for interacting with Solcatcher.io's APIs. It simplifies complex tasks such as data fetching, data manipulation, and interacting with the Flask backend of Solcatcher.io. This module abstracts API calls and Flask requests, providing utility functions that make it easier to perform these operations.

## Features

- **API Calls**: Facilitates making custom API requests to Solcatcher.io with specific endpoints.
- **Flask Backend Interaction**: Manages interactions with a Flask backend, including viewing and listing database tables and columns.
- **Data Handling**: Provides functions to handle and manipulate data before sending it in requests.

## Modules

- **Abstract Call**: Handles direct API interactions with functions that tailor requests for specific Solcatcher.io endpoints.
- **Abstract Flask**: Manages requests to the Flask backend, providing functions to view and list database tables, as well as retrieve specific table columns.
- **Utilities**: Contains helper functions that return standard URLs and endpoints, and help in updating data payloads.

## Installation

To install the `abstract_solcatcher` package, use the following pip command:

```bash
pip install abstract_solcatcher
```

## Usage

### Making API Calls

To make a custom API call to retrieve metadata:

```python
from abstract_solcatcher import getCallRequest

response = getCallRequest('getMetaData', signature='your_signature_here')
print(response)
```

### Interacting with Flask Backend

To view a specific table in the database:

```python
from abstract_solcatcher import view_table

response = view_table('your_table_name')
print(response)
```

### Listing Database Tables

To list all tables in the database:

```python
from abstract_solcatcher import list_tables

tables = list_tables()
print(tables)
```

## Dependencies

- Python 3.6+
- `requests` library
- `abstract_apis`
- `abstract_utilities`

## Contributions

Contributions to enhance the functionalities of `abstract_solcatcher` are welcome. Please fork the [GitHub repository](https://github.com/AbstractEndeavors/abstract_solcatcher), make your changes, and submit a pull request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contact

For any questions or feedback, please reach out to [partners@abstractendeavors.com](mailto:partners@abstractendeavors.com).

---
