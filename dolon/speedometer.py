"""A class that can measure the speed for a monotonically increasing  value."""

import asyncio
import datetime


class Speedometer:
    """Simple class to measure speed.

    Applicable in cases where you have a long-lived process that is running
    in the background, and you need to now its speed in a granular level.

    Can be used in cases where we have a value that is being increasing as time
    goes by to measure its speed in value per time.

    As an example you can think of a global count for messages consumed from an
    exchange; the count is increasing as time goes by and what we need to know
    is how many messages are created per a specific interval.
    """

    def __init__(self, time_interval=2):
        """Initializer.

        :param float time_interval: How ofter the speed will be updated,
        calls that occur in the meanwhile will just return the previous
        speed.
        """
        self._last_updated_time = None
        self._last_updated_value = None
        self._time_interval = time_interval
        self._previous_speed = None
        self._lock = asyncio.Lock()

    async def get_speed(self, value):
        """Returns the current speed for the value."""
        async with self._lock:
            if self._last_updated_time is None:
                self._last_updated_time = datetime.datetime.now()
                self._last_updated_value = value
                self._previous_speed = 0
                return 0
            else:
                now = datetime.datetime.now()
                time_diff = (now - self._last_updated_time).total_seconds()
                if time_diff == 0:
                    return 0
                elif time_diff <= self._time_interval:
                    return self._previous_speed
                else:
                    msg_produced_meanwhile = value - self._last_updated_value
                    speed = msg_produced_meanwhile / time_diff
                    self._previous_speed = speed

                    self._last_updated_time = now
                    self._last_updated_value = value
                    return speed
