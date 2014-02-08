# coding: utf-8

from lexer import Lexer
from htmlparser import HTMLPooper

class Converter(object):
    def __init__(self, input_file):
        self.input_file = input_file
        self.indent = 0
        self.buf = []
        with open(input_file, 'r') as f:
            data = f.read()
            self.tree = Lexer(data, input_encoding='utf-8').parse()

    @property
    def output_file(self):
        if self.input_file.endswith('html'):
            return self.input_file[:-4] + 'plim'
        return self.input_file + '.plim'

    def convert(self):
        self.blahblah(self.tree)
        with open(self.output_file, 'w') as o:
            o.write(''.join(self.buf).encode('utf-8'))

    def blahblah(self, node):
        getattr(self, 'push' + node.__class__.__name__)(node)

    def pushTemplateNode(self, node):
        for child in node.get_children():
            self.blahblah(child)

    def pushCode(self, node):
        header = '-py!' if node.ismodule else '-py'
        texts = node.text.strip().split('\n')
        indent = ' ' * self.indent
        if len(texts) == 1:
            self.buf.append(indent + header + ' ' + texts[0].strip() + '\n')
        else:
            self.buf.append(indent + header + '\n')
            indent += '  '
            for line in texts:
                if line.strip():
                    self.buf.append(indent + line + '\n')
        if node.ismodule:
            self.buf.append('\n')

    def pushText(self, node):
        parser = HTMLPooper(self)
        parser.feed(node.content)

    def pushNamespaceTag(self, node):
        self.push_simple_tag(node, 'namespace')

    def pushComment(self, node):
        indent = ' ' * self.indent
        for line in node.text.strip().split('\n'):
            self.buf.append(indent + '/ ' + line + '\n')

    def push_simple_tag(self, node, name):
        indent = ' ' * self.indent
        file = node.attributes['file'] if 'file' in node.attributes else node.attributes['module']
        attrs = ''
        for attr in ['name', 'import', 'inheritable']:
            if attr in node.attributes:
                attrs += '%s="%s" ' % (attr, node.attributes[attr])
        self.buf.append(indent + '-%s ' % name + attrs + file + '\n\n')

    def pushInheritTag(self, node):
        self.push_simple_tag(node, 'inherit')

    def pushControlLine(self, node):
        indent = ' ' * (self.indent if node.is_primary else self.indent - 2)
        if node.isend:
            self.indent -= 2
        else:
            if node.is_primary:
                self.indent += 2
            self.buf.append(indent + '-' + node.text.strip(' %:') + '\n')

    def pushExpression(self, node):
        raise NotImplementedError

    def pushDefTag(self, node):
        buf = ' ' * self.indent + '-def ' + node.attributes['name'] + '\n'
        self.buf.append(buf)
        self.indent += 2
        for child in node.get_children():
            self.blahblah(child)
        self.indent -= 2
        self.buf.append('\n')
