from mi_modulo.cache_manager import DiskCacheManager

def test_cache_function():
    cache_manager = DiskCacheManager(cache_path="./test_cache")

    @cache_manager.cache_function
    def square(x):
        return x * x

    assert square(3) == 9
    assert square(3) == 9  # Verifica que usa el caché
