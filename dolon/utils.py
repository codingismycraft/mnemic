"""Exposes the basic interface to interact with the serialization means."""

import dolon.impl.utils_impl as utils_impl


async def process_message(db, payload):
    """Processes a tracing message storing it to the db.

    :param db: The database object to use.

    :param dict payload: A dict representing the message to store.

    Can be either a tracing run creation in the form of:

        msg = {
            "msg_type": "create_trace_run",
            "app_name": app_name,
            "uuid": identifier,
            "column_names": ["v1", 'v2']
        }

    or for the insertion of a tracing row:

        msg = {
            "msg_type": "row",
            "uuid": identifier,
            "row_data": [12.2, 123.1]
        }

    raises: InvalidMessage
    """
    await utils_impl.process_message(db, payload)


async def get_trace(uuid):
    """Returns all the tracing rows for the passed in uuid.

    :param str uuid: The identifier for the trace run.

    :returns: A list of strings representing a csv view of the tracing run.
    :rtype: list[str]
    """
    return await utils_impl.get_trace(uuid)


async def get_all_tracers():
    """Returns a list with the names of all tracing runs.

    :returns: A list with the names of all tracing runs.
    :rtype: list[str]
    """
    return await utils_impl.get_all_tracers()


async def get_trace_as_json(uuid):
    """Returns all the tracing rows for the passed in uuid as json.

    :param str uuid: The identifier for the trace run.

    :returns: All the tracing rows for the passed in uuid as json.
    :rtype: list[dict]
    """
    return await utils_impl.get_trace_as_json(uuid)


async def get_trace_run_info(uuid):
    """Returns descriptive info for the passed in uuid.

    :param str uuid: The identifier for the trace run.

    :returns: Descriptive info for the passed in uuid.
    :rtype: dict
    """
    return await utils_impl.get_trace_run_info(uuid)


async def get_latest_trace(app_name):
    """Returns the latest trace for the passed in app_name.

    :return: A list of objects.
    """
    return await utils_impl.get_latest_trace(app_name)
