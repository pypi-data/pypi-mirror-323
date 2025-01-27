# kaededb_server/api.py
from flask import Flask, request, jsonify
from kdb_core import KDBEngine
import os
import json
import uuid
import argparse

app = Flask(__name__)

# --- Default Configuration ---
DEFAULT_PORT = 80
DEFAULT_STORAGE_PATH = "."  # Current directory by default
DEFAULT_AUTHENTICATION = True  # Authentication ON by default
TOKENS_FILE_DEFAULT_NAME = "tokens.json"  # Default tokens filename

# --- API Key Management ---
TOKENS_FILE = None  # Will be set based on storage path

def load_api_keys():
    if os.path.exists(TOKENS_FILE):
        with open(TOKENS_FILE, "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:  # Handle empty or corrupted JSON
                return {}
    return {}

def save_api_keys(api_keys):
    with open(TOKENS_FILE, "w") as f:
        json.dump(api_keys, f, indent=4)

API_KEYS = {}  # Initialize empty, will be loaded in main based on storage path


# --- Middleware: API Key Authentication and IP Filtering ---
def authenticate_request():
    if request.path.startswith('/kapi/services/kdb/tokens'):
        return None
    if not request.path.startswith('/kapi/services/kdb/'):
        return None
    if request.endpoint == 'static':
        return None

    api_key = request.headers.get('X-API-Key')
    client_ip = request.remote_addr

    if client_ip not in API_KEYS or API_KEYS[client_ip] != api_key:
        return jsonify({"error": "Unauthorized: Missing or invalid API key for this IP"}), 401

    ALLOWED_IPS = []  # You can configure allowed IPs here if needed
    if ALLOWED_IPS and client_ip not in ALLOWED_IPS:
        return jsonify({"error": "Forbidden: IP address not allowed"}), 403
    return None


# --- API Endpoints ---

@app.route('/kapi/services/kdb/tokens/generate', methods=['POST'])
def generate_token():
    client_ip = request.remote_addr
    new_api_key = str(uuid.uuid4())
    API_KEYS[client_ip] = new_api_key
    save_api_keys(API_KEYS)
    return jsonify({"status": "success", "api_key": new_api_key}), 200


@app.route('/kapi/services/kdb/databases', methods=['GET', 'POST'])
def databases():
    if request.method == 'GET':
        status, message, data = DATABASE_ENGINE.list_databases()
        return jsonify({"status": "success" if status else "error", "message": message, "databases": data}), 200 if status else 400
    elif request.method == 'POST':
        data = request.get_json()
        if not data or 'db_name' not in data:
            return jsonify({"error": "Missing 'db_name' in request body"}), 400
        status, message = DATABASE_ENGINE.create_database(data['db_name'])
        return jsonify({"status": "success" if status else "error", "message": message}), 201 if status else 400


@app.route('/kapi/services/kdb/databases/<db_name>', methods=['DELETE'])
def database_detail(db_name):
    status, message = DATABASE_ENGINE.delete_database(db_name)
    return jsonify({"status": "success" if status else "error", "message": message}), 200 if status else 404


@app.route('/kapi/services/kdb/databases/<db_name>/collections', methods=['GET', 'POST'])
def collections(db_name):
    if request.method == 'GET':
        status, message, data = DATABASE_ENGINE.list_collections(db_name)
        if not status:
            return jsonify({"status": "error", "message": message}), 404
        return jsonify({"status": "success", "message": message, "collections": data}), 200
    elif request.method == 'POST':
        data = request.get_json()
        if not data or 'collection_name' not in data:
            return jsonify({"error": "Missing 'collection_name' in request body"}), 400
        status, message = DATABASE_ENGINE.create_collection(db_name, data['collection_name'])
        if not status:
            return jsonify({"status": "error", "message": message}), 400
        return jsonify({"status": "success", "message": message}), 201


@app.route('/kapi/services/kdb/databases/<db_name>/collections/<collection_name>', methods=['DELETE'])
def collection_detail(db_name, collection_name):
    status, message = DATABASE_ENGINE.delete_collection(db_name, collection_name)
    return jsonify({"status": "success" if status else "error", "message": message}), 200 if status else 404


@app.route('/kapi/services/kdb/databases/<db_name>/collections/<collection_name>/documents', methods=['GET', 'POST'])
def documents(db_name, collection_name):
    if request.method == 'GET':  # GET with query parameters for find_documents
        query = request.args.to_dict()  # Get query params as dict
        status, message, data = DATABASE_ENGINE.find_documents(db_name, collection_name, query)
        if not status:
            return jsonify({"status": "error", "message": message}), 404
        return jsonify({"status": "success", "message": message, "documents": data}), 200
    elif request.method == 'POST':
        document = request.get_json()
        if not document:
            return jsonify({"error": "Missing document in request body"}), 400
        status, doc_id = DATABASE_ENGINE.insert_document(db_name, collection_name, document)
        if not status:
            return jsonify({"status": "error", "message": doc_id}), 400  # message contains error in this case
        return jsonify({"status": "success", "message": "Document inserted", "document_id": doc_id}), 201


@app.route('/kapi/services/kdb/databases/<db_name>/collections/<collection_name>/documents/<doc_id>', methods=['GET', 'PUT', 'DELETE'])
def document_detail(db_name, collection_name, doc_id):
    if request.method == 'GET':
        status, message, data = DATABASE_ENGINE.find_document_by_id(db_name, collection_name, doc_id)
        if not status:
            return jsonify({"status": "error", "message": message}), 404
        return jsonify({"status": "success", "message": message, "document": data}), 200
    elif request.method == 'PUT':
        update_data = request.get_json()
        if not update_data:
            return jsonify({"error": "Missing update data in request body"}), 400
        status, message = DATABASE_ENGINE.update_document(db_name, collection_name, doc_id, update_data)
        return jsonify({"status": "success" if status else "error", "message": message}), 200 if status else 404
    elif request.method == 'DELETE':
        status, message = DATABASE_ENGINE.delete_document(db_name, collection_name, doc_id)
        return jsonify({"status": "success" if status else "error", "message": message}), 200 if status else 404


@app.route('/kapi/services/kdb/docs/', methods=['GET'])
def api_documentation():
    documentation_html = """
    <!DOCTYPE html>
    <html>
    <head>
    <title>KaedeDB API Documentation</title>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; margin: 20px; }
        h1, h2, h3 { color: #0056b3; }
        h1 { border-bottom: 2px solid #0056b3; padding-bottom: 0.5em; }
        h2 { margin-top: 1.5em; border-bottom: 1px solid #ccc; padding-bottom: 0.3em; }
        h3 { margin-top: 1em; }
        p, ul, ol { margin-bottom: 1em; }
        pre { background-color: #f4f4f4; padding: 10px; border: 1px solid #ddd; overflow-x: auto; }
        code { font-family: monospace, monospace; font-size: 1em; background-color: #f0f0f0; padding: 2px 5px; border-radius: 3px; }
        .endpoint { margin-bottom: 1.5em; padding: 15px; border: 1px solid #ddd; border-radius: 5px; background-color: #f9f9f9; }
        .endpoint h3 { color: #007bff; margin-top: 0; }
        .request-type { font-weight: bold; color: #28a745; } /* Green for request type */
        .url { font-family: monospace, monospace; color: #0056b3; } /* URL color */
        .headers, .body, .query-params, .response { margin-left: 20px; }
        .response-code { font-weight: bold; color: #17a2b8; } /* Cyan for response code */
        .response-body { background-color: #e8f0fe; padding: 8px; border-radius: 3px; } /* Light blue for response body */
    </style>
    </head>
    <body>

    <h1>KaedeDB API Documentation</h1>

    <h2>Base URL</h2>
    <p><code>/kapi/services/kdb/</code></p>

    <h2>Authentication</h2>
    <p>All endpoints (except token generation) require an <code>X-API-Key</code> header.</p>
    <p>API keys are generated per IP address using the <code>/kapi/services/kdb/tokens/generate</code> endpoint.</p>

    <!-- Documentation for Endpoints - You can structure this better using loops if needed -->
    <div class="endpoint">
        <h3><span class="request-type">POST</span> <span class="url">/kapi/services/kdb/tokens/generate</span></h3>
        <p>Generates a new API key for the requesting IP address.</p>
        <div class="request">
            <h4>Request</h4>
            <p><strong>Method:</strong> <code>POST</code></p>
            <p><strong>Body:</strong> None</p>
        </div>
        <div class="response">
            <h4>Response</h4>
            <p><span class="response-code">200 OK</span></p>
            <p><strong>Body:</strong></p>
            <pre><code class="response-body">{
    "status": "success",
    "api_key": "generated_api_key"
}</code></pre>
        </div>
    </div>

    <div class="endpoint">
        <h3><span class="request-type">GET</span> <span class="url">/kapi/services/kdb/databases</span></h3>
        <p>List all databases.</p>
        <div class="request">
            <h4>Request</h4>
            <p><strong>Method:</strong> <code>GET</code></p>
            <div class="headers">
                <p><strong>Headers:</strong> <code>X-API-Key: <your_api_key></code></p>
            </div>
        </div>
        <div class="response">
            <h4>Response</h4>
            <p><span class="response-code">200 OK</span></p>
            <p><strong>Body:</strong></p>
            <pre><code class="response-body">{
    "status": "success",
    "message": "Databases listed.",
    "databases": ["db1", "db2", ...]
}</code></pre>
        </div>
    </div>

    <div class="endpoint">
        <h3><span class="request-type">POST</span> <span class="url">/kapi/services/kdb/databases</span></h3>
        <p>Create a new database.</p>
        <div class="request">
            <h4>Request</h4>
            <p><strong>Method:</strong> <code>POST</code></p>
            <div class="headers">
                <p><strong>Headers:</strong> <code>X-API-Key: <your_api_key></code></p>
            </div>
            <div class="body">
                <p><strong>Body:</strong></p>
                <pre><code class="request-body">{
    "db_name": "your_db_name"
}</code></pre>
            </div>
        </div>
        <div class="response">
            <h4>Response</h4>
            <p><span class="response-code">201 Created</span></p>
            <p><strong>Body:</strong></p>
            <pre><code class="response-body">{
    "status": "success",
    "message": "Database 'your_db_name' created."
}</code></pre>
        </div>
    </div>

    <div class="endpoint">
        <h3><span class="request-type">DELETE</span> <span class="url">/kapi/services/kdb/databases/{db_name}</span></h3>
        <p>Delete a database.</p>
        <div class="request">
            <h4>Request</h4>
            <p><strong>Method:</strong> <code>DELETE</code></p>
            <div class="headers">
                <p><strong>Headers:</strong> <code>X-API-Key: <your_api_key></code></p>
            </div>
            <div class="url-params">
                 <p><strong>URL Parameters:</strong> <code>db_name</code> (database name to delete)</p>
            </div>
        </div>
        <div class="response">
            <h4>Response</h4>
            <p><span class="response-code">200 OK</span></p>
            <p><strong>Body:</strong></p>
            <pre><code class="response-body">{
    "status": "success",
    "message": "Database 'db_name' deleted."
}</code></pre>
        </div>
    </div>

     <div class="endpoint">
        <h3><span class="request-type">GET</span> <span class="url">/kapi/services/kdb/databases/{db_name}/collections</span></h3>
        <p>List collections in a database.</p>
        <div class="request">
            <h4>Request</h4>
            <p><strong>Method:</strong> <code>GET</code></p>
            <div class="headers">
                <p><strong>Headers:</strong> <code>X-API-Key: <your_api_key></code></p>
            </div>
             <div class="url-params">
                 <p><strong>URL Parameters:</strong> <code>db_name</code> (database name)</p>
            </div>
        </div>
        <div class="response">
            <h4>Response</h4>
            <p><span class="response-code">200 OK</span></p>
            <p><strong>Body:</strong></p>
            <pre><code class="response-body">{
    "status": "success",
    "message": "Collections listed.",
    "collections": ["col1", "col2", ...]
}</code></pre>
        </div>
    </div>

     <div class="endpoint">
        <h3><span class="request-type">POST</span> <span class="url">/kapi/services/kdb/databases/{db_name}/collections</span></h3>
        <p>Create a new collection in a database.</p>
        <div class="request">
            <h4>Request</h4>
            <p><strong>Method:</strong> <code>POST</code></p>
            <div class="headers">
                <p><strong>Headers:</strong> <code>X-API-Key: <your_api_key></code></p>
            </div>
             <div class="url-params">
                 <p><strong>URL Parameters:</strong> <code>db_name</code> (database name)</p>
            </div>
            <div class="body">
                <p><strong>Body:</strong></p>
                <pre><code class="request-body">{
    "collection_name": "your_collection_name"
}</code></pre>
            </div>
        </div>
        <div class="response">
            <h4>Response</h4>
            <p><span class="response-code">201 Created</span></p>
            <p><strong>Body:</strong></p>
            <pre><code class="response-body">{
    "status": "success",
    "message": "Collection 'your_collection_name' created in 'db_name'."
}</code></pre>
        </div>
    </div>

    <div class="endpoint">
        <h3><span class="request-type">DELETE</span> <span class="url">/kapi/services/kdb/databases/{db_name}/collections/{collection_name}</span></h3>
        <p>Delete a collection.</p>
        <div class="request">
            <h4>Request</h4>
            <p><strong>Method:</strong> <code>DELETE</code></p>
            <div class="headers">
                <p><strong>Headers:</strong> <code>X-API-Key: <your_api_key></code></p>
            </div>
            <div class="url-params">
                 <p><strong>URL Parameters:</strong> <code>db_name</code> (database name), <code>collection_name</code> (collection name to delete)</p>
            </div>
        </div>
        <div class="response">
            <h4>Response</h4>
            <p><span class="response-code">200 OK</span></p>
            <p><strong>Body:</strong></p>
            <pre><code class="response-body">{
    "status": "success",
    "message": "Collection 'collection_name' deleted from 'db_name'."
}</code></pre>
        </div>
    </div>

    <div class="endpoint">
        <h3><span class="request-type">GET</span> <span class="url">/kapi/services/kdb/databases/{db_name}/collections/{collection_name}/documents</span></h3>
        <p>Find documents in a collection (supports query parameters for filtering).</p>
        <div class="request">
            <h4>Request</h4>
            <p><strong>Method:</strong> <code>GET</code></p>
            <div class="headers">
                <p><strong>Headers:</strong> <code>X-API-Key: <your_api_key></code></p>
            </div>
            <div class="url-params">
                 <p><strong>URL Parameters:</strong> <code>db_name</code> (database name), <code>collection_name</code> (collection name)</p>
            </div>
            <div class="query-params">
                <p><strong>Query Parameters:</strong> e.g., <code>?field1=value1&field2=value2</code></p>
            </div>
        </div>
        <div class="response">
            <h4>Response</h4>
            <p><span class="response-code">200 OK</span></p>
            <p><strong>Body:</strong></p>
            <pre><code class="response-body">{
    "status": "success",
    "message": "Documents found.",
    "documents": [{}, {}, ...]
}</code></pre>
        </div>
    </div>

     <div class="endpoint">
        <h3><span class="request-type">POST</span> <span class="url">/kapi/services/kdb/databases/{db_name}/collections/{collection_name}/documents</span></h3>
        <p>Insert a document into a collection.</p>
        <div class="request">
            <h4>Request</h4>
            <p><strong>Method:</strong> <code>POST</code></p>
            <div class="headers">
                <p><strong>Headers:</strong> <code>X-API-Key: <your_api_key></code></p>
            </div>
            <div class="url-params">
                 <p><strong>URL Parameters:</strong> <code>db_name</code> (database name), <code>collection_name</code> (collection name)</p>
            </div>
            <div class="body">
                <p><strong>Body:</strong></p>
                <pre><code class="request-body">{
    "field1": "value1",
    "field2": "value2",
    "...": "..."
}</code></pre>
            </div>
        </div>
        <div class="response">
            <h4>Response</h4>
            <p><span class="response-code">201 Created</span></p>
            <p><strong>Body:</strong></p>
            <pre><code class="response-body">{
    "status": "success",
    "message": "Document inserted",
    "document_id": "generated_doc_id"
}</code></pre>
        </div>
    </div>

    <div class="endpoint">
        <h3><span class="request-type">GET</span> <span class="url">/kapi/services/kdb/databases/{db_name}/collections/{collection_name}/documents/{doc_id}</span></h3>
        <p>Get a document by its ID.</p>
        <div class="request">
            <h4>Request</h4>
            <p><strong>Method:</strong> <code>GET</code></p>
            <div class="headers">
                <p><strong>Headers:</strong> <code>X-API-Key: <your_api_key></code></p>
            </div>
            <div class="url-params">
                 <p><strong>URL Parameters:</strong> <code>db_name</code> (database name), <code>collection_name</code> (collection name), <code>doc_id</code> (document ID)</p>
            </div>
        </div>
        <div class="response">
            <h4>Response</h4>
            <p><span class="response-code">200 OK</span></p>
            <p><strong>Body:</strong></p>
            <pre><code class="response-body">{
    "status": "success",
    "message": "Document found.",
    "document": {}
}</code></pre>
        </div>
    </div>

    <div class="endpoint">
        <h3><span class="request-type">PUT</span> <span class="url">/kapi/services/kdb/databases/{db_name}/collections/{collection_name}/documents/{doc_id}</span></h3>
        <p>Update a document by its ID.</p>
        <div class="request">
            <h4>Request</h4>
            <p><strong>Method:</strong> <code>PUT</code></p>
            <div class="headers">
                <p><strong>Headers:</strong> <code>X-API-Key: <your_api_key></code></p>
            </div>
            <div class="url-params">
                 <p><strong>URL Parameters:</strong> <code>db_name</code> (database name), <code>collection_name</code> (collection name), <code>doc_id</code> (document ID)</p>
            </div>
            <div class="body">
                <p><strong>Body:</strong></p>
                <pre><code class="request-body">{
    "fieldToUpdate": "newValue",
    "...": "..."
}</code></pre>
            </div>
        </div>
        <div class="response">
            <h4>Response</h4>
            <p><span class="response-code">200 OK</span></p>
            <p><strong>Body:</strong></p>
            <pre><code class="response-body">{
    "status": "success",
    "message": "Document updated."
}</code></pre>
        </div>
    </div>

    <div class="endpoint">
        <h3><span class="request-type">DELETE</span> <span class="url">/kapi/services/kdb/databases/{db_name}/collections/{collection_name}/documents/{doc_id}</span></h3>
        <p>Delete a document by its ID.</p>
        <div class="request">
            <h4>Request</h4>
            <p><strong>Method:</strong> <code>DELETE</code></p>
            <div class="headers">
                <p><strong>Headers:</strong> <code>X-API-Key: <your_api_key></code></p>
            </div>
            <div class="url-params">
                 <p><strong>URL Parameters:</strong> <code>db_name</code> (database name), <code>collection_name</code> (collection name), <code>doc_id</code> (document ID)</p>
            </div>
        </div>
        <div class="response">
            <h4>Response</h4>
            <p><span class="response-code">200 OK</span></p>
            <p><strong>Body:</strong></p>
            <pre><code class="response-body">{
    "status": "success",
    "message": "Document deleted."
}</code></pre>
        </div>
    </div>


    </body>
    </html>
    """
    return documentation_html, 200, {'Content-Type': 'text/html'}


def main():
    parser = argparse.ArgumentParser(description="KaedeDB Command Line Interface")
    subparsers = parser.add_subparsers(title='commands', dest='command', help='Available commands')

    # 'serve' subcommand
    serve_parser = subparsers.add_parser('serve', help='Start the KaedeDB server')
    serve_parser.add_argument('--host', type=str, default='0.0.0.0', help='Host IP to bind to (default: 0.0.0.0)')
    serve_parser.add_argument('--port', type=int, default=DEFAULT_PORT, help=f'Port to listen on (default: {DEFAULT_PORT})')
    serve_parser.add_argument('--storage-path', type=str, default=DEFAULT_STORAGE_PATH, help=f'Path to store KDB files (default: "{DEFAULT_STORAGE_PATH}")')
    serve_parser.add_argument('--set-authentication', type=str, default=str(DEFAULT_AUTHENTICATION), choices=['true', 'false'], help=f'Enable API Key authentication (default: {DEFAULT_AUTHENTICATION})')
    serve_parser.add_argument('--default-db', type=str, default="my_database.kdb", help='Filename for the default database (.kdb extension, default: my_database.kdb)')  # Added --default-db argument
    # Add more arguments to 'serve' parser here if needed

    args = parser.parse_args()

    if args.command == 'serve':
        # Construct db_file path using --default-db argument
        db_file = os.path.join(args.storage_path, args.default_db)  # Use args.default_db
        global TOKENS_FILE
        TOKENS_FILE = os.path.join(args.storage_path, TOKENS_FILE_DEFAULT_NAME)
        global API_KEYS
        API_KEYS = load_api_keys()

        global DATABASE_ENGINE
        DATABASE_ENGINE = KDBEngine(db_file)

        authentication_enabled = args.set_authentication.lower() == 'true'

        if authentication_enabled:
            app.before_request(authenticate_request)
        else:
            app.view_functions['generate_token'] = lambda: jsonify({"error": "Token generation disabled"}), 405
            if authenticate_request in app.before_request_funcs.get(None, []):
                app.before_request_funcs[None].remove(authenticate_request)

        print(f"Starting KaedeDB Server (serve command) with:")
        print(f"  Host: {args.host}")
        print(f"  Port: {args.port}")
        print(f"  Storage Path: {args.storage_path}")
        print(f"  Authentication: {'Enabled' if authentication_enabled else 'Disabled'}")
        print(f"  Database File: {args.default_db}")  # Display the database filename

        app.run(host=args.host, port=args.port, debug=True)
    elif args.command is None:
        parser.print_help()
    else:
        print(f"Unknown command: {args.command}")
        parser.print_help()


if __name__ == '__main__':
    main()