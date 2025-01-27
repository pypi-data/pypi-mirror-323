import os
import json
from cryptography.fernet import Fernet
import base64

class KDBEngine:
    def __init__(self, db_file):
        self.db_file = db_file
        self.encryption_key = self._load_encryption_key()
        self.db_data = self._load_db()

    def _generate_encryption_key(self):
        key = Fernet.generate_key()
        return base64.urlsafe_b64encode(key).decode() # Store as string

    def _load_encryption_key(self):
        key_file = self.db_file + ".key"
        if os.path.exists(key_file):
            with open(key_file, "r") as f:
                key_str = f.read().strip()
                return base64.urlsafe_b64decode(key_str.encode()) # Convert back to bytes
        else:
            key_str = self._generate_encryption_key()
            with open(key_file, "w") as f:
                f.write(key_str)
            return base64.urlsafe_b64decode(key_str.encode())

    def _encrypt_db(self, data_str):
        f = Fernet(self.encryption_key)
        encrypted_data = f.encrypt(data_str.encode())
        return encrypted_data

    def _decrypt_db(self, encrypted_data):
        f = Fernet(self.encryption_key)
        decrypted_data = f.decrypt(encrypted_data)
        return decrypted_data.decode()

    def _load_db(self):
        if os.path.exists(self.db_file):
            try:
                with open(self.db_file, "rb") as f: # Read binary for encrypted data
                    encrypted_data = f.read()
                    if not encrypted_data: # Handle empty file
                        return {}
                    decrypted_str = self._decrypt_db(encrypted_data)
                    return json.loads(decrypted_str)
            except Exception as e: # Handle decryption or JSON errors
                print(f"Error loading database: {e}. Database file might be corrupted or key mismatch.")
                return {} # Return empty DB to avoid crashing
        else:
            return {}

    def _save_db(self):
        data_str = json.dumps(self.db_data, indent=4) # Indent for readability in decrypted form (debugging)
        encrypted_data = self._encrypt_db(data_str)
        with open(self.db_file, "wb") as f: # Write binary for encrypted data
            f.write(encrypted_data)

    def create_database(self, db_name):
        if db_name in self.db_data:
            return False, f"Database '{db_name}' already exists."
        self.db_data[db_name] = {}
        self._save_db()
        return True, f"Database '{db_name}' created."

    def delete_database(self, db_name):
        if db_name not in self.db_data:
            return False, f"Database '{db_name}' does not exist."
        del self.db_data[db_name]
        self._save_db()
        return True, f"Database '{db_name}' deleted."

    def create_collection(self, db_name, collection_name):
        if db_name not in self.db_data:
            return False, f"Database '{db_name}' does not exist."
        if collection_name in self.db_data[db_name]:
            return False, f"Collection '{collection_name}' already exists in '{db_name}'."
        self.db_data[db_name][collection_name] = []
        self._save_db()
        return True, f"Collection '{collection_name}' created in '{db_name}'."

    def delete_collection(self, db_name, collection_name):
        if db_name not in self.db_data:
            return False, f"Database '{db_name}' does not exist."
        if collection_name not in self.db_data[db_name]:
            return False, f"Collection '{collection_name}' does not exist in '{db_name}'."
        del self.db_data[db_name][collection_name]
        self._save_db()
        return True, f"Collection '{collection_name}' deleted from '{db_name}'."

    def insert_document(self, db_name, collection_name, document):
        if db_name not in self.db_data:
            return False, f"Database '{db_name}' does not exist."
        if collection_name not in self.db_data[db_name]:
            return False, f"Collection '{collection_name}' does not exist in '{db_name}'."
        if not isinstance(document, dict):
            return False, "Document must be a dictionary."
        document['_id'] = self._generate_id() # Simple ID generation (not globally unique in a distributed system!)
        self.db_data[db_name][collection_name].append(document)
        self._save_db()
        return True, document['_id']

    def _generate_id(self):
        import uuid
        return str(uuid.uuid4())

    def find_documents(self, db_name, collection_name, query={}):
        if db_name not in self.db_data:
            return False, f"Database '{db_name}' does not exist.", []
        if collection_name not in self.db_data[db_name]:
            return False, f"Collection '{collection_name}' does not exist in '{db_name}'.", []

        results = []
        for doc in self.db_data[db_name][collection_name]:
            match = True
            for key, value in query.items():
                if key not in doc or doc[key] != value:
                    match = False
                    break
            if match:
                results.append(doc)
        return True, "Documents found.", results

    def find_document_by_id(self, db_name, collection_name, doc_id):
        if db_name not in self.db_data:
            return False, f"Database '{db_name}' does not exist.", None
        if collection_name not in self.db_data[db_name]:
            return False, f"Collection '{collection_name}' does not exist in '{db_name}'.", None

        for doc in self.db_data[db_name][collection_name]:
            if doc.get('_id') == doc_id:
                return True, "Document found.", doc
        return False, "Document not found.", None

    def update_document(self, db_name, collection_name, doc_id, update_data):
        if db_name not in self.db_data:
            return False, f"Database '{db_name}' does not exist."
        if collection_name not in self.db_data[db_name]:
            return False, f"Collection '{collection_name}' does not exist in '{db_name}'."
        if not isinstance(update_data, dict):
            return False, "Update data must be a dictionary."

        for doc in self.db_data[db_name][collection_name]:
            if doc.get('_id') == doc_id:
                doc.update(update_data)
                self._save_db()
                return True, "Document updated."
        return False, "Document not found."

    def delete_document(self, db_name, collection_name, doc_id):
        if db_name not in self.db_data:
            return False, f"Database '{db_name}' does not exist."
        if collection_name not in self.db_data[db_name]:
            return False, f"Collection '{collection_name}' does not exist in '{db_name}'."

        original_len = len(self.db_data[db_name][collection_name])
        self.db_data[db_name][collection_name] = [
            doc for doc in self.db_data[db_name][collection_name] if doc.get('_id') != doc_id
        ]
        if len(self.db_data[db_name][collection_name]) < original_len:
            self._save_db()
            return True, "Document deleted."
        return False, "Document not found."

    def list_databases(self):
        return True, "Databases listed.", list(self.db_data.keys())

    def list_collections(self, db_name):
        if db_name not in self.db_data:
            return False, f"Database '{db_name}' does not exist.", []
        return True, "Collections listed.", list(self.db_data[db_name].keys())