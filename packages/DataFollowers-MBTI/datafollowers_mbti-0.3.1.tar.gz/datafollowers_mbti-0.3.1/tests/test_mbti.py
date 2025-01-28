from mbti.cli import check_type
import pytest

def test_check_type():
    mbti_type = check_type("ISFP")

    assert mbti_type is not None
    assert len(mbti_type) > 2
