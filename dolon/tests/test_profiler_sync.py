"""Tests sync profiler."""

import time
import unittest

import dolon.profiler as profiler



class TestProfilerSync(unittest.TestCase):
    """Tests sync profiler."""

    def test_get_profiling_functions(self):
        """Tests sync profiler."""
        profiler.clear()
        N = 3
        prefix = "TestProfilerSync.test_get_profiling_functions.<locals>."

        class RetrieveInfo:
            """Dummy class used for testing."""

            @profiler.profiler
            def retriever(self):
                """Dummy method for testing."""
                time.sleep(0.01)

        @profiler.profiler
        def foo():
            """Dummy function for testing."""
            time.sleep(0.2)

        ri = RetrieveInfo()

        for _ in range(N):
            ri.retriever()
            foo()

        retrieved_func_names = []
        for profiling_func in profiler.get_profiling_functions():
            func_name = profiling_func.__name__
            retrieved_func_names.append(func_name)
            if func_name.endswith('_hits'):
                value = profiling_func()
                self.assertEqual(value, N)

        expected_func_names = [
            f'{prefix}RetrieveInfo.retriever_hits',
            f'{prefix}RetrieveInfo.retriever_active_instances',
            f'{prefix}RetrieveInfo.retriever_average_time',
            f'{prefix}foo_hits',
            f'{prefix}foo_active_instances',
            f'{prefix}foo_average_time'
        ]

        self.assertListEqual(retrieved_func_names, expected_func_names)


if __name__ == '__main__':
    unittest.main()
