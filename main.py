from flask import Flask, render_template, request, jsonify
import win32print
import win32api
import os
from werkzeug.utils import secure_filename
import win32con
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, A5
import tempfile

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# 确保上传目录存在
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'txt', 'jpg', 'jpeg', 'png', 'gif'}
IMAGE_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def is_image_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in IMAGE_EXTENSIONS

def convert_image_to_pdf(image_path, output_path, paper_size='A4', orientation='portrait'):
    # 打开图片
    img = Image.open(image_path)
    
    # 确定页面尺寸
    if paper_size == 'A4':
        page_size = A4
    else:  # A5
        page_size = A5
        
    # 处理方向
    if orientation == 'landscape':
        page_size = page_size[::-1]  # 交换宽高
    
    # 创建PDF
    c = canvas.Canvas(output_path, pagesize=page_size)
    
    # 计算图片尺寸以适应页面
    img_width, img_height = img.size
    ratio = min(
        page_size[0] * 0.9 / img_width,
        page_size[1] * 0.9 / img_height
    )
    
    new_width = img_width * ratio
    new_height = img_height * ratio
    
    # 计算居中位置
    x = (page_size[0] - new_width) / 2
    y = (page_size[1] - new_height) / 2
    
    # 将图片绘制到PDF
    c.drawImage(image_path, x, y, width=new_width, height=new_height)
    c.save()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': '没有文件被上传'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': '没有选择文件'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # 获取打印参数
        paper_size = request.form.get('paperSize', 'A4')
        orientation = request.form.get('orientation', 'portrait')
        scale = request.form.get('scale', '100')
        
        try:
            printer_name = win32print.GetDefaultPrinter()
            print_filepath = filepath
            
            # 如果是图片文件，先转换为PDF
            if is_image_file(filename):
                pdf_filepath = os.path.join(tempfile.gettempdir(), f"{os.path.splitext(filename)[0]}.pdf")
                convert_image_to_pdf(filepath, pdf_filepath, paper_size, orientation)
                print_filepath = pdf_filepath
            
            # 打印文件
            win32api.ShellExecute(
                0,
                "print",
                print_filepath,
                f'/d:"{printer_name}"',
                ".",
                0
            )
            
            # 如果是临时PDF文件，等待一会儿后删除
            if print_filepath != filepath:
                import time
                time.sleep(2)  # 等待2秒确保打印开始
                try:
                    os.remove(print_filepath)
                except:
                    pass
            
            return jsonify({'success': True, 'message': '文件已发送到打印机'})
            
        except Exception as e:
            return jsonify({'error': f'打印过程中出错: {str(e)}'}), 500
            
    return jsonify({'error': '不支持的文件类型'}), 400

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')