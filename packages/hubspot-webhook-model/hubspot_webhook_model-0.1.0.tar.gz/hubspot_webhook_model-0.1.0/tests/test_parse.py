from pathlib import Path

import msgspec.json

from hubspot_webhook_model import Event_, Message


def test_parse():
    for p in Path("tests").glob("*.json"):
        msgspec.json.decode(p.read_bytes(), type=Event_)

def test_parse_all():
    data = '['+','.join(p.read_text() for p in Path("tests").glob("*.json"))+']'
    model = msgspec.json.decode(data, type=Message)
    assert model
