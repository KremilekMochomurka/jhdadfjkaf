import os
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from datetime import datetime, timezone
import uuid
import logging
import concurrent.futures
from werkzeug.utils import secure_filename
from convertor.core import process_file # Import the processing function
from convertor.file_splitter import split_file, should_split_file, cleanup_temp_files # Import file splitting functions

# Load environment variables (e.g., for API keys)
load_dotenv()

# --- Configuration ---
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, os.environ.get('UPLOAD_FOLDER', 'instance/uploads'))

# Handle database path
db_url = os.environ.get('DATABASE_URL', 'sqlite:///instance/documents.db')
if db_url.startswith('sqlite:///'):
    # For SQLite, convert the URL to a file path
    DATABASE_PATH = os.path.join(BASE_DIR, db_url.replace('sqlite:///', ''))
else:
    # For other databases, keep the URL as is
    DATABASE_PATH = db_url

# Create necessary directories
if not os.path.exists(os.path.join(BASE_DIR, 'instance')):
    os.makedirs(os.path.join(BASE_DIR, 'instance'))
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Parse allowed extensions from environment variable
ALLOWED_EXTENSIONS = os.environ.get('ALLOWED_EXTENSIONS', 'pdf,docx,doc,txt,jpg,jpeg,png').split(',')

# --- App Initialization ---
# Configure logging for Flask app
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')
app_logger = logging.getLogger(__name__) # Use Flask's logger or a specific one

app = Flask(__name__, instance_relative_config=True)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')

# Configure database URI
if db_url.startswith('sqlite:///'):
    # For SQLite, ensure the path is absolute
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DATABASE_PATH}'
else:
    # For other databases, use the URL as is
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = int(os.environ.get('MAX_CONTENT_LENGTH', 100 * 1024 * 1024))  # Default: 100MB
app.config['MAX_WORKERS'] = int(os.environ.get('MAX_WORKERS', 4))  # Default: 4 workers
app.config['FLASK_ENV'] = os.environ.get('FLASK_ENV', 'development')
app.config['FLASK_DEBUG'] = os.environ.get('FLASK_DEBUG', '1') == '1'

# Configure rate limiting if enabled
if os.environ.get('RATE_LIMIT_WINDOW_MS') and os.environ.get('RATE_LIMIT_MAX_REQUESTS'):
    app.config['RATE_LIMIT_WINDOW_MS'] = int(os.environ.get('RATE_LIMIT_WINDOW_MS'))
    app.config['RATE_LIMIT_MAX_REQUESTS'] = int(os.environ.get('RATE_LIMIT_MAX_REQUESTS'))

db = SQLAlchemy(app)

# Create a thread pool executor for file processing
executor = concurrent.futures.ThreadPoolExecutor(max_workers=app.config['MAX_WORKERS'])

# --- Database Models ---
class Folder(db.Model):
    """Model pro složky dokumentů."""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, index=True)  # Indexujeme pro rychlé vyhledávání podle názvu
    description = db.Column(db.Text, nullable=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('folder.id'), nullable=True, index=True)  # Indexujeme pro rychlé hledání podsložek
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), index=True)  # Indexujeme pro řazení
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    folder_type = db.Column(db.String(50), default='general', index=True)  # 'email', 'know_how', 'general'

    # Vztahy
    documents = db.relationship('UserDocument', backref='folder', lazy='dynamic')
    subfolders = db.relationship('Folder', backref=db.backref('parent_folder', remote_side=[id]), lazy='dynamic')

    def __repr__(self):
        return f'<Folder {self.id}: {self.name} ({self.folder_type})>'

    def to_dict(self):
        """Převede složku na slovník pro JSON odpověď."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'parent_id': self.parent_id,
            'folder_type': self.folder_type,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'document_count': self.documents.count(),
            'subfolder_count': self.subfolders.count()
        }

class UserDocument(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original_filename = db.Column(db.String(255), nullable=False)
    stored_filename = db.Column(db.String(255), unique=True, nullable=False) # UUID or secure name
    upload_time = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), index=True)  # Indexujeme pro rychlé řazení
    status = db.Column(db.String(50), default='pending', index=True) # e.g., pending, processing, completed, error, warning
    processed_content = db.Column(db.Text, nullable=True)
    error_message = db.Column(db.Text, nullable=True)
    # Nové sloupce pro rozdělené soubory
    is_split = db.Column(db.Boolean, default=False, index=True) # Označuje, zda byl soubor rozdělen na části
    split_folder = db.Column(db.String(255), nullable=True) # Cesta ke složce s rozdělenými částmi
    parent_id = db.Column(db.Integer, db.ForeignKey('user_document.id'), nullable=True, index=True) # Odkaz na rodičovský dokument
    part_number = db.Column(db.Integer, nullable=True) # Číslo části, pokud je to část rozděleného souboru
    total_parts = db.Column(db.Integer, nullable=True) # Celkový počet částí
    # Nové sloupce pro kategorizaci a třídění
    content_type = db.Column(db.String(50), default='unknown', index=True)  # 'email', 'know_how', 'general', 'unknown'
    folder_id = db.Column(db.Integer, db.ForeignKey('folder.id'), nullable=True, index=True)  # Odkaz na složku
    tags = db.Column(db.String(500), nullable=True)  # Tagy oddělené čárkami
    # user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False) # Add later with user auth

    # Vztah pro přístup k částem rozděleného souboru
    parts = db.relationship('UserDocument', backref=db.backref('parent', remote_side=[id]),
                           lazy='dynamic')

    def __repr__(self):
        if self.is_split:
            return f'<UserDocument {self.id}: {self.original_filename} ({self.status}) - Split into {self.total_parts} parts>'
        elif self.parent_id:
            return f'<UserDocument {self.id}: {self.original_filename} ({self.status}) - Part {self.part_number} of {self.total_parts}>'
        else:
            return f'<UserDocument {self.id}: {self.original_filename} ({self.status})>'

    def to_dict(self):
        """Převede dokument na slovník pro JSON odpověď."""
        result = {
            'id': self.id,
            'original_filename': self.original_filename,
            'status': self.status,
            'upload_time': self.upload_time.isoformat(),
            'content_type': self.content_type,
            'folder_id': self.folder_id,
            'tags': self.tags.split(',') if self.tags else []
        }

        if self.status in ['completed', 'warning']:
            # Přidáme zkrácenou verzi obsahu pro náhled
            if self.processed_content:
                if len(self.processed_content) > 200:
                    result['content_preview'] = self.processed_content[:200] + '...'
                else:
                    result['content_preview'] = self.processed_content

        if self.error_message:
            result['error_message'] = self.error_message

        # Informace o rozdělených souborech
        if self.is_split:
            result['is_split'] = True
            result['total_parts'] = self.total_parts
        elif self.parent_id:
            result['is_part'] = True
            result['part_number'] = self.part_number
            result['total_parts'] = self.total_parts
            result['parent_id'] = self.parent_id

        return result

# --- Helper Functions ---
def detect_content_type(document):
    """
    Detekuje typ obsahu dokumentu na základě jeho zpracovaného obsahu a přiřadí ho do odpovídající složky.

    Args:
        document: Instance modelu UserDocument
    """
    if not document.processed_content:
        document.content_type = 'unknown'
        return

    content = document.processed_content.lower()

    # Detekce emailové korespondence
    if content.startswith('{') and ('type":"email_correspondence"' in content or '"emails":' in content) or \
       any(keyword in content for keyword in ['od:', 'odesílatel:', 'from:', 'komu:', 'to:', 'předmět:', 'subject:']):
        document.content_type = 'email'
        app_logger.info(f"Detected email correspondence in document ID {document.id}")

        # Automatické přiřazení do složky pro emaily
        try:
            email_folder = Folder.query.filter_by(folder_type='email').first()
            if email_folder:
                document.folder_id = email_folder.id
                app_logger.info(f"Automatically assigned document ID {document.id} to email folder ID {email_folder.id}")
        except Exception as e:
            app_logger.error(f"Error assigning document to email folder: {e}")

    # Detekce firemního know-how
    elif any(keyword in content for keyword in ['postup', 'návod', 'how to', 'guide', 'tutorial', 'dokumentace',
                                               'documentation', 'firemní', 'společnost', 'proces', 'procedura',
                                               'personální', 'zaměstnanec', 'pracovník', 'mzda', 'plat', 'dovolená',
                                               'školení', 'nábor', 'pohovor', 'hr', 'human resources']):
        document.content_type = 'company_know_how'
        app_logger.info(f"Detected company know-how content in document ID {document.id}")

        # Automatické přiřazení do složky pro firemní know-how
        try:
            company_folder = Folder.query.filter_by(folder_type='company_know_how').first()
            if company_folder:
                document.folder_id = company_folder.id
                app_logger.info(f"Automatically assigned document ID {document.id} to company know-how folder ID {company_folder.id}")
        except Exception as e:
            app_logger.error(f"Error assigning document to company know-how folder: {e}")

    # Detekce tabulkových dat a obecný obsah - přiřadíme do firemního know-how
    else:
        if '|' in content and '---' in content:
            document.content_type = 'table'
            app_logger.info(f"Detected tabular data in document ID {document.id}")
        else:
            document.content_type = 'general'
            app_logger.info(f"Assigned general content type to document ID {document.id}")

        # Přiřazení do firemního know-how (všechny ostatní dokumenty)
        try:
            company_folder = Folder.query.filter_by(folder_type='company_know_how').first()
            if company_folder:
                document.folder_id = company_folder.id
                app_logger.info(f"Automatically assigned document ID {document.id} to company know-how folder ID {company_folder.id}")
        except Exception as e:
            app_logger.error(f"Error assigning document to company know-how folder: {e}")

# --- Context Processors ---
@app.context_processor
def inject_now():
    """Inject current datetime into template context."""
    return {'now': datetime.now(timezone.utc)}

# --- Routes ---

@app.route('/')
def index():
    """Serves the main HTML page."""
    return render_template('index.html')

@app.route('/static/<path:path>')
def send_static(path):
    """Serves static files (CSS, JS)."""
    # Security Note: In production, use a web server (Nginx/Apache) to serve static files.
    return send_from_directory('static', path)

# --- API Endpoints (Placeholders) ---

# Function to process a file in a separate thread
def process_file_async(file_path, doc_id):
    """Process a file asynchronously and update the database with the result."""
    try:
        app_logger.info(f"Starting async processing for document ID: {doc_id}")

        # Get the document from the database
        with app.app_context():
            doc = db.session.get(UserDocument, doc_id)
            if not doc:
                app_logger.error(f"Document ID {doc_id} not found for async processing")
                return

            # Update status to processing
            doc.status = 'processing'
            db.session.commit()

        # Process the file
        processing_result = process_file(file_path)
        app_logger.info(f"Async processing finished for document ID: {doc_id}. Result error: {processing_result.get('error')}")

        # Update the database with the result
        with app.app_context():
            doc_to_update = db.session.get(UserDocument, doc_id)
            if not doc_to_update:
                app_logger.error(f"Document ID {doc_id} not found after async processing")
                return

            if processing_result.get("error") and processing_result.get("content") is None:
                # Standard error case - no content
                doc_to_update.status = 'error'
                doc_to_update.error_message = processing_result["error"]
                app_logger.error(f"Processing error for doc ID {doc_id}: {processing_result['error']}")
            elif processing_result.get("error") and processing_result.get("content") is not None:
                # Special case: we have both error and content
                doc_to_update.status = 'warning'
                doc_to_update.error_message = processing_result["error"]
                doc_to_update.processed_content = processing_result["content"]
                app_logger.warning(f"Processing warning for doc ID {doc_id}: {processing_result['error']}")

                # Detekce typu obsahu - make sure this runs in app context
                detect_content_type(doc_to_update)
            else:
                # Success case
                doc_to_update.status = 'completed'
                doc_to_update.processed_content = processing_result.get("content", "[No content returned]")

                # Detekce typu obsahu - make sure this runs in app context
                detect_content_type(doc_to_update)

            db.session.commit()
            app_logger.info(f"Updated DB record for doc ID {doc_id} with status: {doc_to_update.status}")

    except Exception as e:
        app_logger.exception(f"Unhandled exception during async processing for doc ID {doc_id}: {e}")
        # Update the database with the error
        with app.app_context():
            try:
                doc = db.session.get(UserDocument, doc_id)
                if doc and doc.status != 'completed':
                    doc.status = 'error'
                    doc.error_message = f"Server error during async processing: {e}"
                    db.session.commit()
            except Exception as db_error:
                app_logger.error(f"Error updating database after async processing error: {db_error}")
    finally:
        # Clean up any temporary resources if needed
        try:
            # We need to use app context for database operations
            with app.app_context():
                # Check if the file is a temporary part file that should be cleaned up
                if doc_id:
                    doc = db.session.get(UserDocument, doc_id)
                    if doc and doc.parent_id:
                        # This is a part file, we might want to clean it up after processing
                        # For now, we'll keep it for debugging purposes
                        pass
        except Exception as cleanup_error:
            app_logger.error(f"Error during cleanup for doc ID {doc_id}: {cleanup_error}")

# Function to submit a file processing task to the thread pool
def submit_processing_task(file_path, doc_id):
    """Submit a file processing task to the thread pool executor."""
    app_logger.info(f"Submitting processing task for document ID: {doc_id}")
    return executor.submit(process_file_async, file_path, doc_id)

@app.route('/api/upload', methods=['POST'])
def upload_files():
    """Handles multiple file uploads, saves the files, and triggers parallel processing."""
    # Check if files are in the request
    if 'files[]' not in request.files:
        app_logger.warning("Upload attempt with no files part.")
        return jsonify({"error": "No files part"}), 400

    files = request.files.getlist('files[]')

    if not files or all(file.filename == '' for file in files):
        app_logger.warning("Upload attempt with no selected files.")
        return jsonify({"error": "No selected files"}), 400

    # Process each file
    uploaded_files = []
    processing_futures = []

    for file in files:
        if file and file.filename != '':
            try:
                original_filename = secure_filename(file.filename)
                # Generate a unique filename
                file_extension = os.path.splitext(original_filename)[1]
                unique_filename = f"{uuid.uuid4()}{file_extension}"
                save_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)

                # Create initial DB record
                new_doc = UserDocument(
                    original_filename=original_filename,
                    stored_filename=unique_filename,
                    status='saving'
                )
                db.session.add(new_doc)
                db.session.commit()
                doc_id = new_doc.id
                app_logger.info(f"Created initial DB record for {original_filename} (ID: {doc_id})")

                # Save the file
                file.save(save_path)
                app_logger.info(f"File {original_filename} saved as {unique_filename} at {save_path}")

                # Check if the file should be split
                should_split, reason = should_split_file(save_path)

                if should_split:
                    app_logger.info(f"Soubor {original_filename} bude rozdělen: {reason}")

                    # Update status to indicate splitting
                    new_doc.status = 'splitting'
                    db.session.commit()

                    try:
                        # Split the file
                        split_folder, part_files, num_chunks = split_file(save_path, app.config['UPLOAD_FOLDER'])

                        if split_folder and part_files and num_chunks > 0:
                            # Update the parent document
                            new_doc.is_split = True
                            new_doc.split_folder = split_folder
                            new_doc.total_parts = num_chunks
                            new_doc.status = 'split'
                            db.session.commit()

                            # Create document records for each part
                            part_doc_ids = []
                            for i, part_file in enumerate(part_files):
                                part_filename = os.path.basename(part_file)
                                part_original_filename = f"{original_filename} (Část {i+1}/{num_chunks})"

                                # Create DB record for the part
                                part_doc = UserDocument(
                                    original_filename=part_original_filename,
                                    stored_filename=part_filename,
                                    status='pending',
                                    parent_id=doc_id,
                                    part_number=i+1,
                                    total_parts=num_chunks
                                )
                                db.session.add(part_doc)
                                db.session.commit()
                                part_doc_id = part_doc.id
                                part_doc_ids.append(part_doc_id)

                                # Submit task to thread pool
                                future = submit_processing_task(part_file, part_doc_id)
                                processing_futures.append(future)

                                app_logger.info(f"Zpracování části {i+1}/{num_chunks} souboru {original_filename} zahájeno (ID: {part_doc_id})")

                            # Add to the list of uploaded files
                            uploaded_files.append({
                                "original_filename": original_filename,
                                "doc_id": doc_id,
                                "status": "split",
                                "parts": num_chunks,
                                "part_ids": part_doc_ids
                            })
                        else:
                            # Splitting failed, process the original file
                            app_logger.warning(f"Rozdělení souboru {original_filename} selhalo, zpracování původního souboru")
                            new_doc.status = 'pending'
                            db.session.commit()

                            # Submit task to thread pool
                            future = submit_processing_task(save_path, doc_id)
                            processing_futures.append(future)

                            # Add to the list of uploaded files
                            uploaded_files.append({
                                "original_filename": original_filename,
                                "doc_id": doc_id,
                                "status": "pending"
                            })
                    except Exception as split_error:
                        app_logger.error(f"Chyba při rozdělování souboru {original_filename}: {split_error}")
                        # Process the original file instead
                        new_doc.status = 'pending'
                        db.session.commit()

                        # Submit task to thread pool
                        future = submit_processing_task(save_path, doc_id)
                        processing_futures.append(future)

                        # Add to the list of uploaded files
                        uploaded_files.append({
                            "original_filename": original_filename,
                            "doc_id": doc_id,
                            "status": "pending",
                            "warning": f"Rozdělení souboru selhalo: {str(split_error)}"
                        })
                else:
                    # Update status to pending
                    new_doc.status = 'pending'
                    db.session.commit()

                    # Submit task to thread pool
                    future = submit_processing_task(save_path, doc_id)
                    processing_futures.append(future)

                    # Add to the list of uploaded files
                    uploaded_files.append({
                        "original_filename": original_filename,
                        "doc_id": doc_id,
                        "status": "pending"
                    })

            except Exception as e:
                db.session.rollback()
                app_logger.exception(f"Unhandled exception during file upload for {file.filename}:")

                # Try to clean up DB entry if it exists
                if 'new_doc' in locals() and hasattr(new_doc, 'id') and new_doc.id:
                    try:
                        doc = db.session.get(UserDocument, new_doc.id)
                        if doc and doc.status != 'completed':
                            doc.status = 'error'
                            doc.error_message = f"Server error during upload: {e}"
                            db.session.commit()
                    except Exception as db_error:
                        app_logger.error(f"Error updating database after upload error: {db_error}")

                # Add error to the list
                uploaded_files.append({
                    "original_filename": file.filename,
                    "error": str(e),
                    "status": "error"
                })

    # Return information about all uploaded files
    return jsonify({
        "message": f"{len(uploaded_files)} files uploaded and processing started.",
        "files": uploaded_files
    }), 202  # 202 Accepted - processing has started but not completed

@app.route('/api/documents', methods=['GET'])
def list_documents():
    """Lists processed documents for the user."""
    # 1. Check if user is authenticated (add later)
    # 2. Query DB for documents belonging to the user
    # 3. Return list of document metadata (id, name, status, upload_time)
    try:
        # Získání parametrů pro filtrování a stránkování
        show_parts = request.args.get('show_parts', 'false').lower() == 'true'
        folder_id = request.args.get('folder_id')
        content_type = request.args.get('content_type')
        status = request.args.get('status')
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)  # Omezení počtu dokumentů na stránku

        # Optimalizace: Omezení maximálního počtu dokumentů na stránku
        if per_page > 100:
            per_page = 100

        # Základní dotaz s optimalizací - vybíráme jen potřebné sloupce
        query = UserDocument.query

        # Filtrování částí rozdělených souborů, pokud není požadováno jejich zobrazení
        if not show_parts:
            query = query.filter(UserDocument.parent_id == None)

        # Filtrování podle složky
        if folder_id:
            if folder_id == 'null':
                query = query.filter(UserDocument.folder_id == None)
            else:
                query = query.filter(UserDocument.folder_id == int(folder_id))

        # Filtrování podle typu obsahu
        if content_type:
            query = query.filter(UserDocument.content_type == content_type)

        # Filtrování podle stavu
        if status:
            query = query.filter(UserDocument.status == status)

        # Seřazení podle času nahrání
        query = query.order_by(UserDocument.upload_time.desc())

        # Stránkování pro optimalizaci výkonu
        paginated_docs = query.paginate(page=page, per_page=per_page, error_out=False)

        # Optimalizace: Předem načteme všechny části dokumentů v jednom dotazu, pokud jsou požadovány
        parts_by_parent = {}
        if show_parts:
            parent_ids = [doc.id for doc in paginated_docs.items if doc.is_split]
            if parent_ids:
                parts = UserDocument.query.filter(UserDocument.parent_id.in_(parent_ids)).order_by(UserDocument.part_number).all()
                for part in parts:
                    if part.parent_id not in parts_by_parent:
                        parts_by_parent[part.parent_id] = []
                    parts_by_parent[part.parent_id].append(part)

        # Vytvoření seznamu dokumentů
        doc_list = []
        for doc in paginated_docs.items:
            doc_info = {
                "id": doc.id,
                "original_filename": doc.original_filename,
                "status": doc.status,
                "upload_time": doc.upload_time.isoformat(),
                "content_type": doc.content_type,
                "folder_id": doc.folder_id
            }

            # Přidání informací o rozdělených souborech
            if doc.is_split:
                doc_info["is_split"] = True
                doc_info["total_parts"] = doc.total_parts

                # Přidání informací o částech, pokud jsou požadovány
                if show_parts and doc.id in parts_by_parent:
                    doc_info["parts"] = [{
                        "id": part.id,
                        "part_number": part.part_number,
                        "status": part.status
                    } for part in parts_by_parent[doc.id]]
            elif doc.parent_id:
                # Toto je část rozděleného dokumentu
                doc_info["is_part"] = True
                doc_info["part_number"] = doc.part_number
                doc_info["total_parts"] = doc.total_parts
                doc_info["parent_id"] = doc.parent_id

            doc_list.append(doc_info)

        # Přidání informací o stránkování
        pagination_info = {
            "total_items": paginated_docs.total,
            "total_pages": paginated_docs.pages,
            "current_page": page,
            "per_page": per_page,
            "has_next": paginated_docs.has_next,
            "has_prev": paginated_docs.has_prev
        }

        return jsonify({
            "documents": doc_list,
            "pagination": pagination_info
        })
    except Exception as e:
        app_logger.error(f"Error fetching documents: {e}")
        return jsonify({"error": "Could not retrieve documents"}), 500


@app.route('/api/documents/<int:doc_id>', methods=['GET'])
def get_document_details(doc_id):
    """Gets details/content of a specific processed document."""
    # 1. Check if user is authenticated and owns the document (add later)
    # 2. Query DB for the specific document
    # 3. Return full document details including processed_content if 'completed'
    # Placeholder implementation:
    doc = db.get_or_404(UserDocument, doc_id)
    # TODO: Add ownership check

    # Základní informace o dokumentu
    result = {
        "id": doc.id,
        "original_filename": doc.original_filename,
        "status": doc.status,
        "upload_time": doc.upload_time.isoformat(),
        "processed_content": doc.processed_content if doc.status in ['completed', 'warning'] else None,
        "error_message": doc.error_message if doc.status in ['error', 'warning'] else None
    }

    # Přidání informací o rozdělených souborech
    if doc.is_split:
        # Dokument byl rozdělen na části
        parts = UserDocument.query.filter_by(parent_id=doc.id).order_by(UserDocument.part_number).all()
        result["is_split"] = True
        result["total_parts"] = doc.total_parts
        result["parts"] = [{
            "id": part.id,
            "part_number": part.part_number,
            "status": part.status,
            "original_filename": part.original_filename
        } for part in parts]
    elif doc.parent_id:
        # Toto je část rozděleného dokumentu
        parent = UserDocument.query.get(doc.parent_id)
        result["is_part"] = True
        result["part_number"] = doc.part_number
        result["total_parts"] = doc.total_parts
        result["parent_id"] = doc.parent_id
        result["parent_filename"] = parent.original_filename if parent else "Unknown"

    return jsonify(result)

@app.route('/api/documents/<int:doc_id>', methods=['PUT', 'PATCH'])
def update_document(doc_id):
    """Updates a document's content and/or filename."""
    # 1. Check if user is authenticated and owns the document (add later)
    # 2. Query DB for the specific document
    # 3. Update document details

    doc = db.get_or_404(UserDocument, doc_id)
    # TODO: Add ownership check

    # Get request data
    data = request.json

    try:
        # Update document filename if provided
        if 'original_filename' in data and data['original_filename']:
            old_filename = doc.original_filename
            doc.original_filename = data['original_filename']
            app_logger.info(f"Renamed document {doc_id} from '{old_filename}' to '{doc.original_filename}'")

        # Update document content if provided
        if 'processed_content' in data and doc.status in ['completed', 'warning']:
            doc.processed_content = data['processed_content']
            app_logger.info(f"Updated content for document {doc_id}")

        # Save changes
        db.session.commit()

        return jsonify({
            "id": doc.id,
            "original_filename": doc.original_filename,
            "status": doc.status,
            "message": "Document updated successfully"
        }), 200

    except Exception as e:
        db.session.rollback()
        app_logger.error(f"Error updating document {doc_id}: {e}")
        return jsonify({"error": "Failed to update document"}), 500

# --- Folder API Endpoints ---
@app.route('/api/folders', methods=['GET'])
@app.route('/api/folders/', methods=['GET'])  # Přidáno pro kompatibilitu s klienty, kteří používají lomítko na konci
def list_folders():
    """Vrátí seznam všech složek."""
    try:
        # Získání parametru pro filtrování podle typu složky
        folder_type = request.args.get('type')
        parent_id = request.args.get('parent_id')

        # Základní dotaz
        query = Folder.query

        # Filtrování podle typu složky
        if folder_type:
            query = query.filter_by(folder_type=folder_type)

        # Filtrování podle nadřazené složky
        if parent_id:
            if parent_id == 'null':
                # Vrátit pouze kořenové složky
                query = query.filter(Folder.parent_id == None)
            else:
                # Vrátit podsložky konkrétní složky
                query = query.filter_by(parent_id=int(parent_id))

        # Seřazení podle názvu
        query = query.order_by(Folder.name)

        # Získání složek
        folders = query.all()

        # Převod na seznam slovníků
        folder_list = [folder.to_dict() for folder in folders]

        return jsonify(folder_list)
    except Exception as e:
        app_logger.error(f"Error fetching folders: {e}")
        return jsonify({"error": "Could not retrieve folders"}), 500

@app.route('/api/folders', methods=['POST'])
@app.route('/api/folders/', methods=['POST'])  # Přidáno pro kompatibilitu s klienty, kteří používají lomítko na konci
def create_folder():
    """Vytvoří novou složku."""
    try:
        # Získání dat z požadavku
        data = request.json

        # Kontrola povinných polí
        if not data or 'name' not in data:
            return jsonify({"error": "Folder name is required"}), 400

        # Vytvoření nové složky
        new_folder = Folder(
            name=data['name'],
            description=data.get('description'),
            parent_id=data.get('parent_id'),
            folder_type=data.get('folder_type', 'general')
        )

        # Uložení do databáze
        db.session.add(new_folder)
        db.session.commit()

        app_logger.info(f"Created new folder: {new_folder.name} (ID: {new_folder.id})")

        return jsonify(new_folder.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        app_logger.error(f"Error creating folder: {e}")
        return jsonify({"error": "Could not create folder"}), 500

@app.route('/api/folders/<int:folder_id>', methods=['GET'])
def get_folder_details(folder_id):
    """Vrátí detaily konkrétní složky včetně dokumentů a podsložek."""
    try:
        folder = db.get_or_404(Folder, folder_id)

        # Základní informace o složce
        result = folder.to_dict()

        # Přidání seznamu dokumentů ve složce
        documents = UserDocument.query.filter_by(folder_id=folder_id).all()
        result['documents'] = [doc.to_dict() for doc in documents]

        # Přidání seznamu podsložek
        subfolders = Folder.query.filter_by(parent_id=folder_id).all()
        result['subfolders'] = [subfolder.to_dict() for subfolder in subfolders]

        return jsonify(result)
    except Exception as e:
        app_logger.error(f"Error fetching folder details: {e}")
        return jsonify({"error": "Could not retrieve folder details"}), 500

@app.route('/api/folders/<int:folder_id>', methods=['PUT', 'PATCH'])
def update_folder(folder_id):
    """Aktualizuje existující složku."""
    try:
        folder = db.get_or_404(Folder, folder_id)

        # Získání dat z požadavku
        data = request.json

        # Aktualizace polí
        if 'name' in data:
            folder.name = data['name']
        if 'description' in data:
            folder.description = data['description']
        if 'parent_id' in data:
            folder.parent_id = data['parent_id']
        if 'folder_type' in data:
            folder.folder_type = data['folder_type']

        # Aktualizace času poslední změny
        folder.updated_at = datetime.now(timezone.utc)

        # Uložení změn
        db.session.commit()

        app_logger.info(f"Updated folder ID {folder_id}: {folder.name}")

        return jsonify(folder.to_dict())
    except Exception as e:
        db.session.rollback()
        app_logger.error(f"Error updating folder: {e}")
        return jsonify({"error": "Could not update folder"}), 500

@app.route('/api/folders/<int:folder_id>', methods=['DELETE'])
def delete_folder(folder_id):
    """Smaže složku a přesune její dokumenty do nadřazené složky."""
    try:
        folder = db.get_or_404(Folder, folder_id)

        # Získání dokumentů ve složce
        documents = UserDocument.query.filter_by(folder_id=folder_id).all()

        # Přesun dokumentů do nadřazené složky nebo nastavení folder_id na None
        for doc in documents:
            doc.folder_id = folder.parent_id  # Může být None, pokud složka nemá nadřazenou složku

        # Získání podsložek
        subfolders = Folder.query.filter_by(parent_id=folder_id).all()

        # Přesun podsložek do nadřazené složky nebo nastavení parent_id na None
        for subfolder in subfolders:
            subfolder.parent_id = folder.parent_id

        # Smazání složky
        db.session.delete(folder)
        db.session.commit()

        app_logger.info(f"Deleted folder ID {folder_id}: {folder.name}")

        return jsonify({"message": f"Folder '{folder.name}' deleted successfully"})
    except Exception as e:
        db.session.rollback()
        app_logger.error(f"Error deleting folder: {e}")
        return jsonify({"error": "Could not delete folder"}), 500

@app.route('/api/documents/<int:doc_id>/move', methods=['POST'])
def move_document(doc_id):
    """Přesune dokument do jiné složky."""
    try:
        doc = db.get_or_404(UserDocument, doc_id)

        # Získání dat z požadavku
        data = request.json

        if 'folder_id' not in data:
            return jsonify({"error": "Folder ID is required"}), 400

        # Kontrola, zda cílová složka existuje (pokud není None)
        target_folder_id = data['folder_id']
        if target_folder_id is not None:
            target_folder = db.session.get(Folder, target_folder_id)
            if not target_folder:
                return jsonify({"error": "Target folder does not exist"}), 404

        # Aktualizace složky dokumentu
        old_folder_id = doc.folder_id
        doc.folder_id = target_folder_id

        # Aktualizace typu obsahu, pokud je poskytnut
        if 'content_type' in data:
            doc.content_type = data['content_type']

        # Aktualizace tagů, pokud jsou poskytnuty
        if 'tags' in data:
            if isinstance(data['tags'], list):
                doc.tags = ','.join(data['tags'])
            else:
                doc.tags = data['tags']

        # Uložení změn
        db.session.commit()

        app_logger.info(f"Moved document ID {doc_id} from folder ID {old_folder_id} to folder ID {target_folder_id}")

        return jsonify(doc.to_dict())
    except Exception as e:
        db.session.rollback()
        app_logger.error(f"Error moving document: {e}")
        return jsonify({"error": "Could not move document"}), 500

@app.route('/api/documents/<int:doc_id>', methods=['DELETE'])
def delete_document(doc_id):
    """Deletes a document record and its associated file."""
    # TODO: Add ownership check
    doc = db.get_or_404(UserDocument, doc_id)
    try:
        # Kontrola, zda je dokument rozdělen na části
        if doc.is_split:
            # Získání všech částí dokumentu
            parts = UserDocument.query.filter_by(parent_id=doc.id).all()

            # Smazání všech částí
            for part in parts:
                # Smazání souboru části
                part_path = os.path.join(app.config['UPLOAD_FOLDER'], part.stored_filename)
                if os.path.exists(part_path):
                    try:
                        os.remove(part_path)
                        app_logger.info(f"Deleted part file: {part_path}")
                    except OSError as e:
                        app_logger.error(f"Error deleting part file {part_path}: {e}")

                # Smazání záznamu části
                db.session.delete(part)
                app_logger.info(f"Deleted part document record ID: {part.id}")

            # Smazání složky s částmi, pokud existuje
            if doc.split_folder and os.path.exists(doc.split_folder):
                try:
                    import shutil
                    shutil.rmtree(doc.split_folder)
                    app_logger.info(f"Deleted split folder: {doc.split_folder}")
                except OSError as e:
                    app_logger.error(f"Error deleting split folder {doc.split_folder}: {e}")

        # Kontrola, zda je dokument částí rozděleného dokumentu
        elif doc.parent_id:
            # Pokud je to poslední část, aktualizujeme rodičovský dokument
            parent = db.session.get(UserDocument, doc.parent_id)
            if parent:
                remaining_parts = UserDocument.query.filter_by(parent_id=doc.parent_id).count()
                if remaining_parts <= 1:  # Tato část je poslední
                    parent.status = 'incomplete'
                    app_logger.info(f"Updated parent document {parent.id} status to 'incomplete' (all parts deleted)")

        # Attempt to delete the file from the filesystem
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], doc.stored_filename)
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                app_logger.info(f"Deleted file: {file_path}")
            except OSError as e:
                # Log the error but proceed with DB deletion
                app_logger.error(f"Error deleting file {file_path}: {e}")
        else:
            app_logger.warning(f"File not found for deletion, proceeding with DB record removal: {file_path}")

        # Delete the database record
        db.session.delete(doc)
        db.session.commit()
        app_logger.info(f"Deleted document record ID: {doc_id}")
        return jsonify({"message": "Document deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        app_logger.error(f"Error deleting document {doc_id}: {e}")
        return jsonify({"error": "Failed to delete document"}), 500


# Endpoint removed - duplicated with the one above


@app.route('/api/documents/<int:doc_id>/status', methods=['GET'])
def get_document_status(doc_id):
    """Gets the processing status of a specific document (useful for async polling)."""
    # 1. Check if user is authenticated and owns the document (add later)
    # 2. Query DB for the document status
    # 3. Return status information
    # Placeholder implementation:
    doc = db.get_or_404(UserDocument, doc_id)
    # TODO: Add ownership check
    return jsonify({
        "id": doc.id,
        "status": doc.status,
        "error_message": doc.error_message if doc.status == 'error' else None
    })

# --- Initialization ---
def init_default_folders():
    """Vytvoří výchozí složky a odstraní nepotřebné složky."""
    with app.app_context():
        # Vytvoření tabulek, pokud neexistují
        db.create_all()

        # Definice výchozích složek - pouze dvě požadované
        default_folders = [
            {
                'name': 'Emailová korespondence',
                'description': 'Složka pro emailovou korespondenci',
                'folder_type': 'email'
            },
            {
                'name': 'Firemní know-how',
                'description': 'Složka pro firemní dokumentaci, návody a postupy',
                'folder_type': 'company_know_how'
            }
        ]

        # Seznam povolených typů složek
        allowed_folder_types = ['email', 'company_know_how']

        # Odstranění nepotřebných složek
        folders_to_remove = Folder.query.filter(~Folder.folder_type.in_(allowed_folder_types)).all()
        for folder in folders_to_remove:
            # Přesunout dokumenty do složky Firemní know-how
            company_folder = Folder.query.filter_by(folder_type='company_know_how').first()
            if company_folder:
                # Přesunout dokumenty do složky Firemní know-how
                docs = UserDocument.query.filter_by(folder_id=folder.id).all()
                for doc in docs:
                    doc.folder_id = company_folder.id
                    app_logger.info(f"Moved document ID {doc.id} from folder '{folder.name}' to 'Firemní know-how'")

            # Odstranit složku
            app_logger.info(f"Removing unnecessary folder: {folder.name}")
            db.session.delete(folder)

        # Vytvoření složek, pokud neexistují
        for folder_data in default_folders:
            folder = Folder.query.filter_by(folder_type=folder_data['folder_type']).first()
            if not folder:
                folder = Folder(
                    name=folder_data['name'],
                    description=folder_data['description'],
                    folder_type=folder_data['folder_type']
                )
                db.session.add(folder)
                app_logger.info(f"Created default folder: {folder_data['name']}")

        # Uložení změn
        db.session.commit()

# Inicializace databáze
with app.app_context():
    db.create_all() # Create database tables if they don't exist

# Funkce pro pravidelné čištění dočasných souborů
def schedule_cleanup():
    """Spustí pravidelné čištění dočasných souborů."""
    import threading
    import time

    def cleanup_task():
        while True:
            try:
                app_logger.info("Spouštím pravidelné čištění dočasných souborů...")
                cleanup_temp_files(app.config['UPLOAD_FOLDER'], max_age_hours=24)
                app_logger.info("Čištění dočasných souborů dokončeno.")
            except Exception as e:
                app_logger.error(f"Chyba při čištění dočasných souborů: {e}")

            # Počkáme 6 hodin před dalším čištěním
            time.sleep(6 * 60 * 60)

    # Spustíme čištění v samostatném vlákně
    cleanup_thread = threading.Thread(target=cleanup_task)
    cleanup_thread.daemon = True
    cleanup_thread.start()
    app_logger.info("Naplánováno pravidelné čištění dočasných souborů.")

if __name__ == '__main__':
    # Inicializace výchozích složek
    init_default_folders()

    # Spustíme pravidelné čištění dočasných souborů
    schedule_cleanup()

    # Vyčistíme dočasné soubory při startu aplikace
    cleanup_temp_files(app.config['UPLOAD_FOLDER'], max_age_hours=24)

    # Get port from environment variable or use default
    port = int(os.environ.get('PORT', 5001))

    # Note: Use a proper WSGI server (like Gunicorn or Waitress) for production.
    app.run(debug=app.config['FLASK_DEBUG'], host='0.0.0.0', port=port)
