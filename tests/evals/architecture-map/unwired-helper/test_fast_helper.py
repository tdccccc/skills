from fast_helper import transform_fast


def test_transform_fast() -> None:
    assert transform_fast("  Daily   Papers ") == "daily papers"
