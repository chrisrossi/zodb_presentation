from mimetypes import guess_type
from repoze.folder import Folder

from pyramid.events import BeforeRender
from pyramid.events import subscriber
from pyramid.httpexceptions import HTTPFound
from pyramid.renderers import get_renderer
from pyramid.response import Response
from pyramid.traversal import find_model
from pyramid.url import static_url
from pyramid.view import view_config

from surebro.catalog import index_doc
from surebro.catalog import query
from surebro.catalog import unindex_doc
from surebro.content import Page
from surebro.content import Site


@subscriber(BeforeRender)
def add_renderer_globals(event):
    """
    Set up variables used in all templates.
    """
    request = event['request']
    event['nav'] = [
        {'title': page.title, 'url': request.resource_url(page)} for
        page in request.root.values() if isinstance(page, Page)]
    event['nav'].insert(0, {'title': 'Home', 'url': request.application_url})
    event['owrap'] = get_renderer('templates/main.pt').implementation()
    event['static_url'] = request.static_url('static/')
    event['title'] = event['context'].title
    event['search_url'] = request.resource_url(request.root, 'search')


@view_config(context=Page, renderer='templates/view_page.pt')
def view_page(context, request):
    if context.image:
        img_url = request.resource_url(context, 'image')
    else:
        img_url = None
    actions = [{'title': 'Edit this page',
                'url': request.resource_url(context, 'edit')}]
    if not isinstance(context, Site):
        actions.append({'title': 'Delete this page',
                        'url': request.resource_url(context, 'delete')})

    return {'body': context.html(request.resource_url),
            'img_url': img_url, 'actions': actions}


@view_config(name='edit', context=Page, renderer='templates/edit_page.pt')
def edit_page(context, request):
    params = request.params

    if 'save' in params:
        context.title = params['title']
        context.body = params['body']
        image = params.get('image')
        if hasattr(image, 'file'):
            mimetype = guess_type(image.filename)[0]
            context.upload_image(mimetype, image.file)
        index_doc(context)
        return HTTPFound(request.resource_url(context))

    elif 'cancel' in params:
        return HTTPFound(request.resource_url(context))

    # Show form
    if context.image:
        img_url = request.resource_url(context, 'image')
    else:
        img_url = None

    return {
        'title': 'Edit Page',
        'img_url': img_url,
        'page': context,
    }


@view_config(name='add_page', context=Site, renderer='templates/edit_page.pt')
def add_page(context, request):
    params = request.params

    if 'save' in params:
        # Construct page
        page = Page(params['title'], params['body'])

        # Insert page into document tree
        path = params['path']
        try:
            prev = find_model(context, path)

            # Replace an existing node
            for name, child in prev.items():
                page[name] = child
            folder, page_name = prev.__parent__, prev.__name__
            del folder[page_name]
            folder[page_name] = page
        except KeyError:
            # Insert page at new location
            path = filter(None, path.split('/'))
            page_name = path.pop(-1)
            folder = context
            for name in path:
                if name not in folder:
                    folder[name] = Folder()
                folder = folder[name]
            folder[page_name] = page

        # Handle image upload
        image = params.get('image')
        if hasattr(image, 'file'):
            mimetype = guess_type(image.filename)[0]
            page.upload_image(mimetype, image.file)

        index_doc(page)
        return HTTPFound(request.resource_url(page))

    elif 'cancel' in params:
        redirect_to = params['backto']
        if not redirect_to:
            redirect_to = request.resource_url(context)
        return HTTPFound(redirect_to)

    # Show form
    backto = request.referer
    if backto is None:
        backto = ''
    return {
        'title': 'New Page',
        'img_url': None,
        'page': Page('Page Title', ''),
        'backto': backto,
    }


@view_config(name='image', context=Page)
def view_image(context, request):
    return Response(
        app_iter=app_iter_from_stream(context.image.data.open()),
        content_type=context.image.mimetype)


def app_iter_from_stream(stream, block_size=1<<20):
    block = stream.read(block_size)
    while block:
        yield block
        block = stream.read(block_size)


@view_config(name='delete', context=Page)
def delete_page(context, request):
    assert not isinstance(context, Site)
    unindex_doc(context)
    folder = context.__parent__
    id = context.__name__
    del folder[id]
    if len(context):
        new_context = Folder()
        for k, v in context.items():
            new_context[k] = v
        folder[id] = new_context
    while not isinstance(folder, Page):
        folder = folder.__parent__
    return HTTPFound(request.resource_url(folder))


@view_config(name='search', context=Site,
             renderer='templates/search_results.pt')
def search(context, request):
    term = request.params.get('term')
    if term:
        count, docids, resolve = query(
            context, 'term in text', sort_index='text',
            names={'term': request.params.get('term')})
        results = [resolve(docid) for docid in docids]
    else:
        results = []
    return {'title': 'Search Results', 'results': results}




