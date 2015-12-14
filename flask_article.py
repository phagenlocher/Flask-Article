#!/usr/bin/python3

import os
from datetime import date
from flask import render_template

TEMPLATE_NEWLINE = 'FLASK_ARTICLE_NEWLINE'

class ScriptLoader():
	'''Loader for the scripts
	'''
	def __init__(self, script_folder='/scripts'):
		'''Constructor

		Keyword arguments:
		script_folder -- the directory for your scripts (default '/scripts')
		'''
		self.script_folder = script_folder

	def render_article(self, script, template_file):
		'''Generates a 'render_template' function call which sets all the tags
		of your script. Evaluates that call and returns it.

		e.g.
		Your tags are "Author", "Title" and "Date".
		The resulting command will be:
		render_template(<filename>, Author = script["Author"], Title = script["Title"], Date = script["Date"])

		Keyword arguments:
		script -- parsed script
		template_file -- filename of your template file
		'''
		func_call = 'render_template("' + template_file + '"'
		for tag in script.keys():
			func_call += ', ' + tag + ' = ' + var_name + '["' + tag + '"]'
		func_call += ')'
		return eval(func_call)

	def get_single_script(self, script):
		'''Opens single script and parses it so it can be used with a html template

		Keyword arguments:
		script -- script name
		'''
		script = self.__get_script_info__(script)
		if script == None:
			return None
		
		script['TableOfContents'], script['Content']  = self.__generate_toc__(script['Content'])
		return script

	def __get_script_info__(self, script):
		'''Open a script and parse its content 
		If the script is faulty, None is returned

		Keyword arguments:
		script -- script name
		'''
		script_info = {}
		script_info['Filename'] = script

		# The file couldn't be found
		if not script in os.listdir(os.getcwd() + '/' + self.script_folder):
			return None


		data = open(os.getcwd() + '/' + self.script_folder + '/' + script).read()
		data = data.split('\n')
		try:
			i = data.index('---End-Tags---')
		except:
			return None
			
		while '' in data:
			data.remove('')
			
		tags = data[:i-1]
		script_info['Content'] = TEMPLATE_NEWLINE.join(data[i:]).replace("\\\\", "</br>")
		
		for tag in tags:
			tag_name = tag[ tag.find('{')+1 : tag.find('}') ]
			tag_data = tag[ tag.rfind('{')+1 : tag.rfind('}') ]
			script_info[tag_name] = tag_data
			
		# Check script validity
		required_tags = ['Author','Title','Date']
		for rt in required_tags:
			if not rt in script_info.keys():
				return None
			# Make the title titlecased
			if rt == 'Title':
				if not script_info['Title'].startswith('_'):
					script_info['Title'] = script_info['Title'].title()
			# Create a date-object (later used for sorting)
			if rt == 'Date':
				d = script_info['Date'].split('/')
				d = date(day=int(d[0]), month=int(d[1]), year=int(d[2]))
				script_info['Date'] = d.strftime("%d. %h %Y")
				script_info['Date_object'] = d
			
		return script_info

	def __get_scripts__(self, sort=True, key='Date_object'):
		'''Get all the scripts from the script directory and optionally sort them

		Keyword arguments:
		sort -- if the scripts should be sorted by date (default True)
		key -- the key to sort after (default 'Date_object')
		'''
		script_infos = []
		files = os.listdir( os.getcwd() + self.script_folder )
		for script in files:
			info = self.__get_script_info__(script)
			if info is not None:
				script_infos.append(info)
		if sort:
			script_infos.sort(reverse=True, key=lambda x : x[key])
		return script_infos

	def __generate_toc__(self, content, numbered=True):
		'''Generates a table of contents and modifies an articles content

		Keyword arguments:
		content -- the content to parse
		numbered -- if the sections should be numbered (default True)
		'''
		script = content.split(TEMPLATE_NEWLINE)
		
		sections = []
		section_num = 0
		subsection_num = 1
		for i, line in enumerate(script):
			if line.startswith("**"):
				top_sec = sections.pop()
				num = float(str(section_num) + "." + str(subsection_num))
				if line.startswith("**_"):
					sec_title = line[3:].strip()
				else:
					sec_title = line[2:].strip().title()
				top_sec.append((sec_title, i, num))
				subsection_num += 1
				sections.append(top_sec)
			elif line.startswith("*"):
				subsection_num = 1
				section_num += 1
				if line.startswith("*_"):
					sec_title = line[2:].strip()
				else:
					sec_title = line[1:].strip().title()
				sections.append([(sec_title, i, section_num)])

		# Create html content
		content = ""		
		for sec_list in sections:
			for sec in sec_list:
				if numbered:
					sec_name = str(sec[2]) + " - " + sec[0]
				else:
					sec_name = sec[0]
				if type(sec[2]) == int:
					content += "<h2 id='" + str(sec[2]) + "'>" + sec_name + "</h2>\n<p>\n"
				if type(sec[2]) == float:
					content += "<h3 id='" + str(sec[2]) + "'>" + sec_name + "</h3>\n<p>\n"
				index = sec[1] + 1
				if index >= len(script):
					break
				while not script[index].startswith("*"):
					content += script[index] + " "
					index += 1
					if index >= len(script):
						break
				content = content[:-1].replace("\\\\", "</br>")
				content += "\n</p>\n"

		# Create table of contents
		toc = "<ul class='toc'>\n"
		single = False
		for sec_list in sections:
			single = False
			if len(sec_list) == 1:
					single = True
			for sec in sec_list:
				if numbered:
					sec_name = str(sec[2]) + " - " + sec[0]
				else:
					sec_name = sec[0]
				toc += "<li><a href='#" + str(sec[2]) + "'>" + sec_name + "</a></li>\n"
				if sec_list.index(sec) == 0:
					if not single:
						toc += "<ul>\n"
				if sec_list.index(sec) == len(sec_list)-1:
					if not single:
						toc += "</ul>\n"
		toc += "</ul>\n"
		return toc, content

	def get_article_list(self, format_string='{} - {}', sort=True, key='Date_object'):
		'''Get a list of html-links to all the articles

		Keyword arguments:
		format_string -- the string to use as a template for creating links to the articles (default '{} - {}')
		sort -- if the scripts should be sorted by date (default True)
		key -- the key to sort after (default 'Date_object')
		'''
		scripts = self.__get_scripts__(sort, key)
		article_html = '';
		for info in scripts:
			article_html += '<a href="/' + info['Filename'] + '">' \
			+ format_string.format(info['Date'], info['Title']) + '</a>\n'
		return article_html
		