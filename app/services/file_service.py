from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, A5

class FileService:
    @staticmethod
    def convert_image_to_pdf(image_path, output_path, paper_size='A4', orientation='portrait', scale=100):
        img = Image.open(image_path)
        
        page_size = A4 if paper_size == 'A4' else A5
        if orientation == 'landscape':
            page_size = page_size[::-1]
        
        c = canvas.Canvas(output_path, pagesize=page_size)
        
        img_width, img_height = img.size
        ratio = min(
            page_size[0] * 0.9 / img_width,
            page_size[1] * 0.9 / img_height
        )
        
        scale_factor = scale / 100.0
        ratio = ratio * scale_factor
        
        new_width = img_width * ratio
        new_height = img_height * ratio
        
        x = (page_size[0] - new_width) / 2
        y = (page_size[1] - new_height) / 2
        
        c.drawImage(image_path, x, y, width=new_width, height=new_height)
        c.save() 