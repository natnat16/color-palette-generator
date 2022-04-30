# -*- coding: utf-8 -*-
"""
Color palette Generator website 

@author: ANAT-H
"""
from flask import Flask, render_template, redirect, url_for, request, flash, jsonify, make_response
from flask_wtf import FlaskForm
from flask_wtf.file  import FileField, FileRequired, FileAllowed
from wtforms import SubmitField, StringField
from werkzeug.utils import secure_filename
from datetime import datetime
import numpy as np
from PIL import Image
from colorsys import rgb_to_hsv
from sklearn.cluster import KMeans
from threading import Thread
import os
# for local use of .env
# from dotenv import load_dotenv 
# load_dotenv()

app = Flask(__name__, instance_path=os.path.abspath('./static/uploads/'))
app.config['SECRET_KEY'] = os.environ.get('APP_SECRET_KEY')

# globals
filename=None
palette=None
imagefiles = ['jpg','jpeg', 'png', 'bmp', 'gif', 'eps', 'tif', 'mpeg']
clusters = 10

# create KMeans model
model = KMeans(n_clusters=clusters)


class ImageUpload(FlaskForm):
  image = FileField('', validators=[FileRequired(), FileAllowed(imagefiles, 'Images only!')])
  submit = SubmitField('Show')


def format_hsv(r,g,b):
   h, s, v = rgb_to_hsv(r/255, g/255, b/255)
   return f'{h*360:.0f}° {s*100:.0f}% {v*100:.0f}%'
 
## palette generation functions ##  
def get_color_codes(pl): 
  '''
  Generates the color codes in RGB, HEX & HSV.

  Parameters
  ----------
  pl : ARRAY
    An array with the RGB values of the palette.

  Returns
  -------
  palette_codes : List of Dict
    A list of dictionaries of the color codes for the ten colors in the palette.

  '''
  palette_codes = [{'rgb': ('{} {} {}').format(pl[r][0], pl[r][1], pl[r][2]),
                    'hex': ('#{:02X}{:02X}{:02X}').format(pl[r][0], pl[r][1], pl[r][2]),
                    'hsv': format_hsv(pl[r][0], pl[r][1], pl[r][2])
                    } for r in range(clusters)]
  return palette_codes
 
def get_palette(img):
  '''
  Genrates a palette of the most common ten colors in an image.
  
  Parameters
  ----------
  img : STR
    A string containing the image filename.
  
  '''
  global palette
  image = Image.open(f'static/uploads/{img}')
  # verify that all images are in RGB node (with 3 color channels)
  if image.mode != 'RGB':
    image = image.convert('RGB')
  # resizeing image to a max width of 800px (if higher), for a faster calculation. 
  image.thumbnail((800, 800), resample=Image.ANTIALIAS)   
  img_arr = np.array(image)
  n = 3
  model.fit(img_arr.reshape(-1,n)) 
  results = np.rint(model.cluster_centers_, out=np.zeros((clusters,n),'uint8'), casting='unsafe')
  palette = get_color_codes(results)   
  

@app.route('/')
def home():
  '''
  Home view: home page for image upload.

  '''
  form = ImageUpload()
  return render_template("index.html", form=form)

@app.route('/upload', methods=['GET', 'POST'])
def generate_palette():
  '''
  Uploading user Image and starting KMeans Calculation thread

  '''
  global filename, palette
  form = ImageUpload()
  if form.validate_on_submit():    
    image_file = form.image.data
    filename = secure_filename(image_file.filename)  
    image_path = os.path.join(app.instance_path,filename)
    image_file.save(image_path)
    palette=None
    thr = Thread(target=get_palette, args=[filename])
    thr.start()
    return render_template("palette.html", image=filename, palette=palette)
  flash('Choose an image to explore')
  return redirect(url_for('home'))

@app.route('/palette')
def show_palette():
    return render_template("palette.html", image=filename, palette=palette)

@app.route('/check_calc')
def check():
    '''
    Interacting with fetch-API, checking if palette calculation is done, 
    if so redirects to webpage.
    '''
    if palette:
      return redirect(url_for('show_palette'))
    res = make_response(jsonify({'status': 'calculating'}), 200)
    return res


if __name__=="__main__":
  app.run(debug=True)