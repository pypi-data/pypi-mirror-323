# Peslac API Client

A Python package to interact with the Peslac API for document management and AI-powered tools.

## Installation

Install the Peslac API Client using pip:

```bash
pip install peslac
```

## Usage

### Initializing the Client

First, import the Peslac class and create an instance with your API key:

```python
from peslac import Peslac

client = Peslac(api_key="your-api-key-here")
```

### Examples

#### Using a Local File

```python
# Use a tool with a local file
file_path = "path/to/your/document.pdf"
tool_id = "your-tool-id"
response = client.use_tool(file_path, tool_id)
print("Tool Response:", response)
```

#### Using a Remote File URL

```python
# Use a tool with a remote file URL
file_url = "https://example.com/document.pdf"
tool_id = "your-tool-id"
response = client.use_tool_with_file_url(file_url, tool_id)
print("Response:", response)
```

#### Retrieving a Document

```python
# Retrieve a document
document_id = "your-document-id"
response = client.retrieve_document(document_id)
print("Document Response:", response)
```

#### Submitting and Retrieving a Bank Statement

```python
# Submit a bank statement
file_path = "path/to/bank_statement.pdf"
type_of_account = "savings"
currency = "USD"
response = client.submit_bank_statement(file_path, type_of_account, currency)
print("Bank Statement Submission Response:", response)

# Retrieve the bank statement
document_id = "your-document-id"
response = client.retrieve_bank_statement(document_id)
print("Bank Statement Response:", response)
```

## API Reference

### `Peslac(api_key)`

Creates a new instance of the Peslac client.

- `api_key` (string): Your Peslac API key.

### `retrieve_document(document_id)`

Retrieves a document by its ID.

- `document_id` (string): The ID of the document you want to retrieve.
- **Returns**: A dictionary with the document details.

### `use_tool(file_path, tool_id)`

Uses an AI-powered tool on a document.

- `file_path` (string): Path to the file you want to process.
- `tool_id` (string): ID of the tool you want to use.
- **Returns**: A dictionary with the tool usage result.

### `use_tool_with_file_url(file_url, tool_id)`

Uses an AI-powered tool with a remote file URL.

- `file_url` (string): URL of the file you want to process.
- `tool_id` (string): ID of the tool you want to use.
- **Returns**: A dictionary with the tool usage result.

### `submit_bank_statement(file_path, type_of_account, currency)`

Submits a bank statement with additional metadata.

- `file_path` (string): Path to the bank statement file.
- `type_of_account` (string): Type of account (e.g., savings, checking).
- `currency` (string): The currency of the account (e.g., USD, EUR).
- **Returns**: A dictionary with the submission result.

### `retrieve_bank_statement(document_id)`

Retrieves a bank statement by its ID.

- `document_id` (string): The ID of the bank statement you want to retrieve.
- **Returns**: A dictionary with the bank statement details.

## Error Handling

All methods raise exceptions if operations fail. It's recommended to use try-except blocks when calling these functions:

```python
try:
    response = client.retrieve_document("invalid-document-id")
    print("Document Response:", response)
except Exception as e:
    print("Error:", e)
```

## License

This project is licensed under the MIT License. See the LICENSE file for more details.

## Support

For support or questions, please contact:

- Email: support@peslac.com
- GitHub: Open an issue in the repository
