#!/usr/bin/python3

from flask import Flask
from flask import render_template
from flask_article import ScriptLoader

app = Flask(__name__)
sl = ScriptLoader()


@app.route('/')
def index():
	articles = sl.get_article_list()
	article_html = '';
	for info in articles:
		article_html += '<a href="/' + info['Filename'] + '">' \
		+ '{} - {}'.format(info['Date'], info['Title']) + '</a>\n'
	return render_template('index.html', Articles=article_html)


@app.route('/groupby')
def groupby():
	article_groups = sl.get_article_list(groupby='Type')

	article_html = '';
	for group_name in article_groups.keys():
		article_html += '<h2>{}</h2>'.format(group_name)
		for info in article_groups[group_name]:
			article_html += '<a href="/' + info['Filename'] + '">' \
			+ '{} - {}'.format(info['Date'], info['Title']) + '</a>\n'
		
	return render_template('index.html', Articles=article_html)

@app.route('/contact')
def contact():
    return "Not done yet, don't sue"

@app.route('/<article>')
def article(article):
	script = sl.get_single_script(article)
	if script == None:
		return page_not_found()

	return sl.render_article(script, 'article.html')

@app.errorhandler(404)
def page_not_found(error=None):
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run(debug=True)
