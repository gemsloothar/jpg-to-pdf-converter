
from flask import Flask, request, send_file, render_template
from werkzeug.utils import secure_filename
from PyPDF2 import PdfMerger, PdfReader, PdfWriter
from PIL import Image
import os
import io
import zipfile
docx2pdf_installed = False

try:
    from docx2pdf import convert
    docx2pdf_installed = True
except ImportError:
    pass

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/jpg-to-pdf', methods=['POST'])
def jpg_to_pdf():
    files = request.files.getlist('files')
    image_list = [Image.open(f.stream).convert('RGB') for f in files]
    pdf_io = io.BytesIO()
    image_list[0].save(pdf_io, save_all=True, append_images=image_list[1:], format='PDF')
    pdf_io.seek(0)
    return send_file(pdf_io, download_name='converted.pdf', as_attachment=True)

@app.route('/png-to-pdf', methods=['POST'])
def png_to_pdf():
    files = request.files.getlist('files')
    image_list = [Image.open(f.stream).convert('RGB') for f in files]
    pdf_io = io.BytesIO()
    image_list[0].save(pdf_io, save_all=True, append_images=image_list[1:], format='PDF')
    pdf_io.seek(0)
    return send_file(pdf_io, download_name='png_converted.pdf', as_attachment=True)

@app.route('/merge', methods=['POST'])
def merge_pdf():
    merger = PdfMerger()
    for file in request.files.getlist('files'):
        merger.append(file.stream)
    merged_io = io.BytesIO()
    merger.write(merged_io)
    merger.close()
    merged_io.seek(0)
    return send_file(merged_io, download_name='merged.pdf', as_attachment=True)

@app.route('/split', methods=['POST'])
def split_pdf():
    file = request.files['file']
    reader = PdfReader(file.stream)
    output_files = []
    for i, page in enumerate(reader.pages):
        writer = PdfWriter()
        writer.add_page(page)
        split_io = io.BytesIO()
        writer.write(split_io)
        split_io.seek(0)
        output_files.append((f'page_{i+1}.pdf', split_io.read()))
    zip_io = io.BytesIO()
    with zipfile.ZipFile(zip_io, 'w') as zipf:
        for name, data in output_files:
            zipf.writestr(name, data)
    zip_io.seek(0)
    return send_file(zip_io, download_name='split_pages.zip', as_attachment=True)

@app.route('/compress', methods=['POST'])
def compress_pdf():
    file = request.files['file']
    reader = PdfReader(file.stream)
    writer = PdfWriter()
    for page in reader.pages:
        writer.add_page(page)
    compressed_io = io.BytesIO()
    writer.write(compressed_io)
    compressed_io.seek(0)
    return send_file(compressed_io, download_name='compressed.pdf', as_attachment=True)

@app.route('/crop', methods=['POST'])
def crop_pdf():
    file = request.files['file']
    reader = PdfReader(file.stream)
    writer = PdfWriter()
    for page in reader.pages:
        page.mediabox.upper_right = (300, 400)
        writer.add_page(page)
    output_io = io.BytesIO()
    writer.write(output_io)
    output_io.seek(0)
    return send_file(output_io, download_name='cropped.pdf', as_attachment=True)

@app.route('/pdf-to-png', methods=['POST'])
def pdf_to_png():
    from pdf2image import convert_from_bytes
    file = request.files['file']
    images = convert_from_bytes(file.read())
    zip_io = io.BytesIO()
    with zipfile.ZipFile(zip_io, 'w') as zipf:
        for i, image in enumerate(images):
            img_io = io.BytesIO()
            image.save(img_io, format='PNG')
            zipf.writestr(f'page_{i+1}.png', img_io.getvalue())
    zip_io.seek(0)
    return send_file(zip_io, download_name='pdf_to_png.zip', as_attachment=True)

@app.route('/pdf-to-jpg', methods=['POST'])
def pdf_to_jpg():
    from pdf2image import convert_from_bytes
    file = request.files['file']
    images = convert_from_bytes(file.read())
    zip_io = io.BytesIO()
    with zipfile.ZipFile(zip_io, 'w') as zipf:
        for i, image in enumerate(images):
            img_io = io.BytesIO()
            image.save(img_io, format='JPEG')
            zipf.writestr(f'page_{i+1}.jpg', img_io.getvalue())
    zip_io.seek(0)
    return send_file(zip_io, download_name='pdf_to_jpg.zip', as_attachment=True)

@app.route('/doc-to-pdf', methods=['POST'])
def doc_to_pdf():
    if not docx2pdf_installed:
        return "docx2pdf module not installed", 500
    file = request.files['file']
    filepath = os.path.join(UPLOAD_FOLDER, secure_filename(file.filename))
    file.save(filepath)
    output_path = filepath.replace('.docx', '_converted.pdf')
    convert(filepath, output_path)
    return send_file(output_path, download_name='converted.pdf', as_attachment=True)

@app.route('/pdf-to-doc', methods=['POST'])
def pdf_to_doc():
    return "PDF to DOC conversion is not supported in open-source tools reliably.", 501

if __name__ == '__main__':
    app.run(debug=True)
