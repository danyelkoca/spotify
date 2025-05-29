import time
from tools.get_songs import get_songs, SongCache
from logger import SpotifyLogger

logger = SpotifyLogger.get_logger()


def test_caching():
    """Test the caching functionality of get_songs"""

    # Clear the cache first to ensure a fresh start
    cache = SongCache()
    cache.clear_cache()
    logger.info("Cache cleared, starting test")

    # First call - should fetch from API
    print("\nFirst call (uncached):")
    start_time = time.time()
    result1 = get_songs(limit=10)  # Using smaller limit for testing
    uncached_time = time.time() - start_time
    print(f"Time taken: {uncached_time:.2f} seconds")
    print(f"Success: {result1['success']}")
    print(f"Total tracks: {result1['total']}")

    # Second call - should use cache
    print("\nSecond call (should be cached):")
    start_time = time.time()
    result2 = get_songs(limit=10)
    cached_time = time.time() - start_time
    print(f"Time taken: {cached_time:.2f} seconds")
    print(f"Success: {result2['success']}")
    print(f"Total tracks: {result2['total']}")

    # Compare times
    time_difference = uncached_time - cached_time
    print(f"\nTime saved by caching: {time_difference:.2f} seconds")
    print(f"Cache speedup: {(uncached_time/cached_time):.1f}x faster")


if __name__ == "__main__":
    test_caching()
