from flask import Blueprint
main = Blueprint('main', __name__)

@main.route("/")
@main.route("/home")
def home():
	return "home page"

@main.route("/about")
def about():
	return "About Page"