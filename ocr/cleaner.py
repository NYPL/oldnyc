#!/usr/bin/env python
'''Clean up a few common warts in the OCR data from Ocropus.

These include:
    - \& --> &
    - '' --> "
    - Dropping "NO REPRODUCTIONS" lines
    - Merging lines into paragraphs
'''

import json
import re

import editdistance


def swap_chars(txt):
    '''Remove a few common Ocropusisms, like \& and '' '''
    return re.sub(r"''", '"', re.sub(r'\\&', '&', txt))


# See https://github.com/danvk/oldnyc/issues/39
WARNINGS = [
  'NO REPRODUCTIONS',
  'MAY BE REPRODUCED',
  'CREDIT LINE IMPERATIVE',
  'CREDIT LINE IMPERATIVE ON ALL REPRODUCTIONS'
]


def is_warning(line):
    line = re.sub(r'[,.]$', '', line)
    for base in WARNINGS:
        d = editdistance.eval(base, line)
        if 2 * d < len(base):
            return True
    return False


def remove_warnings(txt):
    '''Remove lines like "NO REPRODUCTIONS".'''
    return '\n'.join(line for line in txt.split('\n') if not is_warning(line))


def merge_lines(txt):
    '''Merge sequential lines in a paragraph into a single line.

    This can't be done reliably from just the OCR'd text -- it would be better
    to do this using the bounding boxes of the original images -- but the
    monospaced font allows a reasonable approximation. Merging these lines is
    essential for letting the browser reflow the text, especially on narrower
    screens.
    '''
    lines = txt.split('\n')
    width = max(len(line) for line in lines)
    join_width = width - 15
    if join_width < 25:
        return txt  # be conservative

    txt = ''
    for i, line in enumerate(lines):
        is_hyphen = False
        if line.endswith('-'):
            # A hyphen at end of line is an automatic join.
            txt += line[:-1]
            continue

        txt += line
        if len(line) < join_width:
            txt += '\n'
        elif i < len(lines) - 1 and len(lines[i + 1]) < join_width:
            txt += '\n'
        else:
            txt += ' '
    if txt.endswith('\n\n'):
        txt = txt[:-1]
    return txt


def clean(txt):
    return merge_lines(remove_warnings(swap_chars(txt)))


if __name__ == '__main__':
    ocr = json.load(open('ocr/ocr.json'))
    for k, txt in ocr.iteritems():
        print k
        clean(txt)
        # print '%s:\n%s\n\n-----\n' % (k, clean(txt))
        #txt = clean(txt)
        # txt = '\n'.join('%2d %s' % (len(line), line) for line in txt.split('\n'))
        # print '%s:\n%s\n\n------\n' % (k, txt)
