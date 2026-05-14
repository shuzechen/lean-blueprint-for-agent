"""
Package Lean blueprint

This depends on the depgraph plugin. This plugin has to be installed but then it is
used automatically.

Options:
* project: lean project path

* showmore: enable buttons showing or hiding proofs (this requires the showmore plugin).

You can also add options that will be passed to the dependency graph package.
"""
import json
import string
from pathlib import Path

from jinja2 import Template
from plasTeX import Command
from plasTeX.Logging import getLogger
from plasTeX.PackageResource import PackageCss, PackageTemplateDir
from plastexdepgraph.Packages.depgraph import item_kind

log = getLogger()

PKG_DIR = Path(__file__).parent
STATIC_DIR = Path(__file__).parent.parent/'static'


class home(Command):
    r"""\home{url}"""
    args = 'url:url'

    def invoke(self, tex):
        Command.invoke(self, tex)
        self.ownerDocument.userdata['project_home'] = self.attributes['url']
        return []


class github(Command):
    r"""\github{url}"""
    args = 'url:url'

    def invoke(self, tex):
        Command.invoke(self, tex)
        self.ownerDocument.userdata['project_github'] = self.attributes['url'].textContent.rstrip(
            '/')
        return []


class dochome(Command):
    r"""\dochome{url}"""
    args = 'url:url'

    def invoke(self, tex):
        Command.invoke(self, tex)
        self.ownerDocument.userdata['project_dochome'] = self.attributes['url'].textContent
        return []


class graphcolor(Command):
    r"""\graphcolor{node_type}{color}{color_descr}"""
    args = 'node_type:str color:str color_descr:str'

    def digest(self, tokens):
        Command.digest(self, tokens)
        attrs = self.attributes
        colors = self.ownerDocument.userdata['dep_graph']['colors']
        node_type = attrs['node_type']
        if node_type not in colors:
            log.warning(f'Unknown node type {node_type}')
        colors[node_type] = (attrs['color'].strip(), attrs['color_descr'].strip())


class leanok(Command):
    r"""\leanok"""

    def digest(self, tokens):
        Command.digest(self, tokens)
        self.parentNode.userdata['leanok'] = True


class notready(Command):
    r"""\notready"""

    def digest(self, tokens):
        Command.digest(self, tokens)
        self.parentNode.userdata['notready'] = True


class mathlibok(Command):
    r"""\mathlibok"""

    def digest(self, tokens):
        Command.digest(self, tokens)
        self.parentNode.userdata['leanok'] = True
        self.parentNode.userdata['mathlibok'] = True


class lean(Command):
    r"""\lean{decl list} """
    args = 'decls:list:nox'

    def digest(self, tokens):
        Command.digest(self, tokens)
        decls = [dec.strip() for dec in self.attributes['decls']]
        self.parentNode.setUserData('leandecls', decls)
        all_decls = self.ownerDocument.userdata.setdefault('lean_decls', [])
        all_decls.extend(decls)


class discussion(Command):
    r"""\discussion{issue_number} """
    args = 'issue:str'

    def digest(self, tokens):
        Command.digest(self, tokens)
        self.parentNode.setUserData(
            'issue', self.attributes['issue'].lstrip('#').strip())


CHECKMARK_TPL = Template("""
    {% if obj.userdata.leanok and ('proved_by' not in obj.userdata or obj.userdata.proved_by.userdata.leanok ) %}
    ✓
    {% endif %}
""")

LEAN_DECLS_TPL = Template("""
    {% if obj.userdata.leandecls %}
    <button class="modal lean">L∃∀N</button>
    {% call modal('Lean source') %}
        {% for name, imports, body in obj.userdata.lean_sources %}
        <div class="lean_source_block">
          <div class="lean_source_name">{{ name | e }}</div>
          <pre class="lean_source"><code>{% if imports %}{% for imp in imports %}import {{ imp | e }}
{% endfor %}
{% endif %}{{ body | e }}</code></pre>
        </div>
        {% endfor %}
        {% for name in obj.userdata.lean_sources_missing %}
        <div class="lean_source_block">
          <div class="lean_source_name">{{ name | e }}</div>
          <p class="lean_source_missing">(no source supplied)</p>
        </div>
        {% endfor %}
    {% endcall %}
    {% endif %}
""")

GITHUB_ISSUE_TPL = Template("""
    {% if obj.userdata.issue %}
    <a class="github_link" href="{{ obj.ownerDocument.userdata.project_github }}/issues/{{ obj.userdata.issue }}">Discussion</a>
    {% endif %}
""")

LEAN_LINKS_TPL = Template("""
  {% if thm.userdata['leandecls'] -%}
  <button class="modal lean lean_link">Lean</button>
  <div class="modal-container">
    <div class="modal-content">
      <header>
        <h1>Lean source</h1>
        <button class="closebtn">&times;</button>
      </header>
      {% for name, imports, body in thm.userdata.lean_sources %}
      <div class="lean_source_block">
        <div class="lean_source_name">{{ name | e }}</div>
        <pre class="lean_source"><code>{% if imports %}{% for imp in imports %}import {{ imp | e }}
{% endfor %}
{% endif %}{{ body | e }}</code></pre>
      </div>
      {% endfor %}
      {% for name in thm.userdata.lean_sources_missing %}
      <div class="lean_source_block">
        <div class="lean_source_name">{{ name | e }}</div>
        <p class="lean_source_missing">(no source supplied)</p>
      </div>
      {% endfor %}
    </div>
  </div>
  {%- endif -%}
""")

GITHUB_LINK_TPL = Template("""
  {% if thm.userdata['issue'] -%}
  <a class="issue_link" href="{{ document.userdata['project_github'] }}/issues/{{ thm.userdata['issue'] }}">Discussion</a>
  {%- endif -%}
""")


def ProcessOptions(options, document):
    """This is called when the package is loaded."""

    # We want to ensure the depgraph and showmore packages are loaded.
    # We first need to make sure the corresponding plugins are used.
    # This is a bit hacky but needed for backward compatibility with
    # project who used the blueprint package before the depgraph one was
    # split.
    plugins = document.config['general'].data['plugins'].value
    if 'plastexdepgraph' not in plugins:
        plugins.append('plastexdepgraph')
    # And now load the package.
    document.context.loadPythonPackage(document, 'depgraph', options)
    if 'showmore' in options:
        if 'plastexshowmore' not in plugins:
            plugins.append('plastexshowmore')
        # And now load the package.
        document.context.loadPythonPackage(document, 'showmore', {})

    templatedir = PackageTemplateDir(path=PKG_DIR/'renderer_templates')
    document.addPackageResource(templatedir)

    jobname = document.userdata['jobname']
    outdir = document.config['files']['directory']
    outdir = string.Template(outdir).substitute({'jobname': jobname})

    def make_lean_data() -> None:
        """
        Populate per-node formalization status and embed Lean source from the
        blueprint/lean_sources.json sidecar (written by the agent / MCP).

        Also create the file lean_decls of all Lean names referred to in the
        blueprint (legacy artifact; harmless if unused).
        """

        # Load the optional sidecar that maps name -> {imports, body}.
        # The sidecar lives next to lean_decls, in blueprint/.
        sources_path = Path(document.userdata['working-dir']).parent/"lean_sources.json"
        if sources_path.exists():
            try:
                sources_map = json.loads(sources_path.read_text(encoding='utf-8'))
            except (OSError, ValueError) as e:
                log.warning(f'Could not read {sources_path}: {e}')
                sources_map = {}
        else:
            sources_map = {}

        def _entry_for(name: str):
            entry = sources_map.get(name)
            if not isinstance(entry, dict):
                return None
            imports = entry.get('imports') or []
            if not isinstance(imports, list):
                imports = []
            body = entry.get('body') or entry.get('source') or ''
            return [str(imp) for imp in imports], str(body)

        for graph in document.userdata['dep_graph']['graphs'].values():
            nodes = graph.nodes
            for node in nodes:
                leandecls = node.userdata.get('leandecls', [])
                lean_sources = []
                lean_sources_missing = []
                for leandecl in leandecls:
                    found = _entry_for(leandecl)
                    if found is None:
                        lean_sources_missing.append(leandecl)
                    else:
                        imports, body = found
                        lean_sources.append((leandecl, imports, body))

                node.userdata['lean_sources'] = lean_sources
                node.userdata['lean_sources_missing'] = lean_sources_missing
                # Keep lean_urls as empty list for back-compat with any template
                # still referencing it; doc-gen URLs are no longer constructed.
                node.userdata['lean_urls'] = []

                used = node.userdata.get('uses', [])
                node.userdata['can_state'] = all(thm.userdata.get('leanok')
                                                 for thm in used) and not node.userdata.get('notready', False)
                proof = node.userdata.get('proved_by')
                if proof:
                    used.extend(proof.userdata.get('uses', []))
                    node.userdata['can_prove'] = all(thm.userdata.get('leanok')
                                                     for thm in used)
                    node.userdata['proved'] = proof.userdata.get(
                        'leanok', False)
                else:
                    node.userdata['can_prove'] = False
                    node.userdata['proved'] = False

            for node in nodes:
                node.userdata['fully_proved'] = all(n.userdata.get('proved', False) or item_kind(
                    n) == 'definition' for n in graph.ancestors(node).union({node}))

        lean_decls_path = Path(document.userdata['working-dir']).parent/"lean_decls"
        lean_decls_path.write_text("\n".join(document.userdata.get("lean_decls", [])))

    document.addPostParseCallbacks(150, make_lean_data)

    document.addPackageResource([PackageCss(path=STATIC_DIR/'blueprint.css')])

    colors = document.userdata['dep_graph']['colors'] = {
        'mathlib': ('darkgreen', 'Dark green'),
        'stated': ('green', 'Green'),
        'can_state': ('blue', 'Blue'),
        'not_ready': ('#FFAA33', 'Orange'),
        'proved': ('#9CEC8B', 'Green'),
        'can_prove': ('#A3D6FF', 'Blue'),
        'defined': ('#B0ECA3', 'Light green'),
        'fully_proved': ('#1CAC78', 'Dark green')
    }

    def colorizer(node) -> str:
        data = node.userdata

        color = ''
        if data.get('mathlibok'):
            color = colors['mathlib'][0]
        elif data.get('leanok'):
            color = colors['stated'][0]
        elif data.get('can_state'):
            color = colors['can_state'][0]
        elif data.get('notready'):
            color = colors['not_ready'][0]
        return color

    def fillcolorizer(node) -> str:
        data = node.userdata
        stated = data.get('leanok')
        can_state = data.get('can_state')
        can_prove = data.get('can_prove')
        proved = data.get('proved')
        fully_proved = data.get('fully_proved')

        fillcolor = ''
        if proved:
            fillcolor = colors['proved'][0]
        elif can_prove and (can_state or stated):
            fillcolor = colors['can_prove'][0]
        if item_kind(node) == 'definition':
            if stated:
                fillcolor = colors['defined'][0]
            elif can_state:
                fillcolor = colors['can_prove'][0]
        elif fully_proved:
            fillcolor = colors['fully_proved'][0]
        return fillcolor

    document.userdata['dep_graph']['colorizer'] = colorizer
    document.userdata['dep_graph']['fillcolorizer'] = fillcolorizer

    def make_legend() -> None:
        """
        Extend the dependency graph legend defined by the depgraph plugin
        by adding information specific to Lean blueprints. This is registered
        as a post-parse callback to allow users to redefine colors and their 
        descriptions.
        """
        document.userdata['dep_graph']['legend'].extend([
            (f"{document.userdata['dep_graph']['colors']['can_state'][1]} border",
             "the <em>statement</em> of this result is ready to be formalized; all prerequisites are done"),
            (f"{document.userdata['dep_graph']['colors']['not_ready'][1]} border",
                "the <em>statement</em> of this result is not ready to be formalized; the blueprint needs more work"),
            (f"{document.userdata['dep_graph']['colors']['can_state'][1]} background",
                "the <em>proof</em> of this result is ready to be formalized; all prerequisites are done"),
            (f"{document.userdata['dep_graph']['colors']['proved'][1]} border",
                "the <em>statement</em> of this result is formalized"),
            (f"{document.userdata['dep_graph']['colors']['proved'][1]} background",
                "the <em>proof</em> of this result is formalized"),
            (f"{document.userdata['dep_graph']['colors']['fully_proved'][1]} background", 
                "the <em>proof</em> of this result and all its ancestors are formalized"),
            (f"{document.userdata['dep_graph']['colors']['mathlib'][1]} border",
                "this is in Mathlib"),
        ])

    document.addPostParseCallbacks(150, make_legend)

    document.userdata.setdefault(
        'thm_header_extras_tpl', []).extend([CHECKMARK_TPL])
    document.userdata.setdefault('thm_header_hidden_extras_tpl', []).extend([LEAN_DECLS_TPL,
                                                                             GITHUB_ISSUE_TPL])
    document.userdata['dep_graph'].setdefault('extra_modal_links_tpl', []).extend([
        LEAN_LINKS_TPL, GITHUB_LINK_TPL])
