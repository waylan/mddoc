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

Roadmap
-------

In its current status, this project is more of an experimental proof-of-concept than 
something I would use in a production environment. While I don't have a concrete
roadmap in mind, there are a few possible ways it could go. Here are my thoughts 
on potential future development:

*   Tests: Obviously, tests need to be created before any further development is done.
    I expect this includes creating some sort of mock modules/classes/functions with
    doc strings that the tests can be run against.

    As an aside, the existing implementation simply subclasses pydoc, removes some
    unneeded features and alters object nesting and object titles to fix Markdown's
    syntax. It was surprising how quickly I got it working. Although, I'm sure there 
    are multiple edge cases I didn't account for. Comprehensive tests will likely
    reveal all sorts of issues.

*   The format and syntax of the DocTag is not set in stone at this point. <del>I'm not
    sure I even like it.</del> I was inclined to go with curly brackets (`{}`), but I know
    that a number of people run their Markdown through Django or Jinga template
    systems and this would conflict with that. And angled brackets (`<>`) are easily
    confused with raw HTML, which could trip up browsers when using nonsupporting 
    Markdown parsers. The square brackets (`[]`) feel a little overloaded in Markdown 
    as it is, but is seemed to make sense at the time. Besides, they should go through
    nonsupporting Markdown parsers unaffected in the current format and won't confuse
    browsers in their raw state in an HTML document.

    I went with percent signs (`[% ... %]`) which is reminiscent of Django/Jinga's
    block tags (`{% ... %}`). I could have went with double square brackets 
    (`[[ ... ]]`), but that is already used by the WikiLinks Extension, and is more
    akin to Django/Jinga's tags (`{{ ... }}`), which are not block level. I wanted to 
    convey that this can only be used at the block level and I thought that perhaps
    a similar syntax would help.

*   No consideration for theming has been given. The markup produced may need to be
    adjusted to better accommodate such considerations.

    Currently, the title is wrapped in a header tag (`<h1-6`>) and the body is just
    copied verbatim after the header. As a preprocessor is used, the Markdown text
    is simply inserted into the source document and then the entire document (with
    the newly inserted parts) is parsed and converted to HTML. 

    Things should be simplified even more. For example, one tag would insert the
    signature of a function/class/method and a separate tag would insert the doc
    string. Perhaps something like this:
    
        # [$ object.name $]
        
        [% object.name %]

    However, for this to work, the doc tag would need to be implemented as a
    blockprocessor and the sig tag as an inline pattern. In fact they could be two
    different tags.

    Note that in this scenario, the document author has to mark up the parts of the
    document. For example, the header is explicitly defined by the document author.
    Therefore, the document author has full control and could forgo headers
    altogether. For example, she could use definition lists (and define her own attr
    list):

        [$ object.name $]{ #object.name .function }
        :   [% object.name %]
    
    Classes would only output the doc string for the doc tag. And modules would
    return a synopsis for the sig tag and the  doc string (minus the first line
    if it stands alone (the synopsis)) for the doc tag. The various parts of the
    class/module would need to be added manually -- which is a reduction in functionality
    from what exists now.
    
    Some different proposals were previously described here and have been rejected
    and not fitting in this the goals of this project. If you are interested you can
    check them out in the commit history.
    
Why?
----

While there are various tools out there to automatically generate documentation from
source code, I wanted something light-weight that could easily be incorporated into
various other tools.  Additionally, I have never been fond of tools which create an
entire website auto-magically from source code. I believe that the best documentation
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
