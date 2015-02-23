# -*- coding: utf-8 -*-
'''
Markdown API Documenter

Generate API Documentation from Python Objects in Markdown documents.

This extension expects the "attr_list" extension to be used as well.

'''

from .ext import DocExtension

__all__ = ['MdDocExtension']
__version__ = '0.1.0'

def makeExtension(*args, **kwargs):
    return DocExtension(*args, **kwargs)