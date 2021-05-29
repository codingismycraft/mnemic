"""Tests async profiler."""

import asyncio
import unittest

import dolon.profiler as profiler
import dolon.tests.utils as utils

# Aliases.
async_testable = utils.async_testable


class TestProfiler(unittest.TestCase):

    @async_testable
    async def test_get_profiling_functions(self):
        """Tests a full run."""
        profiler.clear()

        @profiler.profiler
        async def goo():
            """Dummy func to use for testing."""
            await asyncio.sleep(0.1)

        @profiler.profiler
        async def foo():
            """Dummy func to use for testing."""
            await asyncio.sleep(0.1)

        prefix = "TestProfiler.test_get_profiling_functions.<locals>."

        N = 5

        tasks = [(goo()) for _ in range(N)]
        tasks += [(foo()) for _ in range(N)]

        await asyncio.gather(*tasks)

        retrieved_func_names = []

        for profiling_func in profiler.get_profiling_functions(True):
            func_name = profiling_func.__name__
            retrieved_func_names.append(func_name)
            if func_name.endswith('_hits'):
                value = await profiling_func()
                self.assertEqual(value, N)

        expected_func_names = [
            f'{prefix}goo_hits',
            f'{prefix}goo_active_instances',
            f'{prefix}goo_average_time',
            f'{prefix}foo_hits',
            f'{prefix}foo_active_instances',
            f'{prefix}foo_average_time'
        ]

        self.assertListEqual(retrieved_func_names, expected_func_names)


if __name__ == '__main__':
    unittest.main()
