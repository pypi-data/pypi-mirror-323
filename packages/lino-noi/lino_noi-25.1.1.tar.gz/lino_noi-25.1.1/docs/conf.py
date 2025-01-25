# -*- coding: utf-8 -*-

import datetime
from atelier.sphinxconf import configure; configure(globals())
from lino.sphinxcontrib import configure; configure(globals())

extensions += ['lino.sphinxcontrib.base']
extensions += ['lino.sphinxcontrib.logo']

extensions += ['lino.sphinxcontrib.help_texts_extractor']
help_texts_builder_targets = {'lino_noi.': 'lino_noi.lib.noi'}

# from rstgen.sphinxconf import interproject
# interproject.configure(globals(), 'atelier')

project = "Lino Noi"
html_title = "Lino Noi"

copyright = '2014-{} Rumma & Ko Ltd'.format(datetime.date.today().year)

# suppress_warnings = ['image.nonlocal_uri']
blogref_format = "https://luc.lino-framework.org/blog/%Y/%m%d.html"

# html_context.update(public_url='https://noi.lino-framework.org')

# from pprint import pprint
# pprint(intersphinx_mapping)
