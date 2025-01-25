import pytest

from tests.utils import build_rule


@pytest.mark.parametrize(
    "event,expected",
    [
        ({"a": "cABpAG4AZw"}, True),
        ({"a": "AAaQBuAGcA"}, True),
        ({"a": "wAGkAbgBnA"}, True),
        ({"a": "foo"}, False),
    ],
)
def test_wide(event: dict, expected: bool):
    rule = build_rule(
        """
detection:
  foo:
    a|wide|base64offset: ping
  condition: foo
        """
    )
    assert rule.match(event) is expected
