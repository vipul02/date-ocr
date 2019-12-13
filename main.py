from flask import Flask, render_template, request
import os
from model import ExtractDate, ProcessImage
import numpy as np
import re
from PIL import Image
from io import BytesIO
from base64 import b64decode
import requests

app = Flask(__name__)
url = 'http://3.86.229.155:8080/extract_date'
		
@app.route('/', methods=['GET', 'POST'])
def home():
	return 'Goto: /extract_date'

@app.route('/extract_date', methods=['POST', 'GET'])
def date():
	if request.method == 'POST':
		data = request.get_json(force=True)
		base64_img = data["base_64_image_content"]
		return requests.post(url, json={"base_64_image_content" : base64_img}).json()
	else:
		return 'Please POST base64 image data'
