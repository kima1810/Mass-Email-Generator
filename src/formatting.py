import re


def convert_markdown_to_html(text):
    """Convert markdown-style formatting to HTML."""
    text = re.sub(r'\*\*([^\*]+)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'__([^_]+)__', r'<strong>\1</strong>', text)

    text = re.sub(r'\*([^\*]+)\*', r'<em>\1</em>', text)
    text = re.sub(r'_([^_]+)_', r'<em>\1</em>', text)

    text = re.sub(r'~~([^~]+)~~', r'<u>\1</u>', text)
    text = re.sub(r'\{([a-zA-Z]+):([^\}]+)\}', r'<span style="color:\1">\2</span>', text)
    text = re.sub(r'\[([^\]]+)\]\(([^\)]+)\)', r'<a href="\2">\1</a>', text)

    return text


def text_to_html(text):
    """Convert plain text to HTML, preserving formatting."""
    html_text = convert_markdown_to_html(text)
    return html_text.replace('\n', '<br>')


def personalize_template(template, first_name):
    return template.replace('{{first_name}}', str(first_name))
