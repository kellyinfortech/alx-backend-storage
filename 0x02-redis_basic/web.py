import redis
import requests
from functools import wraps
from typing import Callable

redis_store = redis.Redis()

def url_access_counter(method: Callable) -> Callable:
    """Decorator to track the number of times a URL is accessed."""
    @wraps(method)
    def wrapper(url: str) -> str:
        """Wrapper function to count URL accesses."""
        redis_store.incr(f'count:{url}')
        return method(url)
    return wrapper

def cache_with_expiry(method: Callable) -> Callable:
    """Decorator to cache the result of a method with a specified expiration time."""
    @wraps(method)
    def wrapper(url: str) -> str:
        """Wrapper function to cache the result with an expiration time."""
        result = redis_store.get(f'result:{url}')
        if result:
            return result.decode('utf-8')
        result = method(url)
        redis_store.setex(f'result:{url}', 10, result)  # Cache result with 10-second expiration
        return result
    return wrapper

@url_access_counter
@cache_with_expiry
def get_page(url: str) -> str:
    """Fetches the HTML content of a URL, caches the result, and tracks the access count."""
    return requests.get(url).text

# Example usage
if __name__ == "__main__":
    # Test with a slow response URL
    slow_url = 'http://slowwly.robertomurray.co.uk/delay/5000/url/http://www.example.com'
    
    # Access the URL multiple times to see the count incrementing and caching in action
    for _ in range(3):
        content = get_page(slow_url)
        print(content)
    
    # Check the access count for the slow URL
    count = redis_store.get(f'count:{slow_url}')
    print(f"Access count for {slow_url}: {count.decode('utf-8')}")

