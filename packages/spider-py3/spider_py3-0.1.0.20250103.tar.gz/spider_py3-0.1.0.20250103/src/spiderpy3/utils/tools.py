import time
import random
from tqdm import tqdm
from typing import List, Callable, Any


def get_random_pick(data: List[Any]) -> Callable[[], Any]:
    """
    返回一个函数，该函数会从列表中随机选择元素，并确保在重新开始选择前，每个元素都被选过一次

    :param data: 要选择的列表
    :return: 随机选择元素的函数
    """
    shuffled_data = data[:]
    random.shuffle(shuffled_data)
    current_index = 0

    def random_pick() -> Any:
        """随机返回一个元素，确保所有元素被选过后重新打乱顺序"""
        nonlocal shuffled_data, current_index
        if current_index >= len(shuffled_data):
            shuffled_data = data[:]
            random.shuffle(shuffled_data)
            current_index = 0
        selected_item = shuffled_data[current_index]
        current_index += 1
        return selected_item

    return random_pick


class Tqdm(tqdm):
    @staticmethod
    def format_meter(*args, **kwargs):
        tqdm.format_meter(*args, **kwargs)

        prefix = kwargs["prefix"]
        n = kwargs["n"]
        elapsed = kwargs["elapsed"]
        rate_fmt = f"{(n / elapsed):.4f}个/秒" if elapsed != 0 else "?"
        rate_inv_fmt = f"{(elapsed / n):.4f}秒/个" if n != 0 else "?"

        return f"{prefix} [{rate_fmt} {rate_inv_fmt}]"


def monitor(func: Callable[[], int], interval: float = 1.0) -> None:
    with Tqdm(desc="监控") as pbar:
        while True:
            now_n = func()
            pbar.update(now_n - pbar.n)
            time.sleep(interval)
