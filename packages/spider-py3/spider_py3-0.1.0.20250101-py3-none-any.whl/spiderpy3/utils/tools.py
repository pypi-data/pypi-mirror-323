import time
import random
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


def monitor_rate(func: Callable[[], int], interval: float = 1.0) -> None:
    """
    实时监控函数返回值的变化速率

    :param func: 返回当前值的函数
    :param interval: 统计间隔时间（秒）
    """
    last_length = func()
    start_time = time.perf_counter()
    last_time = start_time

    try:
        while True:
            current_time = time.perf_counter()
            elapsed_interval = current_time - last_time

            if elapsed_interval >= interval:
                current_length = func()
                delta = current_length - last_length
                rate = delta / elapsed_interval if elapsed_interval > 0 else 0
                elapsed_total = current_time - start_time

                # 输出监控信息
                print(
                    f"\r已运行时间：{elapsed_total:.2f}秒 | 增量：{delta} | 速率：{rate:.2f}个/秒 | 总数：{current_length}",
                    end=""
                )

                last_length = current_length
                last_time = current_time

    except KeyboardInterrupt:
        print("\n监控已停止")
    except Exception as e:
        print(f"\n错误：{e}")
