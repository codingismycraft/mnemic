"""Exposes the mnemic UI server."""

import asyncio
import datetime
import functools
import glob
import logging
import os
import uuid

import aiohttp
import aiohttp.web as web
import io
import jinja2
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

import dolon.utils as utils

logger = logging.getLogger("mnemic")

_PORT = int(os.environ["FRONT_END_PORT"])

_JINJA_ENV = jinja2.Environment(
    loader=jinja2.PackageLoader(
        'templates',
        'templates'),
    autoescape=jinja2.select_autoescape(['html', 'xml'])
)

_CURR_DIR = os.path.dirname(os.path.realpath(__file__))
_IMAGES_DIR = os.path.join(_CURR_DIR, 'static', 'images')
_PATH_TO_STATIC = os.path.join(_CURR_DIR, 'static')
_IMG_URL = ('<img src="/static/images/{image_name}" alt="image n/a" '
            'width="{width}px" height="{height}px">').format
_CONN_STR = f'postgresql://postgres:postgres123@localhost:5432/mnemic'
_IMAGE_CLEANUP_FREQUENCY_IN_SECS = 30
_IMAGE_MAX_LIFE_SPAN_IN_SECS = 10


async def clear_images():
    """Removes unused images."""
    logger.info("Enters image cleaning loop.")
    while 1:
        await asyncio.sleep(_IMAGE_CLEANUP_FREQUENCY_IN_SECS)
        logger.info("Deleting images..")
        files = glob.glob(f'{_IMAGES_DIR}/*.png')
        for f in files:
            time_now = datetime.datetime.now()
            file_time = datetime.datetime.fromtimestamp(os.path.getmtime(f))
            life_span_in_seconds = (time_now - file_time).total_seconds()
            if life_span_in_seconds > _IMAGE_MAX_LIFE_SPAN_IN_SECS:
                try:
                    os.remove(f)
                except Exception as ex:
                    logger.exception(ex)


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


def make_image_file():
    image_prefix = str(uuid.uuid4())
    filename = f'{image_prefix}_figure.png'
    return filename


def make_correlation_heat_map(
        data,
        title='Correlation Heat Map',
        linewidths=0,
        figsize=(9, 6),
        annot=False):
    cmap = sns.diverging_palette(14, 120, as_cmap=True)
    data = data.dropna()
    corr = data.corr()
    for column_name in corr.columns:
        corr[column_name] = corr[column_name].abs()
    _, ax = plt.subplots(figsize=figsize)
    if title:
        ax.set_title(title)

    heat_map = sns.heatmap(corr, annot=annot, fmt="2.2f",
                           linewidths=linewidths, ax=ax, cmap=cmap)
    figure = heat_map.get_figure()
    figure.set_size_inches(10, 12)
    filename = make_image_file()
    figure.savefig(os.path.join(_IMAGES_DIR, filename), dpi=400)
    return filename, figure


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
        if len(df) == 0:
            # There are no rows for the requested run.
            return web.json_response(
                text="<h1>This tracer does not have any rows to show</h1>",
                content_type='text/html'
            )
        margin_factor = 0.1
        images = []
        image_prefix = str(uuid.uuid4())
        fig_index = 0
        for column_name in df.columns:
            if column_name == 'time':
                continue
            min_value = min(df[column_name])
            max_value = max(df[column_name])
            title = column_name.replace("_", " ").replace("-", " ").title()
            the_plot = df.plot.line(x="time", y=column_name, rot=0,
                                    grid=True,
                                    figsize=(12, 3), title=title,
                                    legend=False)
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
            the_plot.set_facecolor('gainsboro')
            total_number_of_points = len(df)
            x_ticks = np.arange(10, total_number_of_points,
                                total_number_of_points / 12)
            x_ticks = [int(index) for index in x_ticks]
            plt.xticks(x_ticks)
            plt.savefig(os.path.join(_IMAGES_DIR, filename))
            plt.close(the_plot.get_figure())
            images.append(filename)
        correlation_file_name, figure = make_correlation_heat_map(df)
        plt.close(figure)
        html_code = ''
        for image_name in images:
            image_html = _IMG_URL(image_name=image_name, width=1000, height=240)
            html_code += image_html

        html_code += '<div style:"width:1000px;background-color: white">' + _IMG_URL(
            image_name=correlation_file_name, width=600, height=500
        ) + '</div>'

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


def run():
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
    asyncio.ensure_future(clear_images())
    app.router.add_static('/static', _PATH_TO_STATIC)
    web.run_app(app, port=_PORT)


if __name__ == '__main__':
    run()
