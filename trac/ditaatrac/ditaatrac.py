"""
$Id$
$HeadURL$

"""

__revision__  = '$LastChangedRevision$'
__id__        = '$Id$'
__headurl__   = '$HeadURL$'
__docformat__ = 'restructuredtext'
__version__   = '0.7.2'



from genshi.builder import Element, tag
from genshi.core import Markup

from trac.config import BoolOption, IntOption, Option
from trac.core import *
from trac.mimeview.api import IHTMLPreviewRenderer, MIME_MAP
from trac.util import escape
from trac.util.text import to_unicode
from trac.util.translation import _
from trac.web.api import IRequestHandler
from trac.wiki.api import IWikiMacroProvider
from trac.wiki.formatter import extract_link


class Ditaa(Component):
    """
    """
    implements(IWikiMacroProvider, IHTMLPreviewRenderer, IRequestHandler)

    # Note: the following options named "..._option" are those which need
    #       some additional processing, see `_load_config()` below.

    DEFAULT_CACHE_DIR = 'gvcache'

    def __init__(self):
        self.log.info('version: %s - id: %s' % (__version__, str(__id__)))

    # IHTMLPreviewRenderer methods

    MIME_TYPES = ('application/ditaa')

    def get_quality_ratio(self, mimetype):
        self.log.error(mimetype)
        if mimetype in self.MIME_TYPES:
            return 2
        return 0

    def render(self, context, mimetype, content, filename=None, url=None):
        ext = filename.split('.')[1]
        name = ext == 'ditaa' and 'ditaa' or 'ditaa.%s' % ext
        text = hasattr(content, 'read') and content.read() or content
        return self.render_macro(context, name, text)


    # IRequestHandler methods

    def match_request(self, req):
        return req.path_info.startswith('/ditaa')

    def process_request(self, req):
        # check and load the configuration
        errmsg = self._load_config()
        if errmsg:
            return self._error_div(errmsg)

        pieces = [item for item in req.path_info.split('/ditaa') if item]

        if pieces:
            pieces = [item for item in pieces[0].split('/') if item]

            if pieces:
                name = pieces[0]
                img_path = os.path.join(self.cache_dir, name)
                return req.send_file(img_path)

    # IWikiMacroProvider methods

    def get_macros(self):
        """Return an iterable that provides the names of the provided macros."""
        return ['ditaa']

    def get_macro_description(self, name):
        """
        Return a plain text description of the macro with the
        specified name.
        """
        return inspect.getdoc(Ditaa)

    def expand_macro(self, formatter, name, content):
        """Return the HTML output of the macro."""
        req = formatter.req

        # check and load the configuration
        errmsg = self._load_config()
        if errmsg:
            return self._error_div(errmsg)

        ## Extract processor and format from name
        processor = out_format = None

        # first try with the RegExp engine
        try: 
            m = re.match('graphviz\.?([a-z]*)\/?([a-z]*)', name)
            (processor, out_format) = m.group(1, 2)

        # or use the string.split method
        except:
            (d_sp, s_sp) = (name.split('.'), name.split('/'))
            if len(d_sp) > 1:
                s_sp = d_sp[1].split('/')
                if len(s_sp) > 1:
                    out_format = s_sp[1]
                processor = s_sp[0]
            elif len(s_sp) > 1:
                out_format = s_sp[1]
            
        # assign default values, if instance ones are empty
        if not out_format:
            out_format = self.out_format
        if not processor:
            processor = self.processor

        if processor in Graphviz.Processors:
            proc_cmd = self.cmds[processor]

        else:
            self.log.error('render_macro: requested processor (%s) not found.' %
                           processor)
            return self._error_div('requested processor (%s) not found.' % 
                                  processor)
           
        if out_format not in Graphviz.Formats:
            self.log.error('render_macro: requested format (%s) not found.' %
                           out_format)
            return self._error_div(
                    tag.p(_("Graphviz macro processor error: "
                            "requested format (%(fmt)s) not valid.",
                            fmt=out_format)))

        encoded_cmd = (processor + unicode(self.processor_options)) \
                .encode(self.encoding)
        encoded_content = content.encode(self.encoding)
        sha_key  = sha.new(encoded_cmd + encoded_content).hexdigest()
        img_name = '%s.%s.%s' % (sha_key, processor, out_format)
        # cache: hash.<dot>.<png>
        img_path = os.path.join(self.cache_dir, img_name)
        map_name = '%s.%s.map' % (sha_key, processor)
        # cache: hash.<dot>.map
        map_path = os.path.join(self.cache_dir, map_name)

        # Check for URL="" presence in graph code
        URL_in_graph = 'URL=' in content

        # Create image if not in cache
        if not os.path.exists(img_path):
            self._clean_cache()

            if URL_in_graph: # translate wiki TracLinks in URL
                content = self._expand_wiki_links(formatter, out_format, 
                                                  content)
                encoded_content = content.encode(self.encoding)

            # Antialias PNGs with rsvg, if requested
            if out_format == 'png' and self.png_anti_alias == True:
                # 1. SVG output
                errmsg = self._launch(encoded_content, proc_cmd, '-Tsvg', 
                                      '-o%s.svg' % img_path,
                                      *self.processor_options)
                if errmsg:
                    return self._error_div(errmsg)

                # 2. SVG to PNG rasterization
                errmsg = self._launch(None, self.rsvg_path, 
                                      '--dpi-x=%d' % self.dpi,
                                      '--dpi-y=%d' % self.dpi,
                                      '%s.svg' % img_path, img_path)
                if errmsg:
                    return self._error_div(errmsg)
            
            else: # Render other image formats
                errmsg = self._launch(encoded_content, proc_cmd, 
                                      '-T%s' % out_format,
                                      '-o%s' % img_path, 
                                      *self.processor_options)
                if errmsg:
                    return self._error_div(errmsg)

            # Generate a map file for binary formats
            if URL_in_graph and out_format in Graphviz.Bitmap_Formats:

                # Create the map if not in cache
                if not os.path.exists(map_path):
                    errmsg = self._launch(encoded_content, proc_cmd, '-Tcmap',
                                          '-o%s' % map_path,
                                          *self.processor_options)
                    if errmsg:
                        return self._error_div(errmsg)

        # Generate HTML output
        img_url = formatter.href.graphviz(img_name)
        # for SVG(z)
        if out_format in Graphviz.Vector_Formats:
            try: # try to get SVG dimensions
                f = open(img_path, 'r')
                svg = f.readlines(1024) # don't read all
                f.close()
                svg = "".join(svg).replace('\n', '')
                w = re.search('width="([0-9]+)(.*?)" ', svg)
                h = re.search('height="([0-9]+)(.*?)"', svg)
                (w_val, w_unit) = w.group(1,2)
                (h_val, h_unit) = h.group(1,2)
                # Graphviz seems to underestimate height/width for SVG images,
                # so we have to adjust them. 
                # The correction factor seems to be constant.
                w_val, h_val = [1.35 * float(x) for x in (w_val, h_val)]
                width = unicode(w_val) + w_unit
                height = unicode(h_val) + h_unit
            except ValueError:
                width = height = '100%'

            # insert SVG, IE compatibility
            return tag.object(
                    tag.embed(src=img_url, type="image/svg+xml", 
                              width=width, height=height),
                    data=img_url, type="image/svg+xml", 
                    width=width, height=height)

        # for binary formats, add map
        elif URL_in_graph and os.path.exists(map_path):
            f = open(map_path, 'r')
            map = f.readlines()
            f.close()
            map = "".join(map).replace('\n', '')
            return tag(tag.map(Markup(map), id='G'+sha_key, name='G'+sha_key),
                       tag.img(src=img_url, usemap="#G"+sha_key, 
                               alt=_("GraphViz image")))
        else:
            return tag.img(src=img_url, alt=_("GraphViz image"))


    # Private methods

    def _expand_wiki_links(self, formatter, out_format, content):
        """Expand TracLinks that follow all URL= patterns."""
        def expand(match):
            wiki_text = match.groups()[0] # TracLink ([1], source:file/, ...)
            link = extract_link(self.env, formatter.context, wiki_text)
            if isinstance(link, Element):
                href = link.attrib.get('href')
                name = link.children
                description = link.attrib.get('title', '')
            else:
                href = wiki_text
                description = None
            if out_format == 'svg':
                format = 'URL="javascript:window.parent.location.href=\'%s\'"'
            else:
                format = 'URL="%s"'
            url = format % href
            if description:
                url += '\ntooltip="%s"' % description \
                        .replace('"', '').replace('\n', '')
            return url
        return re.sub(r'URL="(.*?)"', expand, content)

    def _load_config(self):
        """Preprocess the graphviz trac.ini configuration."""

        # if 'graphviz' not in self.config.sections():
        # ... so what? the defaults might be good enough

        # check for the cache_dir entry
        self.cache_dir = self.cache_dir_option
        if not self.cache_dir:
            return _("The [graphviz] section is missing the cache_dir field.")

        if not os.path.isabs(self.cache_dir):
            self.cache_dir = os.path.join(self.env.path, self.cache_dir)

        if not os.path.exists(self.cache_dir):
            if self.cache_dir_option == self.DEFAULT_CACHE_DIR:
                os.mkdir(self.cache_dir)
            else:
                return _("The cache_dir '%(path)s' doesn't exist, "
                         "please create it.", path=self.cache_dir)

        # Get optional configuration parameters from trac.ini.

        # check for the cmd_path entry and setup the various command paths
        cmd_paths = Graphviz.Cmd_Paths.get(sys.platform, [])

        if self.cmd_path:
            if not os.path.exists(self.cmd_path):
                return _("The '[graphviz] cmd_path' configuration entry "
                         "is set to '%(path)s' but that path does not exist.", 
                         path=self.cmd_path)
            cmd_paths = [self.cmd_path]

        if not cmd_paths:
            return _("The '[graphviz] cmd_path' configuration entry "
                     "is not set and there is no default for %(platform)s.",
                     platform=sys.platform)

        self.cmds = {}
        pname = self._find_cmd(self.processor, cmd_paths)
        if not pname:
            return _("The default processor '%(proc)s' was not found "
                     "in '%(paths)s'.", proc=self.processor, paths=cmd_paths)

        for name in Graphviz.Processors:
            pname = self._find_cmd(name, cmd_paths)

            if not pname:
                self.log.warn('The %s program was not found. '
                              'The graphviz/%s macro will be disabled.' %
                              (pname, name))
                Graphviz.Processors.remove(name)

            self.cmds[name] = pname

        if self.png_anti_alias:
            self.rsvg_path = self.rsvg_path_option or \
                    self._find_cmd('rsvg', cmd_paths)
            
            if not os.path.exists(self.rsvg_path):
                return _("The rsvg program is set to '%(path)s' but that path "
                         "does not exist.", path=self.rsvg_path)

        # get default graph/node/edge attributes
        self.processor_options = []
        defaults = [opt for opt in self.config.options('graphviz') 
                    if opt[0].startswith('default_')]
        for name, value in defaults:
            for prefix, optkey in [
                    ('default_graph_', '-G'), 
                    ('default_node_', '-N'),
                    ('default_edge_', '-E')]:
                if name.startswith(prefix):
                    self.processor_options.append("%s%s=%s" % 
                            (optkey, name.replace(prefix,''), value))

        # setup mimetypes to support the IHTMLPreviewRenderer interface
        if 'graphviz' not in MIME_MAP:
            MIME_MAP['graphviz'] = 'application/graphviz'
        for processor in Graphviz.Processors:
            if processor not in MIME_MAP:
                MIME_MAP[processor] = 'application/graphviz'

    def _launch(self, encoded_input, *args):
        """Launch a process (cmd), and returns exitcode, stdout + stderr"""
        # Note: subprocess.Popen doesn't support unicode options arguments
        # (http://bugs.python.org/issue1759845) so we have to encode them.
        # Anyway, dot expects utf-8 or the encoding specified with -Gcharset.
        encoded_cmd = []
        for arg in args:
            if isinstance(arg, unicode):
                arg = arg.encode(self.encoding, 'replace')
            encoded_cmd.append(arg)
        p = subprocess.Popen(encoded_cmd, stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if input:
            p.stdin.write(encoded_input)
        p.stdin.close()
        out = p.stdout.read()
        err = p.stderr.read()
        reason = None
        if p.wait() != 0:
            reason = _("failed with the following output:")
        if err or out:
            reason = _("succeeded but emitted the following output:")
        if reason:
            return tag.p(tag.br(), _("The command:"), 
                         tag.pre(repr(' '.join(encoded_cmd))), reason, 
                         out and tag.pre(repr(out)), err and tag.pre(repr(err)))

    def _error_div(self, msg):
        """Display msg in an error box, using Trac style."""
        if isinstance(msg, str):
            msg = to_unicode(msg)
        self.log.error(msg)
        if isinstance(msg, unicode):
            msg = tag.pre(escape(msg))
        return tag.div(
                tag.strong(_("Graphviz macro processor has detected an error. "
                             "Please fix the problem before continuing.")),
                msg, class_="system-message")

    def _clean_cache(self):
        """
        The cache manager (clean_cache) is an attempt at keeping the
        cache directory under control. When the cache manager
        determines that it should clean up the cache, it will delete
        files based on the file access time. The files that were least
        accessed will be deleted first.

        The graphviz section of the trac configuration file should
        have an entry called cache_manager to enable the cache
        cleaning code. If it does, then the cache_max_size,
        cache_min_size, cache_max_count and cache_min_count entries
        must also be there.
        """

        if self.cache_manager:

            # os.stat gives back a tuple with: st_mode(0), st_ino(1),
            # st_dev(2), st_nlink(3), st_uid(4), st_gid(5),
            # st_size(6), st_atime(7), st_mtime(8), st_ctime(9)

            entry_list = {}
            atime_list = {}
            size_list = {}
            count = 0
            size = 0

            for name in os.listdir(self.cache_dir):
                #self.log.debug('clean_cache.entry: %s' % name)
                entry_list[name] = os.stat(os.path.join(self.cache_dir, name))

                atime_list.setdefault(entry_list[name][7], []).append(name)
                count = count + 1

                size_list.setdefault(entry_list[name][6], []).append(name)
                size = size + entry_list[name][6]

            atime_keys = atime_list.keys()
            atime_keys.sort()

            #self.log.debug('clean_cache.atime_keys: %s' % atime_keys)
            #self.log.debug('clean_cache.count: %d' % count)
            #self.log.debug('clean_cache.size: %d' % size)
        
            # In the spirit of keeping the code fairly simple, the
            # clearing out of files from the cache directory may
            # result in the count dropping below cache_min_count if
            # multiple entries are have the same last access
            # time. Same for cache_min_size.
            if count > self.cache_max_count or size > self.cache_max_size:
                while atime_keys and (self.cache_min_count < count or  
                                      self.cache_min_size < size):
                    key = atime_keys.pop(0)
                    for file in atime_list[key]:
                        os.unlink(os.path.join(self.cache_dir, file))
                        count = count - 1
                        size = size - entry_list[file][6]

    def _find_cmd(self, cmd, paths):
        exe_suffix = ''
        if sys.platform == 'win32':
            exe_suffix = '.exe'

        pname = None
        for path in paths:
            p = os.path.join(path, cmd) + exe_suffix
            if os.path.exists(p):
                pname = p
                break

        return pname
