""" Invoke various functionality for imageio docs.
"""

import os
import sys

import imageio

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
DOC_DIR = os.path.dirname(THIS_DIR)


files_to_remove = []


def setup(app):
    init()
    app.connect('build-finished', clean)


def init():
    
    print('Special preparations for imageio docs:')
    
    for func in [prepare_reader_and_witer,
                 prepare_core_docs,
                 create_plugin_docs,
                 create_format_docs,
                 ]:
        print('  ' + func.__doc__.strip())
        func()


def clean(app, *args):
    for fname in files_to_remove:
        os.remove(os.path.join(DOC_DIR, fname))


def _write(fname, text):
    files_to_remove.append(fname)
    with open(os.path.join(DOC_DIR, fname), 'wb') as f:
        f.write(text.encode('utf-8'))


##


def prepare_reader_and_witer():
    """ Prepare Format.Reader and Format.Writer for doc generation.
    """
    
    # Create Reader and Writer subclasses that are going to be placed
    # in the format module so that autoclass can find them. They need
    # to be new classes, otherwise sphinx considers them aliases.
    class Reader(imageio.core.format.Format.Reader):
        pass
    class Writer(imageio.core.format.Format.Writer):
        pass
    imageio.core.format.Reader = Reader
    imageio.core.format.Writer = Writer
    
    # We set the docs of the original classes, and remove the docstring
    # from the original classes so that Reader and Writer do not show
    # up in the docs of the Format class.
    Reader.__doc__ = imageio.core.format.Format.Reader.__doc__
    Writer.__doc__ = imageio.core.format.Format.Writer.__doc__
    imageio.core.format.Format.Reader.__doc__ = ''
    imageio.core.format.Format.Writer.__doc__ = ''


def prepare_core_docs():
    """ Prepare imageio.core for doc generation.
    """
    # Set __all__ and add to __doc__ in imageio.core module,
    # so that the documentation gets generated correctly.
    
    D = imageio.core.__dict__
    
    # Collect functions and classes in imageio.core
    functions, classes = [], []
    for name in D:
        func_type = type(prepare_core_docs)
        if name.startswith('_'):
            continue
        ob = D[name]
        if isinstance(ob, type):
            classes.append(name)
        elif isinstance(ob, func_type):
            functions.append(name)
    
    # Write summaries
    classes.sort()
    functions.sort()
    extradocs = '\nFunctions: '
    extradocs += ', '.join([':func:`.%s`' % n for n in functions])
    extradocs += '\n\nClasses: '
    extradocs += ', '.join([':class:`.%s`' % n for n in classes])
    extradocs += '\n\n----\n'
    
    # Update
    D['__doc__'] += extradocs
    D['__all__'] = functions + classes



def create_plugin_docs():
    """ Create docs for creating plugins.
    """
    
    # Build main plugin dir
    title = "Creating imageio plugins"
    text = '%s\n%s\n\n' % (title, '=' * len(title))
    
    text += '.. automodule:: imageio.plugins\n\n'
    
    # Insert code from example plugin
    text += 'Example / template plugin\n-------------------------\n\n'
    text += ".. code-block:: python\n    :linenos:\n\n"
    filename = imageio.plugins.example.__file__
    code = open(filename, 'rb').read().decode('utf-8')
    code = '\n'.join(['    ' + line.rstrip() for line in code.splitlines()])
    text += code
    
    # Write
    _write('plugins.rst', text)


def create_format_docs():
    """ Create documentation for the formats.
    """
    
    generaltext = """.. note::
        The parameters listed below can be specifief as keyword arguments in
        the ``read()``, ``imread()``, ``mimread()`` etc. functions.
        """
    
    # Build main plugin dir
    title = "Imageio formats"
    text = '%s\n%s\n\n' % (title, '=' * len(title))
    
    text += 'This page lists all formats currently supported by imageio:'
    
    # Get bullet list of all formats
    ss = ['\n']
    covered_formats = []
    modemap = {'i': 'Single images', 'I': 'Multiple images',
               'v': 'Single volumes', 'V': 'Multiple volumes', }
    for mode in 'iIvV-':
        subtitle = modemap.get(mode, 'Unsorted')
        ss.append('%s\n%s\n' % (subtitle, '^' * len(subtitle)))
        for format in imageio.formats: 
            if ((mode in format.modes) or 
                (mode == '-' and format not in covered_formats)):
                covered_formats.append(format)
                s = '  * :ref:`%s <%s>` - %s' % (format.name, 
                                                 format.name, 
                                                 format.description)
                ss.append(s)
    text += '\n'.join(ss) + '\n\n'
    _write('formats.rst', text)
    
    
    # Get more docs for each format
    for format in imageio.formats:
        
        title = '%s %s' % (format.name, format.description)
        ext = ', '.join(['``%s``' % e for e in format.extensions])
        ext = ext or 'None'
        #
        text = ':orphan:\n\n'
        text += '.. _%s:\n\n' % format.name
        text += '%s\n%s\n\n' % (title, '='*len(title))
        #
        text += generaltext + '\n\n'
        text += 'Extensions: %s\n\n' % ext
        docs = '    ' + format.__doc__.lstrip()
        docs = '\n'.join([x[4:].rstrip() for x in docs.splitlines()])
        #
        text += docs + '\n\n'
        
        #members = '\n  :members:\n\n'
        #text += '.. autoclass:: %s.Reader%s' % (format.__module__, members)
        #text += '.. autoclass:: %s.Writer%s' % (format.__module__, members)
        
        _write('format_%s.rst' % format.name.lower(), text)
