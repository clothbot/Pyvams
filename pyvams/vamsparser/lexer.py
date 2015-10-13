#--------------------------
# lexer.py
#
# Verilog-AMS Lexical Analyzer
#
# Copyright (C) 2015, Andrew Plumb
# License: Apache 2.0
#--------------------------
from __future__ import absolute_import
from __future__ import print_function
import sys
import os
import re

sys.path.insert(0, os.path.dirname(os.path.dirname(os.dirname(os.path.abspath(__file)))) )

from pyvams.vamsparser import ply
from pyvams.vamsparser.ply.lex import *

class VerilogAMSLexer(object):
    """ Verilog-AMS Lexical Analyzer """
    def __init__(self, error_func):
        self.filename = ''
        self.error_func = error_func
        self.directives = []
        self.default_nettype = 'wire'

    def build(self, **kwargs):
        self.lexer = ply.lex.lex(object=self, **kwargs)
    def input(self, data):
        self.lexer.input(data)

    def reset_lineno(self):
        self.lexer.lineno = 1

    def get_directives(self):
        return tuple(self.directives)

    def get_default_nettype(self):
        return self.default_nettype

    def token(self):
        return self.lexer.token()

    // Annex B - List of keywords - Table B.1--Reserved keywords
    keywords = (
        'ABOVE','ABS','ABSDELAY','ABSDELTA','ABSTOL','ACCESS','ACOS','ACOSH','AC_STIM','ALIASPARAM',
        'ALWAYS','ANALOG','ANALYSIS','AND','ASIN','ASINH','AUTOMATIC','BEGIN','BRANCH','BUF',
        'BUFIF0','BUFIF1','CASE','CASEX','CASEZ','CEIL','CELL','CMOS','CONFIG','CONNECT',
        'CONNECTMODULE','CONNECTRULES','CONTINUOUS','COS','COSH','CROSS','DDT','DDT_NATURE','DDX','DEASSIGN',
        'DEFAULT','DEFPARAM','DESIGN','DISABLE','DISCIPLINE','DISCRETE','DOMAIN','DRIVER_UPDATE','EDGE','ELSE',
        'END','ENDCASE','ENDCONFIG','ENDCONNECTRULES','ENDDISCIPLINE','ENDFUNCTION','ENDGENERATE','ENDMODULE','ENDNATURE','ENDPARAMSET',
        'ENDPRIMITIVE','ENDSPECIFY','ENDTABLE','ENDTASK','EVENT','EXCLUDE','EXP','FINAL_STEP','FLICKER_NOISE','FLOOR',
        'FLOW','FOR','FORCE','FOREVER','FORK','FROM','FUNCTION','GENERATE','GENVAR','GROUND',
        'HIGHZ0','HIGHZ1','HYPOT','IDT','IDTMOD','IDT_NATURE','IF','IFNONE','INCDIR','INCLUDE',
        'INF','INITIAL','INITIAL_STEP','INOUT','INPUT','INSTANCE','INTEGER','JOIN','LAPLACE_ND','LAPLACE_NP',
        'LAPLACE_ZD','LAPLACE_ZP','LARGE','LAST_CROSSING','LIBLIST','LIBRARY','LIMEXP','LN','LOCALPARAM','LOG',
        'MACROMODULE','MAX','MEDIUM','MERGED','MIN','MODULE','NAND','NATURE','NEGEDGE','NET_RESOLUTION',
        'NMOS','NOISE_TABLE','NOISE_TABLE_LOG','NOR','NOSHOWCANCELLED','NOT','NOTIF0','NOTIF1','OR','OUTPUT',
        'PARAMETER','PARAMSET','PMOS','POSEDGE','POTENTIAL','POW','PRIMITIVE','PULL0','PULL1','PULLDOWN',
        'PULLUP','PULSESTYLE_ONEVENT','PULSESTYLE_ONDETECT','RCMOS','REAL','REALTIME','REG','RELEASE','REPEAT','RESOLVETO',
        'RNMOS','RPMOS','RTRAN','RTRANIF0','RTRANIF1','SCALARED','SIN','SINH','SHOWCANCELLED','SIGNED',
        'SLEW','SMALL','SPECIFY','SPECPARAM','SPLIT','SQRT','STRING','STRONG0','STRONG1','SUPPLY0',
        'SUPPLY1','TABLE','TAN','TANH','TASK','TIME','TIMER','TRAN','TRANIF0','TRANIF1',
        'TRANSITION','TRI','TRI0','TRI1','TRIAND','TRIOR','TRIREG','UNITS','UNSIGNED','USE',
        'UWIRE','VECTORED','WAIT','WAND','WEAK0','WEAK1','WHILE','WHITE_NOISE','WIRE','WOR',
        'WREAL','XNOR','XOR','ZI_ND','ZI_NP','ZI_ZD','ZI_ZP',
        )

    reserved = {}
    for keyword in keywords:
        reserved[keyword.lower()] = keyword

    operators = (
        'PLUS','MINUS','POWER','TIMES','DIVIDE','MOD',
        'SYM_NOT','SYM_OR','SYM_NOR','SYM_AND','SYM_NAND','SYM_XOR','SYM_XNOR',
        'LOR','LAND','LNOT',
        'LSHIFTA','RSHIFTA','LSHIFT','RSHIFT',
        'LT','GT','LE','GE','EQ','NE','EQL','NEL',
        'COND',
        'EQUALS',
        )

    tokens = keywords + operators + (
        'ID',
        'AT','COMMA','COLON','SEMICOLON','DOT',
        'PLUSCOLON','MINUSCOLON',
        'FLOATNUMBER','STRING_LITERAL',
        'INTNUMBER_DEC','SIGNED_INTNUMBER_DEC',
        'INTNUMBER_HEX','SIGNED_INTNUMBER_HEX',
        'INTNUMBER_OCT','SIGNED_INTNUMBER_OCT',
        'INTNUMBER_BIN','SIGNED_INTNUMBER_BIN',
        'LPAREN','RPAREN','LBRACKET','RBRACKET','LBRACE','RBRACE',
        'DELAY','DOLLAR',
        )

    skipped = (
        'COMMENTOUT','LINECOMMENT','DIRECTIVE',
        )

    # Ignore
    t_ignore = ' \t'

    # Directive
    directive = r"""\`.*?\n"""

    @TOKEN(directive)
    def t_DIRECTIVE(self,t):
        self.directives.append( (self.lexer.lineno,t.value) )
        t.lexer.lineno += t.value.count("\n")
        m = re.match("^`default_nettype\s+(.+)\n",t.value)
        if m: self.default_nettype = m.group(1)
        pass

    # Comment
    linecomment = r"""//.*?\n"""
    commentout = r"""/\*(.|\n)*?\*/"""

    @TOKEN(linecomment)
    def t_LINECOMMENT(self,t):
        t.lexer.lineno += t.value.count("\n")
        pass

    @TOKEN(commentout)
    def t_COMMENTOUT(self,t):
        t.lexer.lineno += t.value.count("\n")
        pass

    # Operator
    t_LOR = r'\|\|'
    t_LAND = r'\&\&'

    t_SYM_NOR = r'~\|'
    t_SYM_NAND = r'~\&'
    t_SYM_XNOR = r'~\^'
    t_SYM_OR = r'\|'
    t_SYM_AND = r'\&'
    t_SYM_XOR = r'\^'
    t_SYM_NOT = r'~'

    t_LNOT = r'!'

    t_LSHIFTA = r'<<<'
    t_RSHIFTA = r'>>>'
    t_LSHIFT = r'<<'
    t_RSHIFT = r'>>'

    t_EQL = r'==='
    t_NEL = r'!=='
    t_EQ = r'=='
    t_NE = r'!='

    t_LE = r'<='
    t_GE = r'>='
    t_LT = r'<'
    t_GT = r'>'

    t_POWER = r'\*\*'
    t_PLUS = r'\+'
    t_MINUS = r'-'
    t_TIMES = r'\*'
    t_DIVIDE = r'/'
    t_MOD = r'%'

    t_CONT = r'\?'
    t_EQUALS = r'='

    t_PLUSCOLON = r'\+:'
    t_MINUSCOLON = r'-:'

    t_AT = r'@'
    t_COMMA = r','
    t_SEMICOLON = r';'
    t_COLON = r':'
    t_DOT = r'\.'

    t_LPAREN = r'\('
    t_RPAREN = r'\)'
    t_LBRACKET = r'\['
    t_RBRACKET = r'\]'
    t_LBRACE = r'\{'
    t_RBRACE = r'\}'

    t_DELAY = r'\#'
    t_DOLLAR = r'\$'

    bin_number = '[0-9]*\'[bB][0-1xXzZ?][0-1xXzZ?_]*'
    signed_bin_number = '[0-9]*\'[sS][bB][0-1xZzZ?][0-1xXzZ?_]*'
    octal_number = '[0-9]*\'[oO][0-7xXzZ?][0-7xXzZ?_]*'
    signed_octal_number = '[0-9]*\'[sS][oO][0-7xXzZ?][0-7xXzZ?_]*'
    hex_number = '[0-9]*\'[hH][0-9a-fA-FxXzZ?][0-9a-fA-FxXzZ?_]*'
    signed_hex_number = '[0-9]*\'[sS][hH][0-9a-fA-FxXzZ?][0-9a-fA-FxXzZ?_]*'

    decimal_number = '([0-9]*\'[dD][0-9xXzZ?][0-9xXzZ?_]*)|([0-9][0-9_]*)'
    signed_decimal_number = '[0-9]*\'[sS][dD][0-9xXzZ?][0-9xXzZ?_]*'

    exponent_part = r"""([eE][-+]?[0-9]+)"""
    fractional_constant = r"""([0-9]*\.[0-9]+)|([0-9]+\.)"""
    float_number = '(((('+fractional_constant+')'+exponent_part+'?)|([0-9]+'+exponent_part+')))'

    simple_escape = r"""([a-zA-Z\\?'"])"""
    octal_escape = r"""([0-7]{1,3})"""
    hex_escape = r"""(x[0-9a-fA-F]+)"""
    escape_sequence = r"""(\\("""+simple_escape+'|'+octal_escape+'|'+hex_escape+'))'
    string_char = r"""([^"\\\n]|"""+escape_sequence+')'
    string_literal = '"'+string_char+'*"'

    identifier = r"""(([a-zA-Z_])([a-zA-Z_0-9$])*)|((\\\S)(\S)*)"""

    @TOKEN(string_literal)
    def t_STRING_LITERAL(self, t):
        return t

    @TOKEN(float_number)
    def t_FLOATNUMBER(self, t):
        return t

    @TOKEN(signed_bin_number)
    def t_SIGNED_INTNUMBER_BIN(self, t):
        return t

    @TOKEN(bin_number)
    def t_INTNUMBER_BIN(self, t):
        return t

    @TOKEN(signed_octal_number)
    def t_SIGNED_INTNUMBER_OCT(self, t):
        return t

    @TOKEN(octal_number)
    def t_INTNUMBER_OCT(self, t):
        return t

    @TOKEN(signed_hex_number)
    def t_SIGNED_INTNUMBER_HEX(self, t):
        return t

    @TOKEN(hex_number)
    def t_INTNUMBER_HEX(self, t):
        return t

    @TOKEN(signed_decimal_number)
    def t_SIGNED_INTNUMBER_DEC(self, t):
        return t

    @TOKEN(decimal_number)
    def t_INTNUMBER_DEC(self, t):
        return t

    @TOKEN(identifier)
    def t_ID(self, t):
        t.type = self.reserved.get(t.value, 'ID')
        return t

    def t_NEWLINE(self, t):
        r'\n+'
        t.lexer.lineno += t.value.count("\n")
        pass

    def t_error(self, t):
        msg = 'Illegal character %s' % repr(t.value[0])
        self._error(msg, t)

    def _error(self, msg, token):
        location = self._make_tok_location(token)
        self.error_func(msg, location[0], location[1])
        self.lexer.skip(1)

    def _find_tok_column(self, token):
        i = token.lexpos
        while i > 0:
            if self.lexer.lexdata[i] == '\n': break
            i -= 1
        return (token.lexpos - i) + 1

    def _make_tok_location(self, token):
        return (token.lineno, self._find_tok_column(token))

#-------------------------------------------------------------------------------
def dump_tokens(text):
    def my_error_func(msg, a, b):
        sys.write(msg + "\n")
        sys.exit()
                            
    lexer = VerilogAMSLexer(error_func=my_error_func)
    lexer.build()
    lexer.input(text)

    ret = []
                                                
    # Tokenize
    while True:
        tok = lexer.token()
        if not tok: break # No more input
        ret.append("%s %s %d %s %d\n" %
                   (tok.value, tok.type, tok.lineno, lexer.filename, tok.lexpos))
    
    return ''.join(ret)

#-------------------------------------------------------------------------------
if __name__ == '__main__':
    import pyvams.utils.version
    from pyvams.vparser.preprocessor import preprocess
    from optparse import OptionParser

    INFO = "Verilog Preprocessor"
    VERSION = pyvams.utils.version.VERSION
    USAGE = "Usage: python preprocessor.py file ..."

    def showVersion():
        print(INFO)
        print(VERSION)
        print(USAGE)
        sys.exit()

    optparser = OptionParser()
    optparser.add_option("-v","--version",action="store_true",dest="showversion",
                         default=False,help="Show the version")
    optparser.add_option("-I","--include",dest="include",action="append",
                         default=[],help="Include path")
    optparser.add_option("-D",dest="define",action="append",
                         default=[],help="Macro Definition")
    (options, args) = optparser.parse_args()

    filelist = args
    if options.showversion:
        showVersion()

    for f in filelist:
        if not os.path.exists(f): raise IOError("file not found: " + f)

    if len(filelist) == 0:
        showVersion()
    
    text = preprocess(filelist, 
                      preprocess_include=options.include,
                      preprocess_define=options.define)

    dump = dump_tokens(text)
    
    print(dump)

