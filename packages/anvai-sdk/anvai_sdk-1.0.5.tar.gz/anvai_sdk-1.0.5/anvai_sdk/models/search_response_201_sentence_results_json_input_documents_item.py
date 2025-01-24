from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.search_response_201_sentence_results_json_input_documents_item_metadata import (
        SearchResponse201SentenceResultsJsonInputDocumentsItemMetadata,
    )


T = TypeVar("T", bound="SearchResponse201SentenceResultsJsonInputDocumentsItem")


@_attrs_define
class SearchResponse201SentenceResultsJsonInputDocumentsItem:
    """
    Attributes:
        id (Union[Unset, str]):  Example: None.
        metadata (Union[Unset, SearchResponse201SentenceResultsJsonInputDocumentsItemMetadata]):
        page_content (Union[Unset, str]):  Example: Also, suggest student breaks for each of the above units..
        type_ (Union[Unset, str]):  Example: Document.
    """

    id: Union[Unset, str] = UNSET
    metadata: Union[Unset, "SearchResponse201SentenceResultsJsonInputDocumentsItemMetadata"] = UNSET
    page_content: Union[Unset, str] = UNSET
    type_: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        metadata: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.metadata, Unset):
            metadata = self.metadata.to_dict()

        page_content = self.page_content

        type_ = self.type_

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if metadata is not UNSET:
            field_dict["metadata"] = metadata
        if page_content is not UNSET:
            field_dict["page_content"] = page_content
        if type_ is not UNSET:
            field_dict["type"] = type_

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.search_response_201_sentence_results_json_input_documents_item_metadata import (
            SearchResponse201SentenceResultsJsonInputDocumentsItemMetadata,
        )

        d = src_dict.copy()
        id = d.pop("id", UNSET)

        _metadata = d.pop("metadata", UNSET)
        metadata: Union[Unset, SearchResponse201SentenceResultsJsonInputDocumentsItemMetadata]
        if isinstance(_metadata, Unset):
            metadata = UNSET
        else:
            metadata = SearchResponse201SentenceResultsJsonInputDocumentsItemMetadata.from_dict(_metadata)

        page_content = d.pop("page_content", UNSET)

        type_ = d.pop("type", UNSET)

        search_response_201_sentence_results_json_input_documents_item = cls(
            id=id,
            metadata=metadata,
            page_content=page_content,
            type_=type_,
        )

        search_response_201_sentence_results_json_input_documents_item.additional_properties = d
        return search_response_201_sentence_results_json_input_documents_item

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
