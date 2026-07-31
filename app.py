import os
from flask import Flask, request, jsonify, render_template, send_from_directory
from werkzeug.utils import secure_filename
from detection.ensemble import classify_image

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

UPLOAD_FOLDER = os.path.join(app.static_folder, 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'webp', 'bmp', 'tiff'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No image selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': f'Invalid file type. Allowed: {", ".join(ALLOWED_EXTENSIONS)}'}), 400
    
    filename = secure_filename(file.filename)
    # Add timestamp to avoid caching issues
    import time
    base, ext = os.path.splitext(filename)
    filename = f"{base}_{int(time.time())}{ext}"
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)
    
    try:
        result = classify_image(filepath, UPLOAD_FOLDER)
        
        # Convert paths to URLs for frontend
        if result.get('ela_image_path'):
            ela_basename = os.path.basename(result['ela_image_path'])
            result['ela_image_url'] = f'/static/uploads/{ela_basename}'
        
        result['original_image_url'] = f'/static/uploads/{filename}'
        
        # Remove file system paths from response (security)
        if 'ela_image_path' in result:
            del result['ela_image_path']
        for module in result.get('details', {}).values():
            if 'ela_image_path' in module:
                del module['ela_image_path']
        
        return jsonify(result)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Analysis failed: {str(e)}'}), 500

@app.route('/static/uploads/<path:filename>')
def serve_upload(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

if __name__ == '__main__':
    print('\n' + '='*50)
    print('  ForensicAI - Image Forgery Detection')
    print('  Open http://localhost:5000 in your browser')
    print('='*50 + '\n')
    app.run(debug=True, host='0.0.0.0', port=5000)
