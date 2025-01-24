from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.search_response_201_sentence_results_json_input_documents_item import (
        SearchResponse201SentenceResultsJsonInputDocumentsItem,
    )


T = TypeVar("T", bound="SearchResponse201SentenceResultsJson")


@_attrs_define
class SearchResponse201SentenceResultsJson:
    """
    Attributes:
        input_documents (Union[Unset, list['SearchResponse201SentenceResultsJsonInputDocumentsItem']]):
        question (Union[Unset, str]):  Example: What is difference between TOC and COD.
        output_text (Union[Unset, str]):  Example: I'm sorry, I don't have enough context to answer this question. Could
            you provide more information about the units and their corresponding breaks?.
    """

    input_documents: Union[Unset, list["SearchResponse201SentenceResultsJsonInputDocumentsItem"]] = UNSET
    question: Union[Unset, str] = UNSET
    output_text: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        input_documents: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.input_documents, Unset):
            input_documents = []
            for input_documents_item_data in self.input_documents:
                input_documents_item = input_documents_item_data.to_dict()
                input_documents.append(input_documents_item)

        question = self.question

        output_text = self.output_text

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if input_documents is not UNSET:
            field_dict["input_documents"] = input_documents
        if question is not UNSET:
            field_dict["question"] = question
        if output_text is not UNSET:
            field_dict["output_text"] = output_text

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.search_response_201_sentence_results_json_input_documents_item import (
            SearchResponse201SentenceResultsJsonInputDocumentsItem,
        )

        d = src_dict.copy()
        input_documents = []
        _input_documents = d.pop("input_documents", UNSET)
        for input_documents_item_data in _input_documents or []:
            input_documents_item = SearchResponse201SentenceResultsJsonInputDocumentsItem.from_dict(
                input_documents_item_data
            )

            input_documents.append(input_documents_item)

        question = d.pop("question", UNSET)

        output_text = d.pop("output_text", UNSET)

        search_response_201_sentence_results_json = cls(
            input_documents=input_documents,
            question=question,
            output_text=output_text,
        )

        search_response_201_sentence_results_json.additional_properties = d
        return search_response_201_sentence_results_json

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
