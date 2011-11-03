from pyramid.traversal import find_resource
from pyramid.traversal import find_root
from pyramid.traversal import resource_path

from repoze.catalog.catalog import Catalog
from repoze.catalog.indexes.text import CatalogTextIndex
from repoze.catalog.document import DocumentMap


def make_catalog():
    catalog = Catalog()
    catalog['text'] = CatalogTextIndex(get_text)
    catalog.document_map = DocumentMap()
    return catalog


def get_text(doc, default):
    return ' '.join([doc.title] * 10 + [doc.body])


def find_catalog(context):
    return find_root(context).catalog


def index_doc(doc):
    catalog = find_catalog(doc)
    if hasattr(doc, 'docid'):
        # Already in catalog, reindex
        catalog.reindex_doc(get_docid(catalog, doc), doc)

    else:
        # New document
        catalog.index_doc(get_docid(catalog, doc), doc)


def unindex_doc(doc):
    catalog = find_catalog(doc)
    catalog.document_map.remove_docid(doc.docid)
    catalog.unindex_doc(doc.docid)
    del doc.docid


def get_docid(catalog, doc):
    # Docid is stored as 'docid' attribute of document after it is
    # assigned.
    document_map = catalog.document_map
    path = resource_path(doc)
    docid = getattr(doc, 'docid', None)
    if docid is None:
        # Assign new docid.
        docid = document_map.add(path)
        setattr(doc, 'docid', docid)

    return docid


def query(context, queryobject, sort_index=None, limit=None, sort_type=None,
          reverse=False, names=None):
    site = find_root(context)
    catalog = find_catalog(site)
    document_map = catalog.document_map

    def resolve(docid):
        path = document_map.address_for_docid(docid)
        return find_resource(site, path)

    count, docids = catalog.query(
        queryobject,
        sort_index=sort_index,
        limit=limit,
        sort_type=sort_type,
        reverse=reverse,
        names=names)

    return count, docids, resolve
