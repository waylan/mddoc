# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from markdown.extensions import Extension
from markdown.preprocessors import Preprocessor
from .doc import render
import re

# Doc Tag: [% object.name %]
DOC_TAG_RE = re.compile(r'^\s{0,3}\[%\s*([^ %]+)\s*%\]\s*$')

class DocExtension(Extension):
    def extendMarkdown(self, md, md_globals):
       docprocessor = DocPreprocessor()
       md.preprocessors.add('mddoc', docprocessor,'>normalize_whitespace')

class DocPreprocessor(Preprocessor):
    def run(self, lines):
        new_lines = []
        for line in lines:
            m = DOC_TAG_RE.match(line)
            if m:
                try:
                    # Both Py2 and Py3 expect type str for object name.
                    # As Markdown works with unicode, must force str.
                    # If this very nieve conversion fails then the text
                    # could not possably be a valid Python object name.
                    line = render(str(m.group(1)))
                except Exception:
                    # Failed to get docs. Leave alone.
                    pass
            new_lines.append(line)
        return new_lines