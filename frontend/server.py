import logging
import os
import uuid

import jinja2
import pandas as pd

import aiohttp

from aiohttp import web
from io import StringIO
import matplotlib.pyplot as plt

import dolon.utils as utils

logger = logging.getLogger("mnemic")

# root = os.path.dirname(os.path.abspath(__file__))
# templates_dir = os.path.join(root, 'templates')

env = jinja2.Environment(
    loader=jinja2.PackageLoader(
        'frontend',
        'templates'),
    autoescape=jinja2.select_autoescape(['html', 'xml'])
)

os.environ["POSTGRES_PASSWORD"] = "postgres123"
os.environ["POSTGRES_USER"] = "postgres"
os.environ["POSTGRES_DB"] = "mnemic"
os.environ["HOST"] = "127.0.0.1"

dir_path = os.path.dirname(os.path.realpath(__file__))
IMAGES_DIR = os.path.join(dir_path, 'static', 'images')

PATH_TO_STATIC = os.path.join(dir_path, 'static')


class Handler:

    async def trace_run_info_handler(self, request):
        uuid_for_run = request.rel_url.query['uuid']
        data = await utils.get_trace_run_info(uuid_for_run)
        logger.info(data)
        return web.json_response(data)

    async def tracers_handler(self, request):
        try:
            data = await utils.get_all_tracers()
            return web.json_response(data)
        except Exception as ex:
            logger.exception(ex)
            raise aiohttp.web.HTTPInternalServerError()


    async def tracer_run_handler(self, request):
        uuid_for_run = request.rel_url.query['uuid']
        data = await utils.get_trace(uuid_for_run)
        df = pd.read_csv(StringIO(data))
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
                plt.savefig(os.path.join(IMAGES_DIR, filename))
                images.append(filename)
            except Exception as ex:
                print(ex, type(ex))

        html_code = ''
        for image_name in images:
            image_html = f'<img src="/static/images/{image_name}" alt="image n/a" width="1000px" height="240px">'
            print(image_html)
            html_code += image_html

        return web.json_response(
            text=html_code,
            content_type='text/html'
        )

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
    conn_str = f'postgresql://postgres:postgres123@localhost:5432/mnemic'
    utils.set_conn_str(conn_str)
    app = web.Application()
    handler = Handler()
    app.add_routes(
        [
            web.get('/', handler.main_page_handler),
            web.get('/intro', handler.handle_intro),
            web.get('/greet/{name}', handler.handle_greeting),
            web.get('/tracers', handler.tracers_handler),
            web.get('/tracer_run', handler.tracer_run_handler),
            web.get('/trace_run_info', handler.trace_run_info_handler)
        ]

    )
    app.router.add_static('/static', PATH_TO_STATIC)
    web.run_app(app, port=8900)
