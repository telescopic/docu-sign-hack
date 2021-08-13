from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.units import inch, cm
from reportlab.lib.utils import ImageReader
import PIL
from pdf2image import convert_from_path

class PDFUtil:
    
    def __init__(self):
        pass

    def get_formatted_contents(self, area, author):
        contents = []

        # defaults
        contents.append(('text', 'Map Distribution Approval', (10, 32))) # title
        contents.append(('text', 'sign: ', (1, 2))) # signing tab
        contents.append(('text', 'Visual Description of finalized map', (4.5, 29.0)))
        contents.append(('img', "/home/vignesh/Desktop/FlaskApp/flask_app_basic/static/saved_pdfs/final_map.png", (1.5, 5)))

        # formatted
        contents.append(('text', f'Area: {area}', (1, 30.5)))
        contents.append(('text', f'Author: {author}', (1, 30.0)))

        return contents

    def create_pdf(self, filename, contents, width=25, height=35):
        '''
        Creates a pdf of given size, adds contents
        and saves it in the default directory
        args:
            * width: in cm
            * height: in cm
            * contents: a tuple of values (content_type, content, position)
              where 
                content_type = img/text
                content = text or image object
                position = (dist from left edge, dist from bottom edge)
        '''
        canvas = Canvas(filename, pagesize=(width*cm, height*cm)) # (width, height)

        for content_type, content, position in contents:
            if content_type == 'img':
                img = ImageReader(PIL.Image.open(content))
                canvas.drawImage(img, position[0]*cm, position[1]*cm, mask='auto')
            else:
                canvas.drawString(position[0]*cm, position[1]*cm, content)
        
        canvas.save()
    
    def convert_pdf_to_image(self, pdf_path, image_path):
        pages = convert_from_path(pdf_path, dpi=200)
        pages[0].save(image_path, 'JPEG')

# pdfutil = PDFUtil()
# contents = pdfutil.get_formatted_contents(area="area", author="author", lat="lat", lng="long")
# pdfutil.create_pdf(contents=contents)


    
