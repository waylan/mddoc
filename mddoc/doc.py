# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import pydoc
import inspect
import pkgutil
from pprint import pformat


class MdDoc(pydoc.TextDoc):
    """ Formater class for Markdown documentation. """
    def __init__(self, hlevel):
        self.hlevel = hlevel
        #super(MdDoc, self).__init__()
    
    def header(self, text, level, id, cls):
        """ Format a Markdown header. """
        return '#'*level + ' %s { #%s .%s }\n\n' % (text.rstrip(), id, cls)
    
    def code(self, text):
        """ Format markdown inline code. """
        return '`%s`' % text

    def section(self, title, contents):
        """Format a section with a given heading."""
        return self.header(title, self.hlevel-1, title, 'section') + contents.rstrip() + '\n\n'

    def docmodule(self, object, name=None, mod=None):
        """Produce Markdown documentation for a given module object."""
        try:
            all = object.__all__
        except AttributeError:
            all = None

        name = object.__name__ # ignore the passed-in name
        synop, desc = pydoc.splitdoc(pydoc.getdoc(object))
        synop = synop if synop else name
        result = self.header(synop, self.hlevel, name, 'module')
        
        if desc:
            result = result + desc.rstrip() + '\n\n'

        docloc = self.getdocloc(object)
        if docloc is not None:
            result = result + 'Module Documentation: <%s>\n\n' % docloc

        classes = []
        for key, value in inspect.getmembers(object, inspect.isclass):
            # if __all__ exists, believe it.  Otherwise use old heuristic.
            if (all is not None
                or (inspect.getmodule(value) or object) is object):
                if pydoc.visiblename(key, all, object):
                    classes.append((key, value))
        funcs = []
        for key, value in inspect.getmembers(object, inspect.isroutine):
            # if __all__ exists, believe it.  Otherwise use old heuristic.
            if (all is not None or
                inspect.isbuiltin(value) or inspect.getmodule(value) is object):
                if pydoc.visiblename(key, all, object):
                    funcs.append((key, value))
        data = []
        for key, value in inspect.getmembers(object, pydoc.isdata):
            if pydoc.visiblename(key, all, object):
                data.append((key, value))

        self.hlevel += 2

        #modpkgs = []
        #modpkgs_names = set()
        #if hasattr(object, '__path__'):
        #    for importer, modname, ispkg in pkgutil.iter_modules(object.__path__):
        #        modpkgs_names.add(modname)
        #        if ispkg:
        #            modpkgs.append(modname + ' (package)')
        #        else:
        #            modpkgs.append(modname)
        #
        #    modpkgs.sort()
        #    result = result + self.section(
        #        'PACKAGE CONTENTS', '\n'.join(modpkgs))
        #
        ## Detect submodules as sometimes created by C extensions
        #submodules = []
        #for key, value in inspect.getmembers(object, inspect.ismodule):
        #    if value.__name__.startswith(name + '.') and key not in modpkgs_names:
        #        submodules.append(key)
        #if submodules:
        #    submodules.sort()
        #    result = result + self.section(
        #        'SUBMODULES', '\n'.join(submodules))

        if classes:
            classlist = map(lambda key_value: key_value[1], classes)
            contents = [self.formattree(
                inspect.getclasstree(classlist, 1), name)]
            for key, value in classes:
                contents.append(self.document(value, key, name))
            result = result + self.section('CLASSES', '\n'.join(contents))

        if funcs:
            contents = []
            for key, value in funcs:
                contents.append(self.document(value, key, name))
            result = result + self.section('FUNCTIONS', '\n'.join(contents))

        if data:
            contents = []
            for key, value in data:
                contents.append(self.docother(value, key, name, maxlen=70))
            result = result + self.section('DATA', '\n'.join(contents))

        if hasattr(object, '__version__') and not inspect.ismodule(object.__version__):
            version = object.__version__
            if version[:11] == '$' + 'Revision: ' and version[-1:] == '$':
                version = version[11:-1].strip()
            result = result + self.section('VERSION', version)
        if hasattr(object, '__date__'):
            result = result + self.section('DATE', object.__date__)
        if hasattr(object, '__author__'):
            result = result + self.section('AUTHOR', object.__author__)
        if hasattr(object, '__credits__'):
            result = result + self.section('CREDITS', object.__credits__)
        
        self.hlevel -= 2
        return result

    def docclass(self, object, name=None, mod=None, *ignored):
        """Produce Markdown documentation for a given class object."""
        realname = object.__name__
        name = name or realname
        bases = object.__bases__

        def makename(c, m=object.__module__):
            return pydoc.classname(c, m)

        if name == realname:
            title = 'class ' + realname
        else:
            title = name + ' = class ' + realname
        if bases:
            parents = map(makename, bases)
            title = title + '(%s)' % ', '.join(parents)
        title = self.header(title, self.hlevel, name, 'class')
        
        self.hlevel += 1

        doc = pydoc.getdoc(object)
        contents = doc and [doc + '\n'] or []
        push = contents.append

        # List the mro, if non-trivial.
        mro = pydoc.deque(inspect.getmro(object))
        if len(mro) > 2:
            push("Method resolution order:\n")
            for base in mro:
                push('* ' + makename(base))
            push('')

        # Cute little class to pump out a horizontal rule between sections.
        class HorizontalRule:
            def __init__(self):
                self.needone = 0
            def maybe(self):
                if self.needone:
                    push('-' * 70 + '\n')
                self.needone = 1
        hr = HorizontalRule()

        def spill(msg, attrs, predicate):
            ok, attrs = pydoc._split_list(attrs, predicate)
            if ok:
                hr.maybe()
                push(msg)
                for name, kind, homecls, value in ok:
                    try:
                        value = getattr(object, name)
                    except Exception:
                        # Some descriptors may meet a failure in their __get__.
                        # (bug #1785)
                        push(self._docdescriptor(name, value, mod))
                    else:
                        push(self.document(value,
                                        name, mod, object))
            return attrs

        def spilldescriptors(msg, attrs, predicate):
            ok, attrs = pydoc._split_list(attrs, predicate)
            if ok:
                hr.maybe()
                push(msg)
                for name, kind, homecls, value in ok:
                    push(self._docdescriptor(name, value, mod))
            return attrs

        def spilldata(msg, attrs, predicate):
            ok, attrs = pydoc._split_list(attrs, predicate)
            if ok:
                hr.maybe()
                push(msg)
                for name, kind, homecls, value in ok:
                    if (hasattr(value, '__call__') or
                            inspect.isdatadescriptor(value)):
                        doc = pydoc.getdoc(value)
                    else:
                        doc = None
                    push(self.docother(getattr(object, name),
                                       name, mod, maxlen=70, doc=doc) + '\n')
            return attrs

        attrs = filter(lambda data: pydoc.visiblename(data[0], obj=object),
                       pydoc.classify_class_attrs(object))
        while attrs:
            if mro:
                thisclass = mro.popleft()
            else:
                thisclass = attrs[0][2]
            attrs, inherited = pydoc._split_list(attrs, lambda t: t[2] is thisclass)

            if thisclass is pydoc.__builtin__.object:
                attrs = inherited
                continue
            elif thisclass is object:
                tag = "defined here"
            else:
                tag = "inherited from %s" % pydoc.classname(thisclass,
                                                      object.__module__)

            # Sort attrs by name.
            attrs.sort()

            # Pump out the attrs, segregated by kind.
            attrs = spill("Methods %s:\n" % tag, attrs,
                          lambda t: t[1] == 'method')
            attrs = spill("Class methods %s:\n" % tag, attrs,
                          lambda t: t[1] == 'class method')
            attrs = spill("Static methods %s:\n" % tag, attrs,
                          lambda t: t[1] == 'static method')
            attrs = spilldescriptors("Data descriptors %s:\n" % tag, attrs,
                                     lambda t: t[1] == 'data descriptor')
            attrs = spilldata("Data and other attributes %s:\n" % tag, attrs,
                              lambda t: t[1] == 'data')
            assert attrs == []
            attrs = inherited

        self.hlevel -= 1

        contents = '\n'.join(contents)
        if not contents:
            return title
        return title + contents.rstrip() + '\n'

    def docroutine(self, object, name=None, mod=None, cl=None):
        """Produce text documentation for a function or method object."""
        realname = object.__name__
        name = name or realname
        note = ''
        skipdocs = 0
        if inspect.ismethod(object):
            imclass = object.im_class
            if cl:
                if imclass is not cl:
                    note = ' from ' + pydoc.classname(imclass, mod)
            else:
                if object.im_self is not None:
                    note = ' method of %s instance' % pydoc.classname(
                        object.im_self.__class__, mod)
                else:
                    note = ' unbound %s method' % pydoc.classname(imclass,mod)
            object = object.im_func

        if name == realname:
            title = realname
        else:
            if (cl and realname in cl.__dict__ and
                cl.__dict__[realname] is object):
                skipdocs = 1
            title = name + ' = ' + realname
        if inspect.isfunction(object):
            args, varargs, varkw, defaults = inspect.getargspec(object)
            argspec = inspect.formatargspec(
                args, varargs, varkw, defaults, formatvalue=self.formatvalue)
            if realname == '<lambda>':
                title = name + ' lambda '
                argspec = argspec[1:-1] # remove parentheses
        else:
            argspec = '(...)'
        id = name if not cl else '.'.join((cl.__name__, name))
        decl = self.header(self.code(title + argspec + note), self.hlevel, id, 'routine')

        if skipdocs:
            return decl
        else:
            doc = pydoc.getdoc(object) or ''
            return decl + (doc and pydoc.rstrip(doc) + '\n')
    
    def _docdescriptor(self, name, value, mod):
        results = []
        push = results.append

        if name:
            push(self.header(self.code(name), self.hlevel, name, 'descriptor'))
        doc = pydoc.getdoc(value) or ''
        if doc:
            push(doc)
            push('\n')
        return ''.join(results)
    
    def docother(self, object, name=None, mod=None, parent=None, maxlen=None, doc=None):
        """Produce text documentation for a data object."""
        repr = self.repr(object)
        line = (name and name + ' = ' or '') + repr
        if maxlen and len(line) > maxlen:
            # TODO: Make pformat use self.repr ??
            line = self.indent((name and name + ' = \n' or '') + self.indent(pformat(object)))
        else:
            line = self.indent(line)
        
        if doc is not None:
            line += '\n\n' + doc
        return line
    

def render(thing, hlevel=1, forceload=0):
    """ Render Markdown documentation, given an object or a path to an object. """
    object, name = pydoc.resolve(thing, forceload)
    if type(object) is pydoc._OLD_INSTANCE_TYPE:
        # If the passed object is an instance of an old-style class,
        # document its available methods instead of its value.
        object = object.__class__
    elif not (inspect.ismodule(object) or
              inspect.isclass(object) or
              inspect.isroutine(object) or
              inspect.isgetsetdescriptor(object) or
              inspect.ismemberdescriptor(object) or
              isinstance(object, property)):
        # If the passed object is a piece of data or an instance,
        # document its available methods instead of its value.
        object = type(object)
    mddoc = MdDoc(hlevel=hlevel)
    return mddoc.document(object, name)
