import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

if TYPE_CHECKING:
    from ..models.trigger_extra_property_extra_perms import TriggerExtraPropertyExtraPerms


T = TypeVar("T", bound="TriggerExtraProperty")


@_attrs_define
class TriggerExtraProperty:
    """
    Attributes:
        email (str):
        extra_perms (TriggerExtraPropertyExtraPerms):
        workspace_id (str):
        edited_by (str):
        edited_at (datetime.datetime):
    """

    email: str
    extra_perms: "TriggerExtraPropertyExtraPerms"
    workspace_id: str
    edited_by: str
    edited_at: datetime.datetime
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        email = self.email
        extra_perms = self.extra_perms.to_dict()

        workspace_id = self.workspace_id
        edited_by = self.edited_by
        edited_at = self.edited_at.isoformat()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "email": email,
                "extra_perms": extra_perms,
                "workspace_id": workspace_id,
                "edited_by": edited_by,
                "edited_at": edited_at,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.trigger_extra_property_extra_perms import TriggerExtraPropertyExtraPerms

        d = src_dict.copy()
        email = d.pop("email")

        extra_perms = TriggerExtraPropertyExtraPerms.from_dict(d.pop("extra_perms"))

        workspace_id = d.pop("workspace_id")

        edited_by = d.pop("edited_by")

        edited_at = isoparse(d.pop("edited_at"))

        trigger_extra_property = cls(
            email=email,
            extra_perms=extra_perms,
            workspace_id=workspace_id,
            edited_by=edited_by,
            edited_at=edited_at,
        )

        trigger_extra_property.additional_properties = d
        return trigger_extra_property

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
