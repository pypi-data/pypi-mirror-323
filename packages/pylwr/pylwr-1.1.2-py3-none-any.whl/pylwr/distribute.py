m = {}

def distribute(func):
    """装饰器函数，用于根据给定的名称动态调用已注册的函数。

    如果名称在注册的函数字典 `m` 中存在，则调用对应的函数，
    否则调用默认的 `func` 函数。

    Args:
        func (Callable): 默认的回调函数，在未找到注册函数时调用。

    Returns:
        Callable: 包装后的函数，接收 (name, msg) 参数，根据名称分发任务。
    """

    def _deal(name, msg):
        """内部函数，处理分发逻辑。

        Args:
            name (str): 要调用的函数名称。
            msg (Any): 传递给函数的参数。

        Returns:
            Any: 执行注册函数或默认函数的返回值。
        """
        cal = m.get(name)
        if cal is not None:
            return cal(msg)
        else:
            return func(msg)

    return _deal


def add(name):
    """装饰器函数，在字典 `m` 中注册新的函数。

    此装饰器在编译时执行，将函数与指定的名称绑定到全局字典 `m` 中。

    Args:
        name (str): 要注册的函数名称。

    Returns:
        Callable: 装饰器函数，将目标函数注册到 `m` 字典。
    """

    def _add_m(func):
        """内部装饰器函数，执行注册操作。

        Args:
            func (Callable): 需要注册的函数。

        Returns:
            Callable: 原始函数，保持不变。
        """
        m[name] = func
        return func

    return _add_m


@distribute
def target_fun(msg):
    """默认处理函数，当未找到注册的处理函数时调用。

    Args:
        msg (Any): 要处理的信息。

    Returns:
        None
    """
    print('other', msg)
