#!/usr/bin/python3

import os
from datetime import date

TEMPLATER_NEWLINE = 'FLASKTEMPLATERNEWLINE'

def get_script_info(script, script_folder = '/scripts'):
	'''Open a script and parse its content 

	Keyword arguments:
	script -- script name
	script_folder -- the directory for the script (default '/scripts')
	'''
	script_info = {}
	script_info['Filename'] = script
	data = open(os.getcwd() + '/' + script_folder + '/' + script).read()
	data = data.split('\n')
	try:
		i = data.index('---End-Tags---')
	except:
		return None
		
	while '' in data:
		data.remove('')
		
	tags = data[:i-1]
	script_info['Content'] = TEMPLATER_NEWLINE.join(data[i:]).replace("\\\\", "</br>")
	
	for tag in tags:
		tag_name = tag[ tag.find('{')+1 : tag.find('}') ]
		tag_data = tag[ tag.rfind('{')+1 : tag.rfind('}') ]
		script_info[tag_name] = tag_data
		
	# Check script validity
	required_tags = ['Author','Title','Date']
	for rt in required_tags:
		if not rt in script_info.keys():
			return None
		if rt == 'Title':
			if not script_info['Title'].startswith('_'):
				script_info['Title'] = script_info['Title'].title()
		if rt == 'Date':
			d = script_info['Date'].split('/')
			d = date(day=int(d[0]), month=int(d[1]), year=int(d[2]))
			script_info['Date'] = d.strftime("%d. %h %Y")
			script_info['Date_object'] = d
		
	return script_info

def get_scripts(script_folder = '/scripts', sort=True):
	'''Get all the scripts from the script directory and optionally sort them

	Keyword arguments:
	script_folder -- the directory for the scripts (default '/scripts')
	sort -- if the scripts should be sorted by date (default True)
	'''
	script_infos = []
	files = os.listdir( os.getcwd() + script_folder )
	for script in files:
		info = get_script_info(script, script_folder)
		if info is not None:
			script_infos.append(info)
	if sort:
		script_infos.sort(reverse=True, key=lambda x : x['Date_object'])
	return script_infos

def generate_toc(content, numbered=True):
	'''Generates a table of contents and modifies an articles content

	Keyword arguments:
	content -- the content to parse
	numbered -- if the sections should be numbered (default True)
	'''
	script = content.split(TEMPLATER_NEWLINE)
	
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

def get_article_list(format_string='{} - {}'):
	'''Get a list of html-links to all the articles

	Keyword arguments:
	format_string -- the string to use as a template for creating links to the articles
	'''
	scripts = get_scripts()
	article_html = '';
	for info in scripts:
		article_html += '<a href="/' + info['Filename'] + '">' \
		+ format_string.format(info['Date'], info['Title']) + '</a>\n'
	return article_html
	