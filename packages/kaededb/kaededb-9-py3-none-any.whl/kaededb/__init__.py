import requests
import json
class KDBClient:
    def __init__(self, base_url, api_key):
        self.base_url = base_url.rstrip('/')  # Remove trailing slash if present
        self.api_key = api_key
        self.headers = {'X-API-Key': self.api_key}

    def _handle_response(self, response):
        try:
            response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
            return response.json()
        except requests.exceptions.HTTPError as e:
            error_message = f"API Error: {e}. "
            try:
                error_json = response.json()
                if 'message' in error_json:
                    error_message += error_json['message']
                elif 'error' in error_json:
                    error_message += error_json['error']
            except json.JSONDecodeError:
                error_message += "Could not parse error response."
            raise Exception(error_message)
        except json.JSONDecodeError:
            raise Exception("Invalid JSON response from API.")

    # --- Token Endpoint ---
    def generate_token(self):
        url = f"{self.base_url}/tokens/generate"
        response = requests.post(url)
        return self._handle_response(response)

    # --- Database Endpoints ---
    def list_databases(self):
        url = f"{self.base_url}/databases"
        response = requests.get(url, headers=self.headers)
        return self._handle_response(response)

    def create_database(self, db_name):
        url = f"{self.base_url}/databases"
        response = requests.post(url, headers=self.headers, json={'db_name': db_name})
        return self._handle_response(response)

    def delete_database(self, db_name):
        url = f"{self.base_url}/databases/{db_name}"
        response = requests.delete(url, headers=self.headers)
        return self._handle_response(response)

    # --- Collection Endpoints ---
    def list_collections(self, db_name):
        url = f"{self.base_url}/databases/{db_name}/collections"
        response = requests.get(url, headers=self.headers)
        return self._handle_response(response)

    def create_collection(self, db_name, collection_name):
        url = f"{self.base_url}/databases/{db_name}/collections"
        response = requests.post(url, headers=self.headers, json={'collection_name': collection_name})
        return self._handle_response(response)

    def delete_collection(self, db_name, collection_name):
        url = f"{self.base_url}/databases/{db_name}/collections/{collection_name}"
        response = requests.delete(url, headers=self.headers)
        return self._handle_response(response)

    # --- Document Endpoints ---
    def find_documents(self, db_name, collection_name, query=None):
        url = f"{self.base_url}/databases/{db_name}/collections/{collection_name}/documents"
        response = requests.get(url, headers=self.headers, params=query) # Use params for query strings
        return self._handle_response(response)

    def insert_document(self, db_name, collection_name, document):
        url = f"{self.base_url}/databases/{db_name}/collections/{collection_name}/documents"
        response = requests.post(url, headers=self.headers, json=document)
        return self._handle_response(response)

    def get_document(self, db_name, collection_name, doc_id):
        url = f"{self.base_url}/databases/{db_name}/collections/{collection_name}/documents/{doc_id}"
        response = requests.get(url, headers=self.headers)
        return self._handle_response(response)

    def update_document(self, db_name, collection_name, doc_id, update_data):
        url = f"{self.base_url}/databases/{db_name}/collections/{collection_name}/documents/{doc_id}"
        response = requests.put(url, headers=self.headers, json=update_data)
        return self._handle_response(response)

    def delete_document(self, db_name, collection_name, doc_id):
        url = f"{self.base_url}/databases/{db_name}/collections/{collection_name}/documents/{doc_id}"
        response = requests.delete(url, headers=self.headers)
        return self._handle_response(response)