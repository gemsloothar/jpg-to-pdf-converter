from flask import Flask, request, send_file
from PIL import Image
import os
import io

app = Flask(__name__)

@app.route('/')
def home():
    with open("index.html", "r") as f:
        return f.read()

@app.route('/convert', methods=['POST'])
def convert():
    images = request.files.getlist("images")
    img_list = []
    for img_file in images:
        img = Image.open(img_file)
        if img.mode != 'RGB':
            img = img.convert('RGB')
        img_list.append(img)

    pdf_bytes = io.BytesIO()
    if img_list:
        img_list[0].save(pdf_bytes, format="PDF", save_all=True, append_images=img_list[1:])
    pdf_bytes.seek(0)

    return send_file(pdf_bytes, download_name="converted.pdf", as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
