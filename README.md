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

*   The format and syntax of the DocTag is not set in stone at this point. I'm not
    sure I even like it. I was inclined to go with curly brackets (`{}`), but I know
    that a number of poeple run their Markdown through Django or Jinga template
    systems and this would conflict with that. And angled brackets (`<>`) are easily
    confused with raw HTML, which could trip up browsers when using nonsupporting 
    Markdown parsers. The square brackets (`[]`) feel a little overloaded in Markdown 
    as it is, but is seemed to make sense at the time. Besides, they should go through
    nonsupporting Markdown parsers unaffected in the current format and won't confuse
    browers in their raw state in an HTML document.

    I went with percent signs (`[% ... %]`) which is reminisant of Django/Jinga's
    block tags (`{% ... %}`). I could have went with double square brackets 
    (`[[ ... ]]`), but that is already used by the WikiLinks Extension, and is more
    akin to Django/Jinga's tags (`{{ ... }}`), which are not block level. I wanted to 
    convey that this can only be used at the block level and I thought that perhaps
    a similar syntax would help.

*   No consideration for theming has been given. The markup produced may need to be
    adjusted to better accommodate such considerations.

    There are a few possible ways to address that. Currently, the title is wrapped in
    a header tag (`<h1-6`>) and the body is just copied verbatim after the header.
    As a preprocessor is used, the Markdown text is simply inserted into the source
    document and then the entire document (with the newly inserted parts) is parsed and
    converted to HTML. We could take a few different approaches instead:
    
    1. A templating system could be used allowing the user to more easily adapt the
       output to their specific theming needs. However, this would require that
       already converted HTML would need to be inserted into the document; probably
       by a postprocessor. In this scenario, the regex would look for
       `<p>[% object.name %]</p>` and swap that out.
    
    2. A second alternative would be to use a blockprocessor and custom build the
       HTML using `etree` right in the code. The Markdown doc strings could be parsed
       recursively and inserted as children in the tree. While this gives total 
       control and feels more in line with the spirit of the Markdown Extension API,
       it becomes difficult/impossible for users to customize the resulting markup.
    
    Both of the above paths would allow for the inserted excerpts to be wrapped in
    some way (possibly by a `<div>` or `<section>`). As the output includes headers
    which may not fit into the hierarchy of the rest of the page, this probably makes
    the most sense. In HTML5, each `<section>` can have its own header hierarchy and
    start over at `<h1>`. As long as the sections are given a reasonable styling hook,
    themes can dial down the headers styling to match the hierarchy of the entire page, 
    etc.
    
    Either way, my inclination is to look at Sphinx's markup and possibly copy it so
    that Sphinx CSS could be used out-of-the-box for styling purposes. That said,
    the Markdown parts of the doc strings may not translate so well as we don't have
    Rest's directives to identify various pieces of the doc string. That being the 
    case, it might make more sense to take this in its own direction. If we copy
    an existing scheme, I'm inclined to go with (2) above and hardcode the output.
    But if we do our own thing, I think (1) makes more sense to give users the 
    flexability to change the output to fit their needs.

*   Or we could completely ignore the previous point and simpley improve the existing
    method. A few things would need to happen:

    * The markup inserted by the preprocessor needs to be broken up and integrated 
    into the list of lines so the rest of the preprocessors can operate on it properly.
    
    * The Markdown pulled from the doc strings needs to have whitespace normalization.
    
    * An option could be added to the DocTag to allow the document author to define the
    lowest level header so the output fits into the document's hierarchy. Not sure
    what this would look like. Not sure I like `[% object.name 3 %]`. Maybe 
    `[% object.name|level:3 %]` or `[% object.name level=3 %]` or 
    `[% object=object.name, level=3 %]`... Uhg.

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
