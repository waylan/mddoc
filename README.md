Markdown API Documenter
=======================

A [Python-Markdown] Extension to Generate API Documentation from Python
Objects in Markdown documents.

***WARNING!*** This is an experimental project with alpha code and is
likely to have numerous bugs and untested edge cases. Please feel free to
report bugs (or even better, provide patches) and help make it better.

Syntax
------

To include documentation from a specific Python object, include a DocTag
in the Markdown text on a line by itself. For example:

    [% object.name %]

The DotTag must be at the start of a line by itself.  This means that it
cannot be nested inside lists or blockquotes. Ideally, it would be surrounded
by a blank line before and after it.

Note that the object name used must be the full import path of the object
using Python dot notation. The object may be a module, class, function or
other such object.

When the document is rendered as HTML, the DocTag will be replaced with
the documentation pulled from the source code for that object. It is expected
that any comments used are formatted as Markdown text, which will be rendered
as HTML in the document.

Each object will begin with a header (`<h1>`) that has an id assigned consisting
of the object name and a class indicating which type of object it is. For
example, the following DocTag:

    [% markdown.markdown %]
    
returns the following HTML:

    <h1 class="routine" id="markdown.markdown"><code>markdown.markdown = markdown(text, *args, **kwargs)</code></h1>
    <p>Convert a markdown string to HTML and return HTML as a unicode string.</p>
    <p>This is a shortcut function for <code>Markdown</code> class to cover the most
    basic use case.  It initializes an instance of Markdown, loads the
    necessary extensions and runs the parser on the given text.</p>
    <p>Keyword arguments:</p>
    <ul>
    <li>text: Markdown formatted text as Unicode or ASCII string.</li>
    <li>Any arguments accepted by the Markdown class.</li>
    </ul>
    <p>Returns: An HTML document as a string.</p>

which was generated from the following source code:

    def markdown(text, *args, **kwargs):
        """
        Convert a markdown string to HTML and return HTML as a unicode string.
        This is a shortcut function for `Markdown` class to cover the most
        basic use case.  It initializes an instance of Markdown, loads the
        necessary extensions and runs the parser on the given text.
        
        Keyword arguments:
        
        * text: Markdown formatted text as Unicode or ASCII string.
        * Any arguments accepted by the Markdown class.
        
        Returns: An HTML document as a string.
        
        """

Installation
------------

From the command line run the following command:

    $ pip install git+https://github.com/waylan/mddoc.git#egg=mddoc

Usage
-----

As this extension depends on the [attr_list] Extension (which ships with
Python-Markdown), both must be enabled. From the Python Interpreter do the
following:

    >>> import markdown
    >>> html = markdown.markdown(text, extensions=['mddoc', 'markdown.extensions.attr_list'])

Or, from the command line:

    $ python -m markdown -x mddoc -x markdown.extensions.attr_list input.txt > output.html

Why?
----

While there are various tools out there to automatically generate documentation from
source code, I wanted something light-weight that could easily be incorporated into
various other tools.  Additionally, I have never been fond of tools which create an
entire website automagically from source code. I believe that the best documentation
is hand-crafted prose. However, when the same documentation is duplicated in the
source code and in the documentation for a project, they can diverge over time.
And it is not very DRY to have to edit the documentation in two locations.

Therefore, it can be helpful to pull the API docs into the prose for the best of
both worlds. This extension is intended to meet that need. In fact, I may remove
support for pulling in an entire module as that feels like it may be going
a little to far. As this project is in an experimental stage, it will remain for
the time being.

Happy documenting!

[Python-Markdown]: https://pythonhosted.org/Markdown/
[attr_list]: https://pythonhosted.org/Markdown/extensions/attr_list.html
