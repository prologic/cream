from rply import LexerGenerator
from rply.token import Token
try:
    import rpython.rlib.rsre.rsre_re as re
except:    
    import re

lg = LexerGenerator()

# build up a set of token names and regexes they match
lg.add('FLOAT', '-?\d+\.\d+')
lg.add('INTEGER', '-?\d+')
lg.add('STRING', '(""".*?""")|(".*?")|(\'.*?\')')
lg.add('BOOLEAN', "true(?!\w)|false(?!\w)")
lg.add('IF', 'if(?!\w)')
lg.add('ELSE', 'else(?!\w)')
lg.add('END', 'end(?!\w)')
lg.add('AND', "and(?!\w)")
lg.add('OR', "or(?!\w)")
lg.add('NOT', "not(?!\w)")
# lg.add('LET', 'let(?!\w)')
lg.add('FOR', 'for(?!\w)')
lg.add('WHILE', 'while(?!\w)')
lg.add('BREAK', 'break(?!\w)')
lg.add('CONTINUE', 'continue(?!\w)')
lg.add('MATCH', 'match(?!\w)')
lg.add('ENUM', 'enum(?!\w)')
lg.add('NEW', 'new(?!\w)')
lg.add('RETURN', 'return(?!\w)')
lg.add('TYPE', 'type(?!\w)')
lg.add('TYPE_ARRAY', 'array(?!\w)')
lg.add('TYPE_DICT', 'dict(?!\w)')
lg.add('TYPE_INTEGER', 'int(?!\w)')
lg.add('TYPE_STRING', 'str(?!\w)')
lg.add('TYPE_FLOAT', 'float(?!\w)')
lg.add('TYPE_CHAR', 'char(?!\w)')
lg.add('TYPE_LONG', 'long(?!\w)')
lg.add('TYPE_DOUBLE', 'double(?!\w)')
lg.add('RECORD', 'record(?!\w)')
lg.add('FUNCTION', 'func(?!\w)')
lg.add('LAMBDA', 'fn(?!\w)')
lg.add('PRIVATE', 'priv(?!\w)')
lg.add('MODULE', 'mod(?!\w)')
lg.add('TRAIT', 'trait(?!\w)')
lg.add('IMPLEMENT', 'impl(?!\w)')
lg.add('IMPORT', 'import(?!\w)')
lg.add('SEND', 'send(?!\w)')
lg.add('RECEIVE', 'receive(?!\w)')
lg.add('IDENTIFIER', "[a-zA-Z_][a-zA-Z0-9_]*")
lg.add('PLUS', '\+')
lg.add('==', '==')
lg.add('!=', '!=')
lg.add('>=', '>=')
lg.add('<=', '<=')
lg.add('>', '>')
lg.add('<', '<')
lg.add('=', '=')
lg.add('[', '\[')
lg.add(']', '\]')
lg.add('{', '\{')
lg.add('}', '\}')
lg.add('|', '\|')
lg.add(',', ',')
lg.add('DOT', '\.')
lg.add('COLON', ':')
lg.add('MINUS', '-')
lg.add('MUL', '\*')
lg.add('DIV', '/')
lg.add('MOD', '%')
lg.add('(', '\(')
lg.add(')', '\)')
lg.add('NEWLINE', '\n+')
lg.add('WHITESPACE', '\t+')

# ignore whitespace
# lg.ignore('[ \t\r\f\v]+')
lg.ignore('[ \r\f\v]+')

lexer = lg.build()

def trim_comment(source):
    comments = r'(#.*)(?:\n|\Z)'
    comment = re.search(comments,source)
    while comment is not None:
        start, end = comment.span(1)
        assert start >= 0 and end >= 0
        source = source[0:start] + source[end:] # remove comments
        comment = re.search(comments,source)
    return source

def trim_multiline(source):
    multiline = r'([\s]+)(?:\n)'
    line = re.search(multiline,source)
    while line is not None:
        start, end = line.span(1)
        assert start >= 0 and end >= 0
        source = source[0:start] + source[end:] # remove empty lines
        line = re.search(multiline,source)
    return source

class CreamStream(object):
    def __init__(self, stream):
        self.stream = []
        self.idx = 0

        TAB_WIDTH = 4
        indent = 0
        current_indent = 0
        indent_token = None
        indent_start_pos = 0

        while True:
            try:
                token = stream.next()

            except StopIteration:
                if current_indent > 0:
                    print(current_indent)
                    dedents = [Token('DEDENT', '')] * (current_indent / TAB_WIDTH)
                    self.stream.extend(dedents)
                break

            token_type = token.gettokentype()
            if token_type == 'WHITESPACE':
                indent_token = token
                # WHITESPACE is tab only now.
                indent = len(token.getstr()) * TAB_WIDTH
            elif token_type == 'NEWLINE':
                # print("%d <=> %d" % (current_indent, indent))
                if current_indent < indent:
                    indent_token.name = 'INDENT'
                    current_indent = indent
                elif current_indent > indent:
                    dedent_num = (current_indent - indent) / TAB_WIDTH
                    for i in range(0, dedent_num):
                        if not indent_token:
                            indent_token = Token('', '', token.getsourcepos())
                            self.stream.insert(indent_start_pos, indent_token)
                        indent_token.name = 'DEDENT'
                        indent_token = None
                    current_indent = indent
                else:
                    if indent_token:
                        self.stream.remove(indent_token)
                indent = 0
                indent_token = None
                indent_start_pos = len(self.stream) + 1

            self.stream.append(token)

    def next(self):
        if self.idx < len(self.stream):
            token = self.stream[self.idx]
            self.idx += 1
            return token
        else:
            raise StopIteration

    def __str__(self):
        return "%s" % self.stream

def lex(source):
    source = trim_comment(source)
    # source = trim_multiline(source)

    # print "source is now: %s" % source

    stream = CreamStream(lexer.lex(source))
    print(stream)
    return stream
