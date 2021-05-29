"""Exposes the mnemic UI server."""

import functools
import logging
import os
import uuid

import aiohttp
import aiohttp.web as web
import io
import jinja2
import matplotlib.pyplot as plt
import pandas as pd

import dolon.utils as utils

logger = logging.getLogger("mnemic")

_PORT = 8900

_JINJA_ENV = jinja2.Environment(
    loader=jinja2.PackageLoader(
        'frontend',
        'templates'),
    autoescape=jinja2.select_autoescape(['html', 'xml'])
)

_CURR_DIR = os.path.dirname(os.path.realpath(__file__))
_IMAGES_DIR = os.path.join(_CURR_DIR, 'static', 'images')
_PATH_TO_STATIC = os.path.join(_CURR_DIR, 'static')
_IMG_URL = ('<img src="/static/images/{image_name}" alt="image n/a" '
            'width="1000px" height="240px">').format
_CONN_STR = f'postgresql://postgres:postgres123@localhost:5432/mnemic'

def web_handler(handler_func):
    """Wraps a handler function adding standard processing."""

    @functools.wraps(handler_func)
    async def _inner(*args, **kwargs):
        """The decorator function."""
        try:
            return await handler_func(*args, **kwargs)
        except Exception as ex:
            logger.exception(ex)
            raise aiohttp.web.HTTPInternalServerError()

    return _inner


class Handler:
    """Implements all the web handlers used from the service."""

    @web_handler
    async def trace_run_info_handler(self, request):
        """Returns the basic information for the passed in run.

        Expects the uuid of the run which is used to retrieve and return
        a json document consisting of a dict similar to the following:
            {
                'app_name': run-name,
                'counter': number-of-points,
                'started': start-time
                'duration': duration-time
            }
        """
        uuid_for_run = request.rel_url.query['uuid']
        data = await utils.get_trace_run_info(uuid_for_run)
        return web.json_response(data)

    @web_handler
    async def tracers_handler(self, request):
        """Returns all the available tracer runs sorted by creation time.

        :returns: A json document containing the tracing runs in the
        following format:
            [
               {
                  "tracer_name":"testing_app",
                  "runs":[
                     {
                        "creation_time":"2021-05-29 21:00:20",
                        "uuid":"eefba555-b816-427f-8138-02013067bad8"
                     }
                  ]
               }
            ]
        """
        data = await utils.get_all_tracers()
        return web.json_response(data)

    @web_handler
    async def tracer_run_handler(self, request):
        """Returns all the rows for the passed in run.

        Expects the uuid of the tracer run to be passed as a query parameter.
        """
        uuid_for_run = request.rel_url.query['uuid']
        data = await utils.get_trace(uuid_for_run)
        df = pd.read_csv(io.StringIO(data))
        margin_factor = 0.1
        images = []
        image_prefix = str(uuid.uuid4())
        fig_index = 0
        for column_name in df.columns:
            if column_name == 'time':
                continue

            try:
                min_value = min(df[column_name])
                max_value = max(df[column_name])
                df.plot.line(x="time", y=column_name, rot=0, grid=True,
                             figsize=(12, 3), title=column_name)
                if max_value > min_value:
                    height = max_value - min_value
                    plt.ylim([min_value - height * margin_factor,
                              max_value + height * margin_factor])
                elif max_value < min_value:
                    max_value, min_value = min_value, max_value
                    height = max_value - min_value
                    plt.ylim([min_value - height * margin_factor,
                              max_value + height * margin_factor])
                else:
                    height = 0.2
                    plt.ylim([min_value - height * margin_factor,
                              max_value + height * margin_factor])
                fig_index += 1
                filename = f'{image_prefix}_figure_{fig_index}.png'
                plt.savefig(os.path.join(_IMAGES_DIR, filename))
                images.append(filename)
            except Exception as ex:
                logger.exception(ex)
                raise aiohttp.web.HTTPInternalServerError()

        html_code = ''
        for image_name in images:
            image_html = _IMG_URL(image_name=image_name)
            html_code += image_html

        return web.json_response(
            text=html_code,
            content_type='text/html'
        )

    @web_handler
    async def main_page_handler(self, request):
        """Displays the main page."""
        template = _JINJA_ENV.get_template('index.html')
        txt = template.render()
        return web.Response(
            body=txt.encode(),
            content_type='text/html'
        )


if __name__ == '__main__':
    utils.set_conn_str(_CONN_STR)
    app = web.Application()
    handler = Handler()
    app.add_routes(
        [
            web.get('/', handler.main_page_handler),
            web.get('/tracers', handler.tracers_handler),
            web.get('/tracer_run', handler.tracer_run_handler),
            web.get('/trace_run_info', handler.trace_run_info_handler)
        ]
    )
    app.router.add_static('/static', _PATH_TO_STATIC)
    web.run_app(app, port=_PORT)
