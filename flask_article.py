#!/usr/bin/python3

import os
import shutil
import hashlib as hl
from datetime import date
from flask import render_template

TEMPLATE_NEWLINE = '\0'
CACHE_SEPERATOR = '\n\0\n'

class CacheHandler():
	'''Handler for caching files

	It uses 2 caches, the heap (limited) and the discspace.
	The last cached scripts are the ones in heap.
	'''
	def __init__(self, script_loader, cache_limit=1000, script_folder='scripts', cache_folder='.cache', debug=True, hash_alg='sha1'):
		'''Constructor

		Keyword arguments:
		cache_limit -- how many files should be in heap-cache (default 10)
		script_folder -- the directory for your scripts (default 'scripts')
		cache_folder -- the directory for cached files (default '.cache')
		debug -- specefies wether the handler will output debug information (default True)
		'''
		# TODO documentation
		# TODO test performance
		self.sl = script_loader
		self.cache_limit = cache_limit
		self.script_folder = script_folder
		self.cache_folder = cache_folder
		self.debug = debug
		self.heap_cache = {}

		if hash_alg in hl.algorithms_available:
			self.hash_alg = hash_alg
		else:
			self.report('The hash algorithm "' + hash_alg + '" is not available'\
				' on this system! (Using SHA1 instead)')
			self.hash_alg = 'sha1'
		self.hash_size = hl.new(self.hash_alg).digest_size

		self.create_new_cache_dir()

	def report(self, data):
		'''Prints a message, if the CacheHandler is in debug-mode'''
		if self.debug:
			print(data)

	def create_new_cache_dir(self):
		'''Deletes the cache dir and creates a new empty one'''
		self.report('Renewing cache dir')
		if os.path.exists(self.cache_folder) and os.path.isdir(self.cache_folder):
			shutil.rmtree(self.cache_folder)
		os.mkdir(self.cache_folder)

	def new_cache_entry(self, script):
		'''Creates a new cache entry in the cache dir for a file

		The entry saves a the scripts tags, content and hash.
		'''
		name = script['Filename']
		self.report("Creating new cache entry for " + name)

		# Creating hash-digest of the scriptfile
		file_data = open(self.script_folder + '/' + name, 'rb').read()
		h = hl.new(self.hash_alg, file_data).digest()

		# Creating the content that will be stored in disc cache.
		# The produced file contains the hash and tuples of tags and
		# corrosponding values. The tuples are seperated by the CACHE_SEPERATOR
		# and tags and values are seperated by a zerobyte.
		disc_content = h
		for tag in script.keys():
			# Only save tags, that contain strings
			# 'Date_object' will NOT be saved in the disc cache
			if type(script[tag]) == str:
				disc_content += CACHE_SEPERATOR.encode() \
								+ tag.encode() \
								+ b'\0' + script[tag].encode()

		# Writing cache entry to disc
		cache_path = self.cache_folder + '/' + name
		if os.path.exists(cache_path):
			os.remove(cache_path)
		cache_entry = open(cache_path, 'wb')
		cache_entry.write(disc_content)

		# Writing cache entry to heap
		if len(self.heap_cache) < self.cache_limit:
			# There is still enough space in heap
			pass
		elif name in self.heap_cache:
			# The entry already exists and will be overwritten
			pass
		else:
			# Delete the first entry in the cache to make room for the new one
			#
			# TODO: Find better solution
			#
			del self.heap_cache[list(self.heap_cache.keys())[0]]
		self.heap_cache[name] = (h, script)

	def check_cache_entry(self, name):
		'''Checks with the hash of a cache entry if a script has changed'''
		# Get hash-digest of scriptfile on disc
		file_data = open(self.script_folder + '/' + name, 'rb').read()
		h = hl.new(self.hash_alg, file_data).digest()

		# If the entry wasn't found in heap cache, the disc cache will be
		# checked. If the entry couldn't be found, False will be returned.
		if name in self.heap_cache:
			# Check cache entry in heap
			cached_h = self.heap_cache[name][0]
		else:
			# Check cache entry on disc
			cache_path = self.cache_folder + '/' + name
			if not os.path.exists(cache_path):
				# The cache entry does not exist
				return False
			cached_h = open(cache_path, 'rb').read(self.hash_size)
		return h == cached_h

	def get_cached_content(self, name):
		'''Returns the cached script'''
		if name in self.heap_cache:
			# If the entry is in the heap cache we can load it from there
			self.report('Loaded {} from heap cache'.format(name))
			return self.heap_cache[name][1]
		else:
			script = {}
			# Reading cached file
			cache_entry = open(self.cache_folder + '/' + name, 'rb').read()
			# Splitting the contents into the tuples of tags and values.
			# The first element is the hash value and can be ignored.
			cache_entry = cache_entry.split(CACHE_SEPERATOR.encode())[1:]
			# Creating new 
			for item in cache_entry:
				item = item.split(b'\0')
				tag = item[0].decode()
				value = item[1].decode()
				script[tag] = value
			# Parsing the date again so 'Date_object' can be restored, since it
			# was not stored in the disc cache.
			self.sl.__parse_date__(script)
			self.report('Loaded {} from disc cache'.format(name))
			return script

class ScriptLoader():
	'''Loader for the scripts'''
	def __init__(self, script_folder='scripts', cache_folder='.cache', caching=True):
		'''Constructor

		Keyword arguments:
		script_folder -- the directory for your scripts (default 'scripts')
		cache_folder -- the directory for cached files (default '.cache')
		caching -- specifies if caching is enabled (default True)
		'''
		self.script_folder = script_folder
		self.cache_handler = CacheHandler(self, script_folder = script_folder, cache_folder = cache_folder)
		if not caching:
			print("Caching disabled!")
		self.caching = caching

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
			func_call += ', ' + tag + ' = script["' + tag + '"]'
		func_call += ')'
		return eval(func_call)

	def get_single_script(self, script_name):
		'''Opens single script and parses it so it can be used with a html template

		Keyword arguments:
		script_name -- script name
		'''
		#
		# TODO: Delete this function and rename __get_script_info__
		#
		return self.__get_script_info__(script_name)

	def __get_script_info__(self, script_name):
		'''Open a script and parse its content 
		If the script is faulty, None is returned

		Keyword arguments:
		script_name -- script name
		'''
		script_info = {}
		script_info['Filename'] = script_name

		# The file couldn't be found
		script_path = os.getcwd() + '/' + self.script_folder
		if not script_name in os.listdir(script_path):
			return None

		# Checking cache entry
		if not (self.cache_handler.check_cache_entry(script_name) and self.caching):
			# Parsing file and creating new cache entry
			data = open(script_path + '/' + script_name).read()
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
					self.__parse_date__(script_info)

			# Final formatting
			self.__parse_content__(script_info)

			# Caching
			if self.caching:
				self.cache_handler.new_cache_entry(script_info)
		else:
			# Loading parsed contents
			script_info = self.cache_handler.get_cached_content(script_name)	

		return script_info

	def __parse_date__(self, script_info):
		'''Parsing the date, saving it in a different format and saving a 
		date-object for sorting.

		Keyword Arguments:
		script_info -- the script with the date
		'''
		# The unparsed date will be saved in 'Original_date'. This is done
		# so that the file can be parsed again after caching, so we can create
		# a new date object.
		if 'Original_date' in script_info:
			script_info['Date'] = script_info['Original_date']
		else:
			script_info['Original_date'] = script_info['Date']
		# Parsing
		d = script_info['Date'].split('/')
		d = date(day=int(d[0]), month=int(d[1]), year=int(d[2]))
		# Adding formatted date and date object
		script_info['Date'] = d.strftime("%d. %h %Y")
		script_info['Date_object'] = d

	def __get_scripts__(self, sort=True, key='Date_object'):
		'''Get all the scripts from the script directory and optionally sort them

		Keyword arguments:
		sort -- if the scripts should be sorted by date (default True)
		key -- the key to sort after (default 'Date_object')
		'''
		script_infos = []
		# Get listing of all the files in the script folder
		files = os.listdir( os.getcwd() + '/' +  self.script_folder )
		# Getting the info for every script
		for script in files:
			info = self.__get_script_info__(script)
			if info is not None:
				script_infos.append(info)
		# We can sort by any key in our script dict. The date object is the most
		# sensible.
		if sort:
			script_infos.sort(reverse=True, key=lambda x : x[key])
		return script_infos

	def __parse_content__(self, script_info, numbered=True):
		'''Generates a table of contents and modifies an articles content

		Keyword arguments:
		content -- the content to parse
		numbered -- if the sections should be numbered (default True)
		'''
		script = script_info['Content'].split(TEMPLATE_NEWLINE)
		
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
		toc += "</ul>"
		script_info['TableOfContents'] = toc
		script_info['Content'] = content

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
		