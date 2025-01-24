import concurrent.futures
import time
from functools import wraps
import threading

# 全局锁，防止并发访问时出现竞争
_global_lock = threading.Lock()

# 记录每个函数的调用历史
_call_history = {}

def rate_limit_calls(max_calls_per_period: int, period: float):
    """
    A general rate limiting decorator.

    Args:
        max_calls_per_period (int): Maximum number of calls allowed within the period.
        period (float): The time window for rate limiting in seconds.

    Returns:
        function: The decorated function with rate limiting logic.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            now = time.time()
            with _global_lock:
                # 取出该函数的调用历史时间列表
                call_times = _call_history.setdefault(func, [])

                # 只保留 period 时间范围内的调用时间
                call_times = [t for t in call_times if t > now - period]

                # 判断是否超限
                if len(call_times) >= max_calls_per_period:
                    raise Exception(f"Rate limit exceeded: {func.__name__} "
                                    f"can only be called {max_calls_per_period} times "
                                    f"every {period} seconds.")

                # 记录本次调用时间
                call_times.append(now)
                _call_history[func] = call_times

            return func(*args, **kwargs)
        return wrapper
    return decorator

# 超时重试装饰器
def retry_on_timeout(max_retries, delay, timeout):
    """
    A decorator that retries a function execution with a specified delay and timeout.

    Args:
        max_retries (int): The maximum number of retries.
        delay (float): The delay between each retry in seconds.
        timeout (float): The timeout for each function call in seconds.

    Returns:
        function: The decorated function with retry logic.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            for attempt in range(max_retries):
                with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                    future = executor.submit(func, self, *args, **kwargs)
                    try:
                        return future.result(timeout=timeout)
                    except concurrent.futures.TimeoutError:
                        # 如果到达最后一次重试，抛出超时异常
                        if attempt >= max_retries - 1:
                            raise TimeoutError(
                                f"Function '{func.__name__}' timed out after {timeout} seconds "
                                f"(attempt {attempt + 1}/{max_retries})."
                            )
                        else:
                            # 等待一段时间再重试
                            time.sleep(delay)

        return wrapper
    return decorator


