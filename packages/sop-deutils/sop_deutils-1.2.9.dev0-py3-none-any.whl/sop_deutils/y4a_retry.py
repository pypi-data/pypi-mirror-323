import logging
import warnings
import functools
import time
from airflow.exceptions import AirflowTaskTimeout

warnings.filterwarnings("ignore", category=UserWarning)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)


class RetryContext:
    def __init__(self):
        self.in_retry = False


def retry_on_error(
    max_retries: int = 3,
    delay: int = 1,
):
    def decorator_retry(func):
        @functools.wraps(func)
        def wrapper_retry(*args, **kwargs):
            if retry_context.in_retry:
                return func(*args, **kwargs)

            attempts = 0
            while attempts < max_retries:
                try:
                    retry_context.in_retry = True
                    return func(*args, **kwargs)
                except Exception as e:

                    if isinstance(e, AirflowTaskTimeout):
                        raise

                    logging.error(e)
                    attempts += 1
                    logging.info(f'Retrying in {delay} seconds...')
                    time.sleep(delay)
                finally:
                    retry_context.in_retry = False
            raise RuntimeError('Maximum retries reached')
        return wrapper_retry
    return decorator_retry


retry_context = RetryContext()
