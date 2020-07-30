from flask import Blueprint, render_template


main = Blueprint('main', __name__)

@main.route('/')
@main.route('/main/home')
def home():
    return render_template('home.html')

@main.route('/main/about')
def about():
    return render_template('about.html', title='About')
