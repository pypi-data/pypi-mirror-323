from typing import Any, Union

def seed(rseed: int) -> None: ...
def shuffle(array: list) -> None:
    """清洗列表中的元素，使其随机排列。

    Args:
        array (list): 要清洗的列表。
    """
    ...

def random_sample(container: Union[list, tuple, str, bytes], count: int) -> list[Any]:
    """从容器中随机抽取count个元素。

    Args:
        container (Union[list, tuple, str, bytes]): 要抽取的容器。
        count (int): 要抽取的元素个数。

    Returns:
        list[Any]: 抽取的元素。

    """

def random_integer_noargs() -> int:
    """生成一个随机整数

    Returns:
        int: 随机整数。
    """
    ...

def randbelow(n: int) -> int:
    """返回一个随机整数，范围是[0, n)。

    Args:
        n (int): 范围的上限。

    Returns:
        int: 随机整数。
    """
    ...

def random_choice(container: Union[list, tuple, str, bytes]) -> Any:
    """从列表、元组、字符串或字节串中随机选择一个元素。

    Args:
        elements (Union[list, tuple, str, bytes]): 要选择的元素。

    Returns:
        Any: 随机选择的元素。
    """
    ...

def random_choices(container: Union[list, tuple, str, bytes], count: int) -> list[Any]:
    """从列表、元组、字符串或字节串中随机选择count个元素。

    Args:
        elements (Union[list, tuple, str, bytes]): 要选择的元素。
        count (int): 选择的元素个数。

    Returns:
        list[Any]: 随机选择的元素。
    """
    ...

def randint(min: int, max: int) -> int:
    """返回一个随机整数，范围是[min, max]。

    Args:
        min (int): 最小值。
        max (int): 最大值。

    Returns:
        int: 随机整数。
    """
    ...

def randrange(start: int, stop: int = 0, step: int = 1) -> int:
    """返回一个随机整数，范围是[start, stop)。

    Args:
        start (int): 开始值。
        stop (int, optional): 结束值. 默认为0。
        step (int, optional): 步进. 默认为1。

    Returns:
        int: 范围内随机整数。
    """
    ...

def random_double(a: float, b: float) -> float:
    """返回一个随机浮点数，范围是[a,b)。

    Args:
        a (float): a float
        b (float): a float

    Returns:
        float: 范围内随机浮点数
    """
    ...

def random_double_noargs() -> float:
    """1~0之间的随机浮点数

    Returns:
        float: 1~0之间的随机浮点数
    """
    ...
