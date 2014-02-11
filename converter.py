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
        self.poop(self.tree)
        with open(self.output_file, 'w') as o:
            o.write(''.join(self.buf).encode('utf-8'))

    def poop(self, node):
        getattr(self, 'poop' + node.__class__.__name__)(node)

    def poopTemplateNode(self, node):
        for child in node.get_children():
            self.poop(child)

    def poopCode(self, node):
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

    def poopText(self, node):
        parser = HTMLPooper(self)
        parser.feed(node.content)

    def poopNamespaceTag(self, node):
        self.poop_simple_tag(node, 'namespace')

    def poopIncludeTag(self, node):
        self.poop_simple_tag(node, 'include')

    def poopCallTag(self, node):
        print """plim does not support <% call %> tag, you may need to modify this manually.
see http://docs.makotemplates.org/en/latest/defs.html#defs-with-content"""
        indent = ' ' * self.indent
        expr = node.expression.replace('\n', '')
        self.buf.append(indent + '-call ' + expr + '"' + '\n')
        self.indent += 2
        for child in node.get_children():
            self.poop(child)
        self.indent -= 2

    def poopComment(self, node):
        indent = ' ' * self.indent
        for line in node.text.strip().split('\n'):
            self.buf.append(indent + '/ ' + line + '\n')

    def poop_simple_tag(self, node, name):
        indent = ' ' * self.indent
        file = node.attributes['file'] if 'file' in node.attributes else node.attributes['module']
        attrs = ''
        for attr in ['name', 'import', 'inheritable']:
            if attr in node.attributes:
                attrs += '%s="%s" ' % (attr, node.attributes[attr])
        self.buf.append(indent + '-%s ' % name + attrs + file + '\n')

    def poopInheritTag(self, node):
        self.poop_simple_tag(node, 'inherit')

    def poopControlLine(self, node):
        indent = ' ' * (self.indent if node.is_primary else self.indent - 2)
        if node.isend:
            self.indent -= 2
        else:
            if node.is_primary:
                self.indent += 2
            self.buf.append(indent + '-' + node.text.strip(' %:') + '\n')

    def poopExpression(self, node):
        raise NotImplementedError

    def poopTextTag(self, node):
        raise NotImplementedError

    def poopBlockTag(self, node):
        raise NotImplementedError

    def poopPageTag(self, node):
        raise NotImplementedError

    def poopCallNamespaceTag(self, node):
        raise NotImplementedError

    def poopDefTag(self, node):
        buf = ' ' * self.indent + '-def ' + node.attributes['name'] + '\n'
        self.buf.append(buf)
        self.indent += 2
        for child in node.get_children():
            self.poop(child)
        self.indent -= 2
        self.buf.append('\n')
