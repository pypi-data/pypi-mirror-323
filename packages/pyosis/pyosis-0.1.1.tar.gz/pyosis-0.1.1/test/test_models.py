"""Test the Osis model classes."""

import hypothesis

import pyosis


@hypothesis.given(osis_model=...)
def test_roundtrip_serialization(osis_model: pyosis.Osis) -> None:
    """Test that an Osis model can be serialized and deserialized.

    Args:
        osis_model: An Osis model instance.
    """
    serialized = osis_model.to_xml(pretty_print=True)
    deserialized = pyosis.Osis.from_xml(serialized)
    assert osis_model == deserialized
