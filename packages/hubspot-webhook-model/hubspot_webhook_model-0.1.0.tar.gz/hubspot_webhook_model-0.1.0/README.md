# HubSpot web hooks message models

Models for messages that HubSpot sends as web hook calls to your integrations, written as [msgspec](https://jcristharif.com/msgspec/) models.

# Why

It's easier to operate on objects with parsed properties, and the models themselves are missing from [HubSpot client](https://pypi.org/project/hubspot-api-client/).

# How

Incoming messages are lists of events, each of which is either related to a single object or an association between objects.

Message can be parsed with the following code:

```python
import msgspec.json
from hubspot_webhook_model import Message

data: bytes # request body
model = msgspec.json.decode(data, type=Message)
```

Request signatures should be verified using the raw body

# Caveats

1. Messages contain events related to a single event, which can be user action or one of the internal HubSpot mechanisms. They are typically related to a single object, but not always.
2. Events in a message are not ordered. propertyChange enevts may appear before creation events.
3. The model only workds with the new style [generic webhook subscriptions](https://developers.hubspot.com/docs/guides/apps/public-apps/create-generic-webhook-subscriptions).
4. Only small subset of objects is included. Feel free to create Pull Requests with additional models as needed.
