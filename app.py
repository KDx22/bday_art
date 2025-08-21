from flask import Flask, render_template, request, redirect, url_for, flash, send_file
import os
import uuid
from werkzeug.utils import secure_filename
import traceback
import tempfile

# Import with error handling for deployment
try:
    from pixel_generator import PixelArtGenerator
except ImportError as e:
    print(f"Import error: {e}")
    # Create a dummy class for deployment debugging
    class PixelArtGenerator:
        def generate_pixel_art(self, input_path, output_path, pixel_size, name):
            print("PixelArtGenerator not available")
            return False

app = Flask(__name__)
app.secret_key = 'afshah_pixel_birthday_2024'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Use absolute paths for deployment
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
OUTPUT_FOLDER = os.path.join(BASE_DIR, 'static', 'outputs')

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}

# Create directories with error handling
def create_directories():
    """Create required directories with proper error handling"""
    global UPLOAD_FOLDER, OUTPUT_FOLDER  # Move global declaration here
    
    try:
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        os.makedirs(OUTPUT_FOLDER, exist_ok=True)
        print(f"Directories created: {UPLOAD_FOLDER}, {OUTPUT_FOLDER}")
        
        # Test write permissions
        test_file = os.path.join(UPLOAD_FOLDER, 'test.txt')
        with open(test_file, 'w') as f:
            f.write('test')
        os.remove(test_file)
        print("Write permissions OK")
        
    except Exception as e:
        print(f"Directory creation failed: {e}")
        # Fallback to temp directory
        UPLOAD_FOLDER = tempfile.mkdtemp(prefix='uploads_')
        OUTPUT_FOLDER = tempfile.mkdtemp(prefix='outputs_')
        print(f"Using temp directories: {UPLOAD_FOLDER}, {OUTPUT_FOLDER}")

create_directories()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        print("Upload request received")
        
        if 'file' not in request.files:
            flash('No file selected!')
            return redirect(url_for('index'))
        
        file = request.files['file']
        name = request.form.get('name', 'Afshah').strip()
        pixel_size = int(request.form.get('pixel_size', 8))
        
        print(f"Form data - name: {name}, pixel_size: {pixel_size}")
        
        if file.filename == '':
            flash('No file selected!')
            return redirect(url_for('index'))
        
        if not file or not allowed_file(file.filename):
            flash('Invalid file type. Please upload an image file.')
            return redirect(url_for('index'))
        
        # Generate unique filename
        unique_id = str(uuid.uuid4())[:8]
        filename = secure_filename(file.filename)
        file_extension = filename.rsplit('.', 1)[1].lower() if '.' in filename else 'png'
        
        input_path = os.path.join(UPLOAD_FOLDER, f"{unique_id}_input.{file_extension}")
        output_path = os.path.join(OUTPUT_FOLDER, f"{unique_id}_pixel_art.png")
        
        print(f"Paths - input: {input_path}, output: {output_path}")
        
        # Save uploaded file with error handling
        try:
            file.save(input_path)
            print(f"File saved: {input_path}")
            
            # Verify file was saved
            if not os.path.exists(input_path):
                raise Exception("File not saved properly")
                
        except Exception as e:
            print(f"File save error: {e}")
            flash('Error saving uploaded file. Please try again.')
            return redirect(url_for('index'))
        
        # Generate pixel art with detailed error handling
        try:
            print("Starting pixel art generation...")
            generator = PixelArtGenerator()
            success = generator.generate_pixel_art(input_path, output_path, pixel_size, name)
            
            if success:
                print("Pixel art generation successful")
                
                # Verify output file exists
                if not os.path.exists(output_path):
                    raise Exception("Output file not created")
                
                # Clean up input file
                try:
                    os.remove(input_path)
                    print("Input file cleaned up")
                except:
                    pass  # Don't fail if cleanup fails
                
                # Return relative path for template
                relative_output = f"outputs/{unique_id}_pixel_art.png"
                return render_template('result.html', 
                                     output_file=relative_output,
                                     name=name)
            else:
                raise Exception("Generator returned False")
                
        except Exception as e:
            print(f"Pixel art generation error: {e}")
            traceback.print_exc()
            
            # Clean up input file on error
            try:
                if os.path.exists(input_path):
                    os.remove(input_path)
            except:
                pass
            
            flash(f'Error processing image: {str(e)}. Please try a different image.')
            return redirect(url_for('index'))
    
    except Exception as e:
        print(f"Unexpected error in upload_file: {e}")
        traceback.print_exc()
        flash('Unexpected error occurred. Please try again.')
        return redirect(url_for('index'))

@app.route('/download/<filename>')
def download_file(filename):
    try:
        file_path = os.path.join(OUTPUT_FOLDER, filename)
        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=True)
        else:
            flash('File not found.')
            return redirect(url_for('index'))
    except Exception as e:
        print(f"Download error: {e}")
        flash('Error downloading file.')
        return redirect(url_for('index'))

@app.route('/health')
def health_check():
    """Health check endpoint for deployment debugging"""
    try:
        from pixel_generator import PixelArtGenerator
        generator_status = "Available"
    except ImportError as e:
        generator_status = f"Import Error: {e}"
    
    return {
        "status": "ok",
        "pixel_generator": generator_status,
        "upload_folder": UPLOAD_FOLDER,
        "output_folder": OUTPUT_FOLDER,
        "upload_folder_exists": os.path.exists(UPLOAD_FOLDER),
        "output_folder_exists": os.path.exists(OUTPUT_FOLDER),
        "base_dir": BASE_DIR
    }

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
