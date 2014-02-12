# coding: utf-8

from mako.lexer import Lexer as _Lexer
from mako.parsetree import Text, Expression

class Lexer(_Lexer):
    def parse(self):
        tree = super(Lexer, self).parse()
        return self.merge_text_and_expr(tree)

    def merge_text_and_expr(self, tree):
        nodes = []
        merged_node = None
        for node in tree.nodes:
            if isinstance(node, Text) or isinstance(node, Expression):
                if not merged_node:
                    merged_node = Text('', source='', lineno=0, pos=0, filename='')
                if isinstance(node, Text):
                    merged_node.content += node.content
                else:
                    args = node.escapes_code.args
                    args = args and '|' + ', '.join(args) or ''
                    merged_node.content += '${' + node.text.strip() + args + '}'
            else:
                if merged_node:
                    nodes.append(merged_node)
                    merged_node=None
                nodes.append(node)
            if node.get_children():
                self.merge_text_and_expr(node)
        if merged_node:
            nodes.append(merged_node)
        tree.nodes = nodes
        return tree
