# flask-article

## What does it do?

**flask-article** is a microscopic library to load scripts in an easy-to-use format in order to create articles or blog-posts without using a database. Even though it creates html code that is independent of *Flask* it is made to be used with it!

## Usage

By default, flask-article uses the directory **/scripts** to load the scripts for inserting the content into a HTML-template.

The functions use the dict-datatype to return the parsed contents.
For usual usage you should use the ScriptLoader:
```python
sl = ScriptLoader()
script = sl.get_single_script(<script filename>)
rendered_article = sl.render_article(script, <template filename>)
```
You then can return the rendered article in your function when using Flask.

The keys to use from the resulting dict are:

| Key            | Value                               | HTML-Code  |
| -------------- |:-----------------------------------:| :--------: |
| Content        | The articles content                | Yes        |
| TableOfContents| The table of contents               | Yes        |
| Title          | The articles title                  | No         | 
| Date           | The articles date                   | No         | 
| Author         | The articles author                 | No         | 
| Description    | The articles description            | No         | 
| Keywords       | The articles keywords               | No         | 
| Filename       | The filename behind the article     | No         | 
| Date_object    | A python date-object (for sorting)  | No         | 

When using the values of the dict to insert into your Jinja2-Template you have to make sure that the values containing pure HTML-code have to be inserted into the template without escaping!
```HTML
{{ TableOfContents|safe }}		
{{ Content|safe }}
```
If you want to offer a list of all the articles to your users you can use:
```python
articles = sl.get_article_list()
```
This time the return value is **HTML-code** so don't escape it.

## Script Format

The script starts with tags and values:
```
{Title}{Example article}
{Description}{Just an example}
{Keywords}{Example, Flask}
{Date}{13/12/2015}
{Author}{Philipp Hagenlocher}
```
You can insert as much tags as you want. They will all be parsed and added to the returned dictionary. *Title*, *Date* and *Author* are **required**!

After the tag section the normal content starts. It works like this:
```
* Sectiontitle

** Subsectiontitle
```
The sections and subsections will be numbered automatically. The titles (aswell as the title of the article) will be titlecased. If you don't want them to be titlecase you have to add a '_' infront of the title like this:
```
{Title}{_Example article}

      ...

*_ Sectiontitle

**_ Subsectiontitle
```

You can use HTML-code within the scripts.

## Planned features

* Caching created HTML-code
* Compatibility to Markdown
