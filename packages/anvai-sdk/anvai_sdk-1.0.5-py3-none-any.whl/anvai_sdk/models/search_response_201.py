from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.search_response_201_sentence_results_json import SearchResponse201SentenceResultsJson


T = TypeVar("T", bound="SearchResponse201")


@_attrs_define
class SearchResponse201:
    """
    Attributes:
        sentence_results_json (Union[Unset, SearchResponse201SentenceResultsJson]):
        collection_id (Union[Unset, int]):  Example: 212.
        file_name (Union[Unset, str]):  Example: file2.pdf.
    """

    sentence_results_json: Union[Unset, "SearchResponse201SentenceResultsJson"] = UNSET
    collection_id: Union[Unset, int] = UNSET
    file_name: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        sentence_results_json: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.sentence_results_json, Unset):
            sentence_results_json = self.sentence_results_json.to_dict()

        collection_id = self.collection_id

        file_name = self.file_name

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if sentence_results_json is not UNSET:
            field_dict["sentence_results_json"] = sentence_results_json
        if collection_id is not UNSET:
            field_dict["collection_id"] = collection_id
        if file_name is not UNSET:
            field_dict["file_name"] = file_name

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.search_response_201_sentence_results_json import SearchResponse201SentenceResultsJson

        d = src_dict.copy()
        _sentence_results_json = d.pop("sentence_results_json", UNSET)
        sentence_results_json: Union[Unset, SearchResponse201SentenceResultsJson]
        if isinstance(_sentence_results_json, Unset):
            sentence_results_json = UNSET
        else:
            sentence_results_json = SearchResponse201SentenceResultsJson.from_dict(_sentence_results_json)

        collection_id = d.pop("collection_id", UNSET)

        file_name = d.pop("file_name", UNSET)

        search_response_201 = cls(
            sentence_results_json=sentence_results_json,
            collection_id=collection_id,
            file_name=file_name,
        )

        search_response_201.additional_properties = d
        return search_response_201

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
