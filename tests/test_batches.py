import pytest

from etm_service.batches import Batches
from etm_service.curve import Curve
from etm_service.value import Value

@pytest.fixture
def values():
    return [Value('query_one', 'query'), Curve('interconnector_price_curve', 'curve')]

def test_add_values(values):
    batches = Batches()

    # Are they all valid?
    for batch in batches.each():
        assert batch.is_empty()

    # Let's add some things
    for value in values:
        batches.add(value)

    # Is there something in them?
    for batch in batches.each():
        if batch.endpoint == 'nodes' or batch.endpoint == 'inputs': continue # Not yet in the test

        assert not batch.is_empty()
