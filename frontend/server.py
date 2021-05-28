import os

import jinja2
from aiohttp import web

# root = os.path.dirname(os.path.abspath(__file__))
# templates_dir = os.path.join(root, 'templates')

env = jinja2.Environment(
    loader=jinja2.PackageLoader(
        'frontend',
        'templates'),
    autoescape=jinja2.select_autoescape(['html', 'xml'])
)

def load_static_content(filepath):
    """Loads static content from the "/static/" directory.

    :param str filepath: The filepath of the doc to load, relative to the
    static/ directory.
    :returns: The document for the passed-in filepath.
    :rtype: string.
    """
    dir_path = os.path.dirname(os.path.realpath(__file__))
    absolute_filepath = os.path.join(
        dir_path,
        'static/',
        filepath)
    with open(absolute_filepath) as f:
        return f.read()



class Handler:

    async def static_handler(self, request):

        directory = request.match_info['directory']
        filename = request.match_info['filename']
        relative_filepath = os.path.join(
            directory,
            filename,
        )
        try:
            content = load_static_content(relative_filepath)
        except FileNotFoundError:
            return web.Response(body="404 not found".encode(), status=404)

        content_type = 'text/html'
        if directory == 'css':
            content_type = 'text/css'

        return web.Response(
            body=content.encode(),
            content_type=content_type)


    async def main_page_handler(self, request):
        template = env.get_template('index.html')
        txt = template.render()

        return web.Response(
            body=txt.encode(),
            content_type='text/html'
        )

    async def handle_intro(self, request):
        return web.Response(text="Hello, world")

    async def handle_greeting(self, request):
        name = request.match_info.get('name', "Anonymous")
        txt = "Hello, {}".format(name)
        return web.Response(text=txt)


if __name__ == '__main__':
    app = web.Application()
    handler = Handler()
    app.add_routes(
        [
            web.get('/', handler.main_page_handler),
            web.get('/intro', handler.handle_intro),
            web.get('/greet/{name}', handler.handle_greeting),
            web.get(r"/static/{directory}/{filename}", handler.static_handler)
        ]
    )
    web.run_app(app, port=8900)
