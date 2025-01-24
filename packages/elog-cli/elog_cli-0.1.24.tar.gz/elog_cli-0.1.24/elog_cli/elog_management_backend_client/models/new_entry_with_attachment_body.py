import json
from io import BytesIO
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, File, FileJsonType, Unset

if TYPE_CHECKING:
    from ..models.new_entry_dto import NewEntryDTO


T = TypeVar("T", bound="NewEntryWithAttachmentBody")


@_attrs_define
class NewEntryWithAttachmentBody:
    """
    Attributes:
        entry (NewEntryDTO): Is the model for the new entry creation using name on logbook and tags instead id
        files (Union[Unset, list[File]]):
    """

    entry: "NewEntryDTO"
    files: Union[Unset, list[File]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        entry = self.entry.to_dict()

        files: Union[Unset, list[FileJsonType]] = UNSET
        if not isinstance(self.files, Unset):
            files = []
            for files_item_data in self.files:
                files_item = files_item_data.to_tuple()

                files.append(files_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "entry": entry,
            }
        )
        if files is not UNSET:
            field_dict["files"] = files

        return field_dict

    def to_multipart(self) -> dict[str, Any]:
        entry = (None, json.dumps(self.entry.to_dict()).encode(), "application/json")

        # Prepare the "files" parts: list of tuples with (filename, binary content, content type)
        field_dict: dict[str, Any] = {}
        if not isinstance(self.files, Unset):
            for idx, file_item in enumerate(self.files):
                field_dict["files"] = file_item.to_tuple()

        field_dict: dict[str, Any] = {}
        if not isinstance(self.files, Unset):
            for idx, file_item in enumerate(self.files):
                field_dict["files"] = file_item.to_tuple()

        field_dict.update(
            {
                "entry": entry,
            }
        )
        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.new_entry_dto import NewEntryDTO

        d = src_dict.copy()
        entry = NewEntryDTO.from_dict(d.pop("entry"))

        files = []
        _files = d.pop("files", UNSET)
        for files_item_data in _files or []:
            files_item = File(payload=BytesIO(files_item_data))

            files.append(files_item)

        new_entry_with_attachment_body = cls(
            entry=entry,
            files=files,
        )

        new_entry_with_attachment_body.additional_properties = d
        return new_entry_with_attachment_body

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
