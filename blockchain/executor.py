from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Callable, List, Any


class ParallelExecutor:
    """
    Simple thread-based parallel executor. Accepts a list of callables (no args)
    and returns results in the same order.
    """

    def __init__(self, max_workers: int = None):
        self.max_workers = max_workers

    def execute(self, tasks: List[Callable[[], Any]]) -> List[Any]:
        if not tasks:
            return []
        results = [None] * len(tasks)
        with ThreadPoolExecutor(max_workers=self.max_workers) as ex:
            futures = {ex.submit(task): idx for idx, task in enumerate(tasks)}
            for fut in as_completed(futures):
                idx = futures[fut]
                try:
                    results[idx] = fut.result()
                except Exception as e:
                    results[idx] = e
        return results
