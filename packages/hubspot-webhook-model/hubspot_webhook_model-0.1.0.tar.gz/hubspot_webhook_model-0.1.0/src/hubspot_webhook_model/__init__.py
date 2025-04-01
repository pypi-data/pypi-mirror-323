from typing import Optional, Union

import msgspec


class Event(
    msgspec.Struct,
    frozen=True,
    forbid_unknown_fields=True,
    rename="camel",
    tag_field="subscriptionType",
):  # type: ignore[call-arg]
    app_id: int
    attempt_number: int
    change_source: str
    event_id: int
    occurred_at: int
    portal_id: int
    subscription_id: int

    # object.creation and object.associationChange events
    source_id: Optional[str] = None


class CRUDEvent(
    Event, frozen=True, forbid_unknown_fields=True, rename="camel", kw_only=True
):  # type: ignore[call-arg]
    object_id: int
    object_type_id: str


class Change(
    CRUDEvent, frozen=True, forbid_unknown_fields=True, rename="camel", kw_only=True
):  # type: ignore[call-arg]
    change_flag: str


class Creation(
    Change,
    frozen=True,
    forbid_unknown_fields=True,
    rename="camel",
    tag="object.creation",
):  # type: ignore[call-arg]
    pass


class AssociationChange(
    Event,
    tag="object.associationChange",
    frozen=True,
    forbid_unknown_fields=True,
    rename="camel",
    kw_only=True,
):  # type: ignore[call-arg]
    association_category: str
    association_removed: bool
    association_type: str
    association_type_id: int
    from_object_id: int
    from_object_type_id: str
    is_primary_association: bool
    to_object_id: int
    to_object_type_id: str


class PropertyChange(
    CRUDEvent,
    tag="object.propertyChange",
    frozen=True,
    forbid_unknown_fields=True,
    rename="camel",
    kw_only=True,
):  # type: ignore[call-arg]
    is_sensitive: bool
    property_name: str
    property_value: Union[str, int, float, bool]
    """The new value of the property or an empty string when the property is cleared"""


class Deletion(
    Change,
    tag="object.deletion",
    frozen=True,
    forbid_unknown_fields=True,
    rename="camel",
    kw_only=True,
):  # type: ignore[call-arg]
    pass


Event_ = Union[Creation, PropertyChange, AssociationChange, Deletion]
Message = list[Event_]
