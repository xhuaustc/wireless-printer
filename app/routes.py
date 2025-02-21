from flask import Blueprint, request, jsonify, render_template
from werkzeug.utils import secure_filename
import os
import tempfile
import time
from app.config import Config
from app.utils.file_utils import allowed_file, is_image_file
from app.services.file_service import FileService
from app.services.print_service import PrintService

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    return render_template('index.html')

@bp.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': '没有文件被上传'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': '没有选择文件'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(Config.UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        paper_size = request.form.get('paperSize', 'A4')
        orientation = request.form.get('orientation', 'portrait')
        scale = int(request.form.get('scale', '100'))
        
        try:
            print_filepath = filepath
            
            if is_image_file(filename):
                pdf_filepath = os.path.join(tempfile.gettempdir(), f"{os.path.splitext(filename)[0]}.pdf")
                FileService.convert_image_to_pdf(filepath, pdf_filepath, paper_size, orientation, scale)
                print_filepath = pdf_filepath

            PrintService.print_file(print_filepath, orientation=orientation)
            
            if print_filepath != filepath:
                time.sleep(5)
                try:
                    os.remove(print_filepath)
                except:
                    pass
            
            return jsonify({'success': True, 'message': '文件已发送到打印机'})
            
        except Exception as e:
            return jsonify({'error': f'打印过程中出错: {str(e)}'}), 500
            
    return jsonify({'error': '不支持的文件类型'}), 400 