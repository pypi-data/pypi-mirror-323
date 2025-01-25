import os
import requests
import mimetypes
from requests_toolbelt.multipart.encoder import MultipartEncoder
from .config import BASE_URL

class Peslac:
    def __init__(self, api_key, base_url=BASE_URL):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.headers = {"Authorization": f"Bearer {self.api_key}"}

    def _request(self, method, endpoint, data=None, files=None):
        url = f"{self.base_url}{endpoint}"
        try:
            response = requests.request(
                method, url, headers=self.headers, data=data, files=files
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            # Try to get error details from response
            try:
                error_data = e.response.json()
                error_message = error_data.get('message', str(e))
                error_code = error_data.get('code', e.response.status_code)
                raise Exception(f"API Error {error_code}: {error_message}")
            except ValueError:
                # If response is not JSON
                raise Exception(f"API Error {e.response.status_code}: {str(e)}")
        except requests.exceptions.ConnectionError:
            raise Exception("Failed to connect to API server")
        except requests.exceptions.Timeout:
            raise Exception("API request timed out")
        except requests.exceptions.RequestException as e:
            raise Exception(f"API request failed: {str(e)}")

    def retrieve_document(self, document_id):
        if not document_id:
            raise ValueError("Document ID is required")
        return self._request("GET", f"/documents/{document_id}")

    def use_tool(self, file_path, tool_id):
        if not file_path:
            raise ValueError("File path is required")
        if not tool_id:
            raise ValueError("Tool ID is required")
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        # Check file extension
        file_ext = os.path.splitext(file_path)[1].lower()
        allowed_extensions = ['.pdf', '.png', '.jpg', '.jpeg', '.tiff', '.bmp']
        if file_ext not in allowed_extensions:
            raise ValueError(f"Unsupported file type. Allowed types: {', '.join(allowed_extensions)}")

        try:
            with open(file_path, "rb") as file:
                mime_type, _ = mimetypes.guess_type(file_path)
                if not mime_type:
                    mime_type = 'application/octet-stream'
                    
                multipart_data = MultipartEncoder(
                    fields={
                        "file": (os.path.basename(file_path), file, mime_type),
                        "tool_id": tool_id,
                    }
                )
                headers = {**self.headers, "Content-Type": multipart_data.content_type}
                response = requests.post(
                    f"{self.base_url}/tools/use",
                    headers=headers,
                    data=multipart_data,
                )
                response.raise_for_status()
                return response.json()
        except requests.exceptions.HTTPError as e:
            try:
                error_data = e.response.json()
                error_message = error_data.get('message', str(e))
                error_code = error_data.get('code', e.response.status_code)
                raise Exception(f"API Error {error_code}: {error_message}")
            except ValueError:
                raise Exception(f"API Error {e.response.status_code}: {str(e)}")
        except (IOError, OSError) as e:
            raise Exception(f"File error: {str(e)}")
        except Exception as e:
            raise Exception(f"Unexpected error: {str(e)}")

    def use_tool_with_file_url(self, file_url, tool_id):
        if not file_url:
            raise ValueError("File URL is required")
        if not tool_id:
            raise ValueError("Tool ID is required")

        # Check file extension from URL
        file_ext = os.path.splitext(file_url)[1].lower()
        allowed_extensions = ['.pdf', '.png', '.jpg', '.jpeg', '.tiff', '.bmp']
        if file_ext not in allowed_extensions:
            raise ValueError(f"Unsupported file type. Allowed types: {', '.join(allowed_extensions)}")

        data = {"fileUrl": file_url, "tool_id": tool_id}
        return self._request("POST", "/tools/use-url", data=data)

    def submit_bank_statement(self, file_path, type_of_account, currency):
        if not file_path:
            raise ValueError("File path is required")
        if not type_of_account:
            raise ValueError("Type of account is required")
        if not currency:
            raise ValueError("Currency is required")
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        # Check file extension
        file_ext = os.path.splitext(file_path)[1].lower()
        allowed_extensions = ['.pdf', '.png', '.jpg', '.jpeg', '.tiff', '.bmp', 'webp']
        if file_ext not in allowed_extensions:
            raise ValueError(f"Unsupported file type. Allowed types: {', '.join(allowed_extensions)}")

        try:
            with open(file_path, "rb") as file:
                mime_type, _ = mimetypes.guess_type(file_path)
                if not mime_type:
                    mime_type = 'application/octet-stream'
                    
                multipart_data = MultipartEncoder(
                    fields={
                        "file": (os.path.basename(file_path), file, mime_type),
                        "type_of_account": type_of_account,
                        "currency": currency,
                    }
                )
                headers = {**self.headers, "Content-Type": multipart_data.content_type}
                response = requests.post(
                    f"{self.base_url}/bank-statements/pdf",
                    headers=headers,
                    data=multipart_data,
                )
                response.raise_for_status()
                return response.json()
        except requests.exceptions.HTTPError as e:
            try:
                error_data = e.response.json()
                error_message = error_data.get('message', str(e))
                error_code = error_data.get('code', e.response.status_code)
                raise Exception(f"API Error {error_code}: {error_message}")
            except ValueError:
                raise Exception(f"API Error {e.response.status_code}: {str(e)}")
        except (IOError, OSError) as e:
            raise Exception(f"File error: {str(e)}")
        except Exception as e:
            raise Exception(f"Unexpected error: {str(e)}")

    def retrieve_bank_statement(self, document_id):
        if not document_id:
            raise ValueError("Document ID is required")
        return self._request("GET", f"/bank-statements/{document_id}")

    def parser(self, file_path):
        if not file_path:
            raise ValueError("File path is required")
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        # Check file extension
        file_ext = os.path.splitext(file_path)[1].lower()
        allowed_extensions = ['.pdf', '.png', '.jpg', '.jpeg', '.tiff', '.bmp', 'webp']
        if file_ext not in allowed_extensions:
            raise ValueError(f"Unsupported file type. Allowed types: {', '.join(allowed_extensions)}")

        try:
            with open(file_path, "rb") as file:
                mime_type, _ = mimetypes.guess_type(file_path)
                if not mime_type:
                    mime_type = 'application/octet-stream'
                    
                multipart_data = MultipartEncoder(
                    fields={
                        "file": (os.path.basename(file_path), file, mime_type),
                    }
                )
                headers = {**self.headers, "Content-Type": multipart_data.content_type}
                response = requests.post(
                    f"{self.base_url}/parser",
                    headers=headers,
                    data=multipart_data,
                )
                response.raise_for_status()
                return response.json()
        except requests.exceptions.HTTPError as e:
            try:
                error_data = e.response.json()
                error_message = error_data.get('message', str(e))
                error_code = error_data.get('code', e.response.status_code)
                raise Exception(f"API Error {error_code}: {error_message}")
            except ValueError:
                raise Exception(f"API Error {e.response.status_code}: {str(e)}")
        except (IOError, OSError) as e:
            raise Exception(f"File error: {str(e)}")
        except Exception as e:
            raise Exception(f"Unexpected error: {str(e)}")
