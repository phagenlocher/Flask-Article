#!/usr/bin/python3

from flask import Flask
from flask import render_template
from flask_article import *

app = Flask(__name__)

@app.route('/')
def index():
	articles = get_article_list()
	return render_template("index.html", Articles=articles)

@app.route('/contact')
def contact():
    return 'Not done yet, dont sue'

@app.route('/<article>')
def article(article):
	scripts = get_scripts()
	names = []
	for script in scripts:
		names.append(script['Filename'])
	if not article in names:
		return page_not_found(None)
		
	script = scripts[ names.index(article) ]
	del script['Filename']
	script['TableOfContents'], script['Content']  = generate_toc(script['Content'])
	command = 'render_template("article.html"'
	for tag in script.keys():
		command += ', ' + tag + ' = script["' + tag + '"]'
	command += ')'
	return eval(command)

@app.errorhandler(404)
def page_not_found(error):
    return render_template("404.html"), 404

if __name__ == '__main__':
    app.run(debug=True)
    