import diskcache
from functools import wraps

class DiskCacheManager:
    """
    Manages a shared diskcache instance for caching functions and properties.
    """
    def __init__(self, cache_path="./cache"):
        """
        Initializes the cache manager with a specified cache directory.

        Args:
            cache_path (str): Path to the directory where the cache will be stored.
        """
        self.cache = diskcache.Cache(cache_path)

    def cache_function(self, func):
        """
        Decorator to cache the results of a function using diskcache.

        Args:
            func (callable): The function to be cached.

        Returns:
            callable: A wrapped function that uses diskcache.
        """
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Create a unique cache key based on function name, args, and kwargs
            key = (func.__name__, args, frozenset(kwargs.items()))
            try:
                # Return the cached result if available
                return self.cache[key]
            except KeyError:
                # If not in cache, compute the result, cache it, and return
                result = func(*args, **kwargs)
                self.cache[key] = result
                return result
            except Exception as e:
                raise RuntimeError(f"Error accessing cache: {e}") from e

        return wrapper

    def cache_property(self, func):
        """
        Decorator to cache the result of a property in a class using diskcache.

        Args:
            func (callable): The property method to be cached.

        Returns:
            property: A property object that caches its result.
        """
        @wraps(func)
        def wrapper(instance, *args, **kwargs):
            # Create a unique cache key based on the function name and the instance's id
            key = (func.__name__, id(instance))
            try:
                # Attempt to fetch the value from the cache
                return self.cache[key]
            except KeyError:
                # If not in cache, compute the result, store it, and return
                result = func(instance, *args, **kwargs)
                self.cache[key] = result  # Store the result without expiration
                return result
            except Exception as e:
                raise RuntimeError(f"Error accessing cache for property '{func.__name__}': {e}") from e

        # Return a property object instead of the decorated function
        return property(wrapper)

# Example usage
if __name__ == "__main__":
    # Initialize a DiskCacheManager with a specific cache directory
    cache_manager = DiskCacheManager(cache_path="./custom_cache")

    class MyClass:
        @cache_manager.cache_property
        def expensive_property(self):
            """
            Simulates an expensive computation whose result will be cached.

            Returns:
                dict: A dictionary containing computed values.
            """
            return {'result': 42}

    obj = MyClass()
    print(obj.expensive_property)  # Compute and cache the result
    print(obj.expensive_property)  # Fetch the result from the cache
