from jove_catalog.interfaces import CatalogDescriptor
from jove_catalog.utils import find_catalog

from repoze.catalog.indexes.text import CatalogTextIndex
from repoze.catalog.document import DocumentMap


class SurebroCatalog(CatalogDescriptor):

    def indexes(self):
        return {
            'text': CatalogTextIndex(get_text),
        }


def get_text(doc, default):
    return ' '.join([doc.title] * 10 + [doc.body])


def index_doc(doc):
    catalog = find_catalog(doc)
    if hasattr(doc, 'docid'):
        # Already in catalog, reindex
        catalog.reindex_doc(doc)

    else:
        # New document
        catalog.index_doc(doc)


def unindex_doc(doc):
    catalog = find_catalog(doc)
    catalog.unindex_doc(doc)