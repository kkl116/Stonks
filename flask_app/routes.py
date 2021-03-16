import os 
import secrets 
from PIL import Image
#import models 
#import forms
from flask_app import app, db, bcyrpt
from flask_login import login_user, current_user, logout_user, login_required
from flask import render_template, url_for, flash, redirect, request, abort

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')