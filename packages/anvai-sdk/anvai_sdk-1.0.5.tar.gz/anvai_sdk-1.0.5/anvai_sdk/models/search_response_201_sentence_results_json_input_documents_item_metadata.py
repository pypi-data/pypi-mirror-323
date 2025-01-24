from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="SearchResponse201SentenceResultsJsonInputDocumentsItemMetadata")


@_attrs_define
class SearchResponse201SentenceResultsJsonInputDocumentsItemMetadata:
    """
    Attributes:
        source (Union[Unset, str]):  Example: file2.pdf.
        file_path (Union[Unset, str]):  Example: file2.pdf.
        page (Union[Unset, int]):  Example: 2.
        total_pages (Union[Unset, int]):  Example: 4.
        format_ (Union[Unset, str]):  Example: PDF 1.4.
        title (Union[Unset, str]):  Example: Prompt Library.
        author (Union[Unset, str]):
        subject (Union[Unset, str]):
        keywords (Union[Unset, str]):
        creator (Union[Unset, str]):
        producer (Union[Unset, str]):  Example: Skia/PDF m130 Google Docs Renderer.
        creation_date (Union[Unset, str]):
        mod_date (Union[Unset, str]):
        trapped (Union[Unset, str]):
        tenant_id (Union[Unset, int]):  Example: 1.
        collection_id (Union[Unset, int]):  Example: 212.
        collection_name (Union[Unset, str]):  Example: test collection from sdk.
        file_name (Union[Unset, str]):  Example: file2.pdf.
    """

    source: Union[Unset, str] = UNSET
    file_path: Union[Unset, str] = UNSET
    page: Union[Unset, int] = UNSET
    total_pages: Union[Unset, int] = UNSET
    format_: Union[Unset, str] = UNSET
    title: Union[Unset, str] = UNSET
    author: Union[Unset, str] = UNSET
    subject: Union[Unset, str] = UNSET
    keywords: Union[Unset, str] = UNSET
    creator: Union[Unset, str] = UNSET
    producer: Union[Unset, str] = UNSET
    creation_date: Union[Unset, str] = UNSET
    mod_date: Union[Unset, str] = UNSET
    trapped: Union[Unset, str] = UNSET
    tenant_id: Union[Unset, int] = UNSET
    collection_id: Union[Unset, int] = UNSET
    collection_name: Union[Unset, str] = UNSET
    file_name: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        source = self.source

        file_path = self.file_path

        page = self.page

        total_pages = self.total_pages

        format_ = self.format_

        title = self.title

        author = self.author

        subject = self.subject

        keywords = self.keywords

        creator = self.creator

        producer = self.producer

        creation_date = self.creation_date

        mod_date = self.mod_date

        trapped = self.trapped

        tenant_id = self.tenant_id

        collection_id = self.collection_id

        collection_name = self.collection_name

        file_name = self.file_name

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if source is not UNSET:
            field_dict["source"] = source
        if file_path is not UNSET:
            field_dict["file_path"] = file_path
        if page is not UNSET:
            field_dict["page"] = page
        if total_pages is not UNSET:
            field_dict["total_pages"] = total_pages
        if format_ is not UNSET:
            field_dict["format"] = format_
        if title is not UNSET:
            field_dict["title"] = title
        if author is not UNSET:
            field_dict["author"] = author
        if subject is not UNSET:
            field_dict["subject"] = subject
        if keywords is not UNSET:
            field_dict["keywords"] = keywords
        if creator is not UNSET:
            field_dict["creator"] = creator
        if producer is not UNSET:
            field_dict["producer"] = producer
        if creation_date is not UNSET:
            field_dict["creationDate"] = creation_date
        if mod_date is not UNSET:
            field_dict["modDate"] = mod_date
        if trapped is not UNSET:
            field_dict["trapped"] = trapped
        if tenant_id is not UNSET:
            field_dict["tenant_id"] = tenant_id
        if collection_id is not UNSET:
            field_dict["collection_id"] = collection_id
        if collection_name is not UNSET:
            field_dict["collection_name"] = collection_name
        if file_name is not UNSET:
            field_dict["file_name"] = file_name

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        source = d.pop("source", UNSET)

        file_path = d.pop("file_path", UNSET)

        page = d.pop("page", UNSET)

        total_pages = d.pop("total_pages", UNSET)

        format_ = d.pop("format", UNSET)

        title = d.pop("title", UNSET)

        author = d.pop("author", UNSET)

        subject = d.pop("subject", UNSET)

        keywords = d.pop("keywords", UNSET)

        creator = d.pop("creator", UNSET)

        producer = d.pop("producer", UNSET)

        creation_date = d.pop("creationDate", UNSET)

        mod_date = d.pop("modDate", UNSET)

        trapped = d.pop("trapped", UNSET)

        tenant_id = d.pop("tenant_id", UNSET)

        collection_id = d.pop("collection_id", UNSET)

        collection_name = d.pop("collection_name", UNSET)

        file_name = d.pop("file_name", UNSET)

        search_response_201_sentence_results_json_input_documents_item_metadata = cls(
            source=source,
            file_path=file_path,
            page=page,
            total_pages=total_pages,
            format_=format_,
            title=title,
            author=author,
            subject=subject,
            keywords=keywords,
            creator=creator,
            producer=producer,
            creation_date=creation_date,
            mod_date=mod_date,
            trapped=trapped,
            tenant_id=tenant_id,
            collection_id=collection_id,
            collection_name=collection_name,
            file_name=file_name,
        )

        search_response_201_sentence_results_json_input_documents_item_metadata.additional_properties = d
        return search_response_201_sentence_results_json_input_documents_item_metadata

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
