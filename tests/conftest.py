import pytest

from inventory import GenerationParams, generate_dataset


@pytest.fixture(scope="session")
def small_dataset():
    """Compact dataset reused across the suite for speed."""
    return generate_dataset(
        GenerationParams(n_products=10, n_days=90, seed=123)
    )
