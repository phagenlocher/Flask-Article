#!/usr/bin/python3

from flask import Flask
from flask import render_template
from flask_article import ScriptLoader

app = Flask(__name__)
sl = ScriptLoader()

@app.route('/')
def index():
	articles = sl.get_article_list()
	return render_template("index.html", Articles=articles)

@app.route('/contact')
def contact():
    return "Not done yet, don't sue"

@app.route('/<article>')
def article(article):
	script = sl.get_single_script(article)
	if script == None:
		return page_not_found()

	func_call = sl.generate_render_command(script, 'article.html')
	return eval(func_call)

@app.errorhandler(404)
def page_not_found(error=None):
    return render_template("404.html"), 404

if __name__ == '__main__':
    app.run(debug=True)
