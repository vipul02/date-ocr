from flask import Flask, render_template, request
import os
from model import ExtractDate, ProcessImage
import numpy as np
import re
from PIL import Image
from io import BytesIO
from base64 import b64decode

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def home():
	return 'Goto: https://date-ocr.herokuapp.com/extract_date'

@app.route('/extract_date', methods=['POST', 'GET'])
def date():
	if request.method == 'POST':
		data = request.get_json(force=True)
		base64_img = data["base_64_image_content"]
		if type(base64_img == str):
			img = re.search(r'base64,(.*)', base64_img).group(1)
			img = Image.open(BytesIO(b64decode(img)))
		elif type(base64_img == bytes):
			img = Image.open(BytesIO(b64decode(base64_img)))
		
		txt = ProcessImage().img_to_string(img)
		date = ExtractDate().extract_date(txt)
		return {"date": date}
	else:
		return 'Please POST base64 image data'
