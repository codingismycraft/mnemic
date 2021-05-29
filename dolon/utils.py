"""Exposes the basic interface to interact with the serialization means."""

import dolon.impl.utils_impl as utils_impl
import dolon.impl.get_all_tracers_impl as get_all_tracers_impl


async def process_message(db, payload):
    await utils_impl.process_message(db, payload)


async def get_latest_trace(app_name):
    return await utils_impl.get_latest_trace(app_name)


async def get_trace(uuid, db=None):
    return await utils_impl.get_trace(uuid, db)


async def get_all_tracers():
    return await get_all_tracers_impl.get_all_tracers()


async def get_trace_as_json(uuid):
    return await utils_impl.get_trace_as_json(uuid)


async def get_trace_run_info(uuid):
    return await utils_impl.get_trace_run_info(uuid)
