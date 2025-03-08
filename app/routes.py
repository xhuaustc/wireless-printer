from flask import Blueprint, request, jsonify, render_template, send_from_directory
from werkzeug.utils import secure_filename
import os
import tempfile
import time
from app.config import Config
from app.utils.file_utils import allowed_file, is_image_file
from app.services.file_service import FileService
from app.services.print_service import PrintService
from app.services.sketch_service import SketchService

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
                time.sleep(10)
                try:
                    os.remove(print_filepath)
                except:
                    pass
            
            return jsonify({'success': True, 'message': '文件已发送到打印机'})
            
        except Exception as e:
            return jsonify({'error': f'打印过程中出错: {str(e)}'}), 500
            
    return jsonify({'error': '不支持的文件类型'}), 400 

@bp.route('/convert-sketch', methods=['POST'])
def convert_sketch():
    if 'file' not in request.files:
        return jsonify({'error': '没有文件被上传'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': '没有选择文件'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(Config.UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        # 获取转换参数
        style = request.form.get('style', 'normal')  # normal 或 artistic
        # 确保输出文件使用.png扩展名
        output_filename = f"sketch_{os.path.splitext(filename)[0]}.png"
        output_path = os.path.join(Config.UPLOAD_FOLDER, output_filename)
        
        try:
            if style == 'artistic':
                success = SketchService.convert_to_sketch_artistic(filepath, output_path)
            else:
                threshold1 = int(request.form.get('threshold1', '50'))
                threshold2 = int(request.form.get('threshold2', '150'))
                blur_size = int(request.form.get('blurSize', '5'))
                success = SketchService.convert_to_sketch(
                    filepath, 
                    output_path,
                    threshold1,
                    threshold2,
                    blur_size
                )
            
            if success:
                return jsonify({
                    'success': True,
                    'message': '转换成功',
                    'filename': output_filename
                })
            else:
                return jsonify({'error': '转换失败'}), 500
                
        except Exception as e:
            return jsonify({'error': f'转换过程中出错: {str(e)}'}), 500
            
    return jsonify({'error': '不支持的文件类型'}), 400 

@bp.route('/uploads/<filename>')
def uploaded_file(filename):
    """提供对上传文件的访问"""
    return send_from_directory(Config.UPLOAD_FOLDER, filename) 

@bp.route('/print-sketch', methods=['POST'])
def print_sketch():
    """处理简笔画打印请求"""
    try:
        data = request.json
        filename = data.get('filename')
        if not filename:
            return jsonify({'error': '未指定文件名'}), 400
            
        filepath = os.path.join(Config.UPLOAD_FOLDER, filename)
        if not os.path.exists(filepath):
            return jsonify({'error': '文件不存在'}), 404
            
        # 转换为PDF并打印
        pdf_filepath = os.path.join(tempfile.gettempdir(), f"{os.path.splitext(filename)[0]}.pdf")
        FileService.convert_image_to_pdf(filepath, pdf_filepath)
        
        PrintService.print_file(pdf_filepath)
        
        # 清理临时PDF文件
        time.sleep(5)
        try:
            os.remove(pdf_filepath)
        except:
            pass
            
        return jsonify({'success': True, 'message': '文件已发送到打印机'})
        
    except Exception as e:
        return jsonify({'error': f'打印过程中出错: {str(e)}'}), 500 