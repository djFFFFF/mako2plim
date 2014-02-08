# coding: utf-8

from HTMLParser import HTMLParser

class Attributes(object):
    def __init__(self, attrs):
        self.attrs = attrs

    def __getattr__(self, name):
        name = name.strip('_')
        for k, v in self.attrs:
            if k == name:
                return v

    def get_other_attrs(self):
        for k, v in self.attrs:
            if not (k == 'id' or k == 'class'):
                yield k, v

class HTMLPooper(HTMLParser):
    unindent_tags = ['br', 'link', 'img']

    def __init__(self, converter):
        HTMLParser.__init__(self)
        self.converter = converter

    def handle_starttag(self, tag, attrs):
        self.parse_tag(tag, attrs)
        if tag not in self.unindent_tags:
            self.converter.indent += 2

    def handle_startendtag(self, tag, attrs):
        self.parse_tag(tag, attrs)

    def parse_tag(self, tag, attrs):
        attrs = Attributes(attrs)
        if tag == 'div' and (attrs.id or attrs._class):
            tag = ''
        indent = ' ' * self.converter.indent
        buf = indent + tag
        if attrs.id:
            buf = buf + '#' + attrs.id
        if attrs._class:
            for class_name in attrs._class.split():
                buf = buf + '.' + class_name
        for k, v in attrs.get_other_attrs():
            buf = buf + ' ' + k + '="' + v + '"'
        self.converter.buf.append(buf + '\n')
    def handle_endtag(self, tag):
        self.converter.indent -= 2

    def handle_data(self, data):
        data = data.strip()
        if data:
            self.converter.buf.append(' ' * self.converter.indent + data + '\n')
