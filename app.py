from flask import Flask, render_template, request, redirect, url_for, flash, send_file
import os
import uuid
from werkzeug.utils import secure_filename
from pixel_generator import PixelArtGenerator



app = Flask(__name__)
app.secret_key = 'afshah_pixel_birthday_2024'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

UPLOAD_FOLDER = 'static/uploads'
OUTPUT_FOLDER = 'static/outputs'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}

# Create directories if they don't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash('No file selected!')
        return redirect(request.url)
    
    file = request.files['file']
    name = request.form.get('name', 'Afshah').strip()
    pixel_size = int(request.form.get('pixel_size', 8))
    
    if file.filename == '':
        flash('No file selected!')
        return redirect(url_for('index'))
    
    if file and allowed_file(file.filename):
        # Generate unique filename
        unique_id = str(uuid.uuid4())[:8]
        filename = secure_filename(file.filename)
        file_extension = filename.rsplit('.', 1)[1].lower()
        
        input_path = os.path.join(UPLOAD_FOLDER, f"{unique_id}_input.{file_extension}")
        output_path = os.path.join(OUTPUT_FOLDER, f"{unique_id}_pixel_art.png")
        
        # Save uploaded file
        file.save(input_path)
        
        # Generate pixel art
        generator = PixelArtGenerator()
        success = generator.generate_pixel_art(input_path, output_path, pixel_size, name)
        
        if success:
            # Clean up input file
            os.remove(input_path)
            
            return render_template('result.html', 
                                 output_file=f"outputs/{unique_id}_pixel_art.png",
                                 name=name)
        else:
            flash('Error processing image. Please try again.')
            return redirect(url_for('index'))
    
    flash('Invalid file type. Please upload an image file.')
    return redirect(url_for('index'))

@app.route('/download/<filename>')
def download_file(filename):
    return send_file(os.path.join(OUTPUT_FOLDER, filename), as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)