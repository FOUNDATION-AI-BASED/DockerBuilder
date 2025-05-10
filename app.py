import os
import json
import magic
import yaml
import zipfile
import tarfile
import shutil
import chardet
from flask import Flask, request, jsonify, send_file, render_template, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
from project_analyzer import ProjectAnalyzer
from docker_generator import DockerGenerator

app = Flask(__name__, 
    static_folder='static',
    template_folder='templates'
)
CORS(app)

UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'output'
EXTRACT_FOLDER = 'extracted'
ALLOWED_EXTENSIONS = {'zip', 'tar', 'gz'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER
app.config['EXTRACT_FOLDER'] = EXTRACT_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure required directories exist
for directory in [UPLOAD_FOLDER, OUTPUT_FOLDER, EXTRACT_FOLDER, 'static', 'templates']:
    os.makedirs(directory, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def detect_encoding(file_path):
    """Detect the encoding of a file."""
    with open(file_path, 'rb') as f:
        raw_data = f.read()
        result = chardet.detect(raw_data)
        return result['encoding'] or 'utf-8'

def is_binary_file(file_path):
    """Check if a file is binary."""
    mime = magic.Magic(mime=True)
    file_type = mime.from_file(file_path)
    return not file_type.startswith('text/')

def extract_archive(filepath, extract_to):
    """Extract the uploaded archive to the specified directory."""
    if filepath.endswith('.zip'):
        with zipfile.ZipFile(filepath, 'r') as zip_ref:
            zip_ref.extractall(extract_to)
    elif filepath.endswith(('.tar', '.tar.gz', '.tgz')):
        with tarfile.open(filepath, 'r:*') as tar_ref:
            tar_ref.extractall(extract_to)
    else:
        raise ValueError(f"Unsupported archive format: {filepath}")

def create_dockerized_project(project_dir, docker_configs, output_path, format):
    """Create a new archive containing the project and Docker configurations."""
    if format == 'zip':
        with zipfile.ZipFile(output_path, 'w') as zipf:
            # Add project files
            for root, _, files in os.walk(project_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, project_dir)
                    zipf.write(file_path, arcname)
            
            # Add Docker configuration files
            for config_file in docker_configs:
                zipf.write(config_file, os.path.basename(config_file))
    else:
        with tarfile.open(output_path, 'w:gz') as tarf:
            # Add project files
            for root, _, files in os.walk(project_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, project_dir)
                    tarf.add(file_path, arcname)
            
            # Add Docker configuration files
            for config_file in docker_configs:
                tarf.add(config_file, os.path.basename(config_file))

def remove_macos_folders(directory):
    """Remove _MACOS folders from the extracted project."""
    for root, dirs, _ in os.walk(directory):
        if '_MACOS' in dirs:
            macos_path = os.path.join(root, '_MACOS')
            shutil.rmtree(macos_path)
            dirs.remove('_MACOS')

def find_project_root(directory):
    """Find the actual project root directory by looking for key files."""
    key_files = ['package.json', 'requirements.txt', 'pom.xml', 'Gemfile', 'composer.json', 'go.mod', 'Cargo.toml']
    
    # First check the current directory
    if any(os.path.exists(os.path.join(directory, f)) for f in key_files):
        return directory
    
    # Then check immediate subdirectories
    for item in os.listdir(directory):
        item_path = os.path.join(directory, item)
        if os.path.isdir(item_path):
            if any(os.path.exists(os.path.join(item_path, f)) for f in key_files):
                return item_path
    
    return directory

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/analyze', methods=['POST'])
def analyze_project():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type'}), 400
    
    try:
        # Get configuration options
        host = request.form.get('host', '0.0.0.0')
        port = request.form.get('port', '5000')
        output_format = request.form.get('format', 'zip')
        
        # Save the uploaded file
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Create a unique extraction directory
        project_name = os.path.splitext(filename)[0]
        extract_path = os.path.join(app.config['EXTRACT_FOLDER'], project_name)
        os.makedirs(extract_path, exist_ok=True)
        
        # Extract the archive
        extract_archive(filepath, extract_path)
        
        # Remove _MACOS folders
        remove_macos_folders(extract_path)
        
        # Find the actual project root
        project_root = find_project_root(extract_path)
        
        # Analyze the project with encoding detection
        analyzer = ProjectAnalyzer(project_root)
        analysis_result = analyzer.analyze()
        
        # Generate Docker configurations with custom host and port
        generator = DockerGenerator(analysis_result)
        docker_configs = generator.generate(host=host, port=port)
        
        # Create output package with project and Docker files
        output_filename = f"dockerized_project.{output_format}"
        output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)
        
        create_dockerized_project(project_root, docker_configs, output_path, output_format)
        
        return send_file(output_path, as_attachment=True)
    
    except zipfile.BadZipFile:
        return jsonify({'error': 'Invalid ZIP file'}), 400
    except tarfile.ReadError:
        return jsonify({'error': 'Invalid TAR file'}), 400
    except Exception as e:
        app.logger.error(f"Error processing file: {str(e)}")
        return jsonify({'error': str(e)}), 500
    finally:
        # Cleanup
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
            if os.path.exists(extract_path):
                shutil.rmtree(extract_path)
        except Exception as e:
            app.logger.error(f"Error cleaning up: {str(e)}")

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False) 
