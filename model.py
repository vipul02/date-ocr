import re
from PIL import Image
import cv2
import numpy as np
import pytesseract as tr
from dateutil.parser import parse

# for windows write this path
# tr.pytesseract.tesseract_cmd = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'


class ExtractDate:
    def __init__(self):
        self.months = 'JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC|JANUARY|FEBRUARY|MARCH|APRIL|JUNE|JULY|AUGUST|SEPTEMBER|OCTOBER|NOVEMBER|DECEMBER|jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec|january|february|march|april|june|july|august|september|october|november|december|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|January|February|March|April|June|July|August|September|October|November|December'
        self.regex = [r'(\d{1,4}([.\-/])\d{1,2}([.\-/])\d{1,4})',
                      r'(\d{1,4}([\',.\-/\s]*)(' + self.months + r')([\',.\-/\s]*)\d{1,4})',
                      r'((' + self.months + r')([\',.\-/\s]*)\d{1,2}([\',.\-/\s]+)\d{1,4})']
        self.extracted_dates = []
    
    def extract_date(self, text):
        for string in text:
            try:
                self.extracted_dates.append([parse(x.group()).strftime('%Y-%m-%d') for x in (re.search(reg, string) for reg in self.regex) if x])
            except:
                continue
        self.extracted_dates = list(filter(None, self.extracted_dates))
        if not self.extracted_dates:
            return 'null'
        else:
            return self.extracted_dates[0][0]

        
class ProcessImage:
    def __init__(self):
        self.config = '-l eng --oem 1 --psm 3+12' # psm 1,11,12
    
    def resize(self, img):
        return cv2.resize(img, None, fx = 1.5, fy = 1.5, interpolation=cv2.INTER_CUBIC)
    
    def fix_lightening(self, img):
        rgb_planes = cv2.split(img)
        result_norm_planes = []
        for plane in rgb_planes:
            dilated_img = cv2.dilate(plane, np.ones((7,7), np.uint8))
            bg_img = cv2.medianBlur(dilated_img, 21)
            diff_img = 255 - cv2.absdiff(plane, bg_img)
            norm_img = cv2.normalize(diff_img,None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8UC1)
            result_norm_planes.append(norm_img)
        return cv2.merge(result_norm_planes)

    def thresholding(self, img):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        return cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

    def reduce_noise(self, img):
        kernel = np.ones((1, 1), np.uint8)
        img = cv2.erode(img, kernel, iterations=1)
        img = cv2.dilate(img, kernel, iterations=1)
        img = cv2.morphologyEx(img, cv2.MORPH_OPEN, kernel)
        img = cv2.morphologyEx(img, cv2.MORPH_CLOSE, kernel)
        return img

    def img_to_string(self, img):
        img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        resized_img = self.resize(img)
        norm_img = self.fix_lightening(resized_img)
        thresh_img = self.thresholding(norm_img)
        processed_img = self.reduce_noise(thresh_img)
        text = tr.image_to_string(Image.fromarray(processed_img), config=self.config)
        return list(map(lambda x: x.strip(), text.split('\n')))
