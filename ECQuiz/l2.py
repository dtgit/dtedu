#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-
#
# $Id: l2.py,v 1.2 2007/06/22 08:30:19 mxp Exp $
#
# L2 - A simple Lisp parser
#
# Copyright © 2006 Wolfram Fenske
#
# L2 is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# ECQuiz is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with L2; if not, write to the Free Software Foundation,
# Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301 USA

import re, sys, os, pickle
#import l_bootstrap
#from l_bootstrap import *

class TokenizerError(Exception):
    pass

class Symbol(object):
    def __init__(self, name):
        self.name = name
    def __cmp__(self, other):
        if type(other) is type(self):
            return cmp(self.name, other.name)
        else:
            return -1
    def __str__(self):
        return self.name
    def __repr__(self):
        return self.__str__()

class KwSymbol(Symbol):
    def __init__(self, name):
        Symbol.__init__(self, name[1:])
    def __str__(self):
        return ':' + self.name

class Tokenizer(object):
    RE_C_SINGLE = re.compile(r';.*')
    RE_SYM = r"(?:[-+_?<>=*/&%a-zA-Z0-9]+)"
    SEPARATORS = r"(?=[ \n\t()'#" + '"])'
    SHORTHAND = {r"'"  : 'quote',
                 r"#'" : 'fquote',
                 r"`"  : 'backquote',
                 r",@" : 'unquote-splice',
                 r","  : 'unquote'}
    TOKENS = [('(', re.compile(r'\(')),
              (')', re.compile(r'\)')),
              ('float', re.compile(r'[-+]?((0|([1-9]\d*))\.\d+)'
                                     + SEPARATORS)),
              ('int',   re.compile(r'[-+]?(0|([1-9]\d*))'
                                   + SEPARATORS)),
              (':sym', re.compile(r':%s' % RE_SYM)),
              ('sym',  re.compile(RE_SYM)),
              ('string', re.compile(r'"(?:[^"\\]+|(?:\\.)+)*"'))] \
              + [('shorthand', re.compile(short)) for short in
                 SHORTHAND.keys()]

    def init(self):
        self.tokens = []
    

    def emit_token(self, token):
        self.tokens.append(token)


    def c_single(self, string):
        """Remove single line comments (starting with ';').
        """
        sl = string.lstrip()
        m = self.RE_C_SINGLE.match(sl)
        if m:
            return sl[len(m.group(0)):]
        else:
            return sl


    def c_block(self, string):
        """Remove block comments (enclosed by '#|' and '|#') from
        [string].  Block comments can be nested.
        """
        sl = string.lstrip()
        if sl.startswith("#|"):
            sl = sl[2:]
            level = 1
            while True:
                try:
                    pos_o = sl.index("#|")
                except:
                    pos_o = None
                try:
                    pos_c = sl.index("|#")
                except:
                    raise TokenizerError("no closing |# for open #|")
                level -= 1 # since we found a |#
                sl = sl[pos_c+2 : ]
                if pos_o and (pos_o < pos_c):
                    level += 1
                if level == 0:
                    break
            return sl
        else:
            return sl


    def c_all(self, string):
        """Remove all comments(block and single line) from the string
        [string] that start at index 0 (after stripping leading
        whitespace).

        Return [string] without leading comments.
        """
        while True:
            new = self.c_single(self.c_block(string))
            if new == string:
                return string
            else:
                string = new


    def t_match(self, string, orig, t_type, t_pat):
        """Try to match a token in string [string] using the pattern
        [t_pat].  If successful, a token of type [t_type] is created
        and emitted via [emit_token].

        Comments and leading whitespace are stripped.

        The remaining part of the string that was not consumed is
        returned.
        """
        no_comment = self.c_all(string)
        sl = no_comment.lstrip()
        
#         if not hasattr(t_pat, "match"):
#             t_pat = re.compile(t_pat + self.SEPARATORS)
            
        match = t_pat.match(sl)
        if match:
            line_no, col_no, line = self.calc_pos(orig, sl)
            match_data = match.group(0)
            self.emit_token((t_type, match_data, line_no, col_no, line))
            return sl[len(match_data):]
        else:
            return sl

    def calc_pos(self, orig, rest):
        rest = rest.expandtabs()
        orig = orig.expandtabs()
        
        col_no = len(orig) - len(rest)
        line_no = 0
        
        for line in orig.split("\n"):
            l = len(line) + 1 # plus 1 for the linefeed
            if col_no >= l:
                col_no -= l
                line_no += 1
            else:
                return (line_no, col_no, line,)


    def tokenize(self, o_string):
        """Main function of the tokenizer.  Takes a string, tokenizes
        it and returns a list of tokens.
        """
        self.init() # reset the tokenizer
        string = o_string
        while True:
            match = False
            # Try to match one of the tokens in [self.TOKENS].  Set
            # [match] to [True] if we made any progress.
            for t_type, t_pat in self.TOKENS:
                rest = self.t_match(string, o_string, t_type, t_pat)
                if rest != string:
                    match = True
                    break
            
            if not rest: # nothing left to tokenize --> we're done
                break
            elif not match: # no token could be matched --> error
                line_no, col_no, bad_line = self.calc_pos(o_string, rest)
                maker = '^'.rjust(col_no+1)
                raise TokenizerError(
                    "Invalid syntax in line %d, column %d:\n"
                    "%s\n"
                    "%s"
                    % (line_no, col_no, bad_line, maker))
            else: # continue tokenizing
                string = rest
                
        return self.tokens


class ParserError(Exception):
    pass

interned_symbols = {}
def intern(name, klass):
    try:
        return interned_symbols[name]
    except KeyError:
        ret_val = klass(name)
        interned_symbols[name] = ret_val
        return ret_val

def mk_sym(name):
    return intern(name, Symbol)

def mk_kwsym(name):
    return intern(name, KwSymbol)

STR_ESCAPES = {
    'a' : '\a',
    'b' : '\b',
    'f' : '\f',
    'n' : '\n',
    'r' : '\r',
    't' : '\t',
    'v' : '\v',
    '"' : '"',
    '\\' : '\\',
    }

def mk_str(o_img):
    """Convert the image of a string into a real Python string.  This
    done by removing the enclosing double quotes and converting escape
    sequences.
    """
    img = o_img[1:-1] # string the double quotes
    r = ''
    esc = False
    for c in img:
        if esc:
            esc = False
            try:
                r += STR_ESCAPES[c]
            except KeyError, ke:
                raise ParserError("Invalid escape sequence in string: `\\%s'"
                                  % c)
        elif c == '\\':
            esc = True
        else:
            r += c
    return r

class Parser(object):


    def parse(self, token_list):
        self.parse_tree, rest = self.parse_sub(token_list)
        if rest:
            line_no, col_no, bad_line = rest[0][2:]
            maker = '^'.rjust(col_no+1)
            raise ParserError(
                "Superfluous ')' just before line %d, column %d:\n"
                "%s\n"
                "%s"
                % (line_no, col_no, bad_line, maker))
        
        return self.parse_tree

    
    CONV = {'int'     : int,
            'float'   : float,
            'sym'     : mk_sym,
            ':sym'    : mk_kwsym,
            'string'  : mk_str,
            }
    def parse_sub(self, token_list):
        if token_list:
            t_type, t_val = token_list[0][0:2]
            token_list = token_list[1:]

            if t_type == "(": # start of a list
                ret_val = []
                # read s-expressions and add them to [ret_val] until
                # we hit the matching ')'
                line_no = 1
                col_no = 0
                bad_line = ''
                while True: 
                    if not token_list:
                        maker = '^'.rjust(col_no+1)
                        raise ParserError(
                            "Missing ')' for opening '(' in line %d, "
                            "column %d:\n"
                            "%s\n"
                            "%s"
                            % (line_no, col_no, bad_line, maker))
                    t_type, t_val, line_no, col_no, bad_line = token_list[0]
                    if t_type == ")":
                        token_list = token_list[1:]
                        break
                    else:
                        sub_tree, token_list = self.parse_sub(token_list)
                        ret_val.append(sub_tree)
            
            elif t_type == 'shorthand': # shorthand notations
                ret_val = []
                sym_name = Tokenizer.SHORTHAND[t_val]
                ret_val.append(mk_sym(sym_name))
                sub_tree, token_list = self.parse_sub(token_list)
                ret_val.append(sub_tree)
            else: # another atom (i. e. an int, float, string, etc.)
                conv = self.CONV[t_type]
                ret_val = conv(t_val)
        else:
            ret_val = []
                    
        return ret_val, token_list
    

###############################################################################
#                            Command line options                             #
###############################################################################
def is_param_opt(option):
    return len(option) > 3

def get_opt_short_names(option, param=False):
    if param:        
        suffix = ' ' + option[3]
    else:
        suffix = ''
    return ['-' + o + suffix for o in option[0]]

def get_opt_long_names(option, param=False):
    if param:        
        suffix = '=' + option[3]
    else:
        suffix = ''
    return ['--' + o + suffix for o in option[1]]

def get_opt_names(option, param=False):
    return   get_opt_short_names(option, param=param) \
           + get_opt_long_names(option,  param=param)

def get_opts(option, getopt_options):
    return [o for o in getopt_options if o[0] in get_opt_names(option)]

def is_opt_present(option, getopt_options):
    return get_opts(option, getopt_options) != []

def get_opt_value(option, getopt_options):
    values = get_opts(option, getopt_options)
    if values:
        return values[-1][1]
    else:
        return None

O_HELP =           (('?', 'h',),
                    ('help',),
                    'Display this help screen.')
O_VERBOSE =        (('v',),
                    ('verbose',),
                    'Print what the program is currently doing to STDERR.')

OPTIONS =   [
    O_HELP,
    O_VERBOSE,
    ]
def option_key(o):
    # 1st rule: if one of the options has a short name and the other
    # one doesn't, the one with the short name is less than the other
    # one.
    if get_opt_short_names(o):
        key = 'a'
    else:
        key = 'b'
    # 2nd rule: otherwise, sort alphabetically, sort of
    names = get_opt_names(o)
    for name in names:
        for c in '-':
            name = name.replace(c, '')
        for c in name:
            key += c.lower() + 'ab'[c.isupper()]
    return key
#OPTIONS.sort(key=option_key)
OPTIONS.sort()

def print_help(out=sys.stdout):
    msg = 'Usage: %s [options] [file]\n' \
          'Options:' \
          % os.path.split(sys.argv[0])[-1]
    
    all_names = []
    for option in OPTIONS:
        names_list = get_opt_names(option, param=is_param_opt(option))
        names      = ', '.join(names_list)
        all_names.append(names)
        
    max_len = min(max(map(len, all_names)), 20)
    indent = '  '
    col_sep = '  '
    new_line = '\n%s%s%s' %(indent,
                            ''.join([' ' for n in range(max_len)]),
                            col_sep)
    len_left = len(new_line) - 1
    for option in OPTIONS:
        # Add the names
        names = all_names[0]
        need_new_line = len(names) > max_len
        if need_new_line:
            left = '%s%s%s'   % (indent, names, new_line)
        else:
            padding = ''.join([' ' for n in range(max_len - len(names))])
            left = '%s%s%s%s' % (indent, names, padding, col_sep)
        msg += '\n' + left

        # Add the description
        len_line = len_left
        is_new_line = True
        descr = option[2]
        descr_words = descr.split(' ')
        len_descr = len(descr_words)
        for i in range(len_descr):
            word = descr_words[i]
            last_word = i == len_descr - 1
            if not last_word:
                word += ' '
            len_word = len(word)
            if is_new_line or (len_line + len_word < 80):
                is_new_line = False                
            else:
                msg += new_line
                is_new_line = True
                len_line = len_left
            msg += word
            len_line += len_word

        # Done        
        all_names = all_names[1:]
    
    print >> out, msg

def print_usage(goe=None):
    if goe:
        print >> sys.stderr, "Error: %s" % str(goe)
    print_help(sys.stderr)
    sys.exit(1)


if __name__ == '__main__':
    from getopt import getopt, GetoptError
    try:
        o_short = ''
        o_long = []
        for option in OPTIONS:
            param = is_param_opt(option)
            suffix_s = ['', ':'][param]
            suffix_l = ['', '='][param]
            for name in option[0]:
                o_short += name + suffix_s
            for name in option[1]:
                o_long.append(name + suffix_l)
        
        options, args = getopt(sys.argv[1:], o_short, o_long)
    except GetoptError, goe:
        # print help information and exit:
        print_usage(goe)

    check_opt = (lambda opt: is_opt_present(opt, options))
    opt_val   = (lambda opt: get_opt_value(opt, options))

    verbose        = check_opt(O_VERBOSE)
    help           = check_opt(O_HELP)

    if help:
        print_help()
        sys.exit(0)

    if len(args) > 1:
        print_usage()

    if args:
        string = open(args[0], 'r').read()
    else:
        string = sys.stdin.read()
    
    tokenizer = Tokenizer()
    parser    = Parser()

    if verbose:
        sys.stderr.write(';; TOKENIZING ... ')
        sys.stderr.flush()
    try:
        token_list = tokenizer.tokenize("(quiz\n%s\n)" % (string,))
    except TokenizerError, te:
        print >> sys.stderr, "Tokenizer Error:", str(te)
        sys.exit(2)
    if verbose:
        sys.stderr.write('DONE\n')
        sys.stderr.flush()
    if verbose:
        sys.stderr.write(';; PARSING ... ')
        sys.stderr.flush()
    try:
        parse_tree = parser.parse(token_list)
    except ParserError, pe:
        print >> sys.stderr, "Parser Error:", str(pe)
        sys.exit(2)
    if verbose:
        sys.stderr.write('DONE\n')
        sys.stderr.flush()

    print parse_tree
