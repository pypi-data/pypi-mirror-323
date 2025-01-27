"""Pydantic models representing the OSIS Schema 2.1.1 file standard.

Official OSIS schema reference guide: https://crosswire.org/osis/OSIS%202.1.1%20User%20Manual%2006March2006.pdf
"""

from __future__ import annotations

import datetime
from typing import ClassVar, List, Literal
from typing import Type as TypingType

import pydantic
import pydantic_xml
from pydantic_extra_types import language_code

NSMAP = {
    "": "http://www.bibletechnologies.net/2003/OSIS/namespace",
    "xsi": "http://www.w3.org/2001/XMLSchema-instance",
    "xml": "http://www.w3.org/XML/1998/namespace",
}

# TODO: Implement Milestoneable mixin, so that they are parsed properly


class Milestoneable(pydantic_xml.BaseXmlModel):
    start_id: str = pydantic_xml.attr(name="sID", default="")
    end_id: str = pydantic_xml.attr(name="eID", default="")


class Canonical(pydantic_xml.BaseXmlModel, strict=False):
    canonical: bool | None = pydantic_xml.attr(default=None)

    __canonical_classes__: ClassVar[list[type[Canonical]]] = []

    # TODO: implement inheritance of these values to all child elements
    # TODO: ensure that when serializing and canonical is None, it is not included in the output

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.__canonical_classes__.append(cls)


class A(Canonical, tag="a", nsmap=NSMAP):
    href: str = pydantic_xml.attr()
    content: str = ""


class Abbreviation(Canonical, Milestoneable, tag="abbr", nsmap=NSMAP): ...


class CatchWord(Canonical, tag="catchWord", nsmap=NSMAP): ...


class DivineName(Canonical, tag="divineName", nsmap=NSMAP): ...


class Foreign(Canonical, Milestoneable, tag="foreign", nsmap=NSMAP): ...


class Highlight(Canonical, tag="hi", nsmap=NSMAP): ...


class Index(Canonical, tag="index", nsmap=NSMAP): ...


class Inscription(Canonical, tag="inscription", nsmap=NSMAP): ...


class Mentioned(Canonical, tag="mentioned", nsmap=NSMAP): ...


class Name(Canonical, tag="name", nsmap=NSMAP): ...


class Reading(Canonical, tag="rdg", nsmap=NSMAP): ...


class ReadingGroup(Canonical, tag="rdgGroup", nsmap=NSMAP): ...


class Reference(Canonical, tag="reference", nsmap=NSMAP): ...


class Seg(Canonical, Milestoneable, tag="seg", nsmap=NSMAP): ...


class TransChange(Canonical, tag="transChange", nsmap=NSMAP): ...


class Verse(Canonical, Milestoneable, tag="verse", nsmap=NSMAP):
    osis_id: str = pydantic_xml.attr(name="osisID")
    content: str = ""


class W(Canonical, tag="w", nsmap=NSMAP): ...


class Closer(Canonical, Milestoneable, tag="closer", nsmap=NSMAP): ...


class LineBreak(Canonical, tag="lb", nsmap=NSMAP):
    type: str = pydantic_xml.attr()


class LineGroup(Canonical, Milestoneable, tag="lg", nsmap=NSMAP):
    type: str = pydantic_xml.attr()


class Line(Canonical, Milestoneable, tag="l", nsmap=NSMAP):
    type: Literal["attribution", "doxology", "refrain", "selah"] | str = pydantic_xml.attr()
    level: int = pydantic_xml.attr()


class Head(Canonical, tag="head", nsmap=NSMAP): ...


class Quote(Canonical, Milestoneable, tag="q", nsmap=NSMAP): ...


class Note(Canonical, tag="note", nsmap=NSMAP): ...


class Title(Canonical, tag="title", nsmap=NSMAP):
    content: str
    placement: (
        Literal[
            "leftHead",
            "centerHead",
            "rightHead",
            "insideHead",
            "outsideHead",
            "leftFoot",
            "centerFoot",
            "rightFoot",
            "insideFoot",
            "outsideFoot",
        ]
        | None
    ) = pydantic_xml.attr(default=None)
    type: Literal["main", "sub", "part"] | str | None = pydantic_xml.attr(default=None)
    # TODO: Respect the xml:lang description in section 7.2.1


class Creator(Canonical, tag="creator", nsmap=NSMAP):
    name: str
    role: str | Literal["aut", "edt", "cmm", "trl", "ill"] = pydantic_xml.attr()


class Date(Canonical, tag="date", nsmap=NSMAP):
    event: Literal["edition", "eversion", "imprint", "original"] = pydantic_xml.attr(default="")
    type: Literal["Chinese", "Gregorian", "Islamic", "ISO", "Jewish", "Julian"] = pydantic_xml.attr(default="ISO")
    value: datetime.date | str
    # TODO: Support weekly/monthly/yearly date formats (7.3)

    @pydantic.field_serializer("value")
    def encode_content(self, value: datetime.datetime | str) -> str:
        if isinstance(value, str):
            return value
        return value.isoformat().replace("-", ".")

    @pydantic.field_validator("value", mode="before")
    def decode_content(self, value: str) -> datetime.date | str:
        # OSIS uses "." as a separator, but Python uses "-"
        value = value.replace(".", "-")
        try:
            return datetime.date.fromisoformat(value)
        except ValueError:
            return value


class Language(Canonical, tag="language", nsmap=NSMAP):
    use: Literal[
        "base",
        "didactic",
        "interlinear",
        "original",
        "quotation",
        "source",
        "target",
        "translation",
    ] = pydantic_xml.attr()
    value: language_code.LanguageAlpha2


class Type(Canonical, tag="type", nsmap=NSMAP):
    type: str = pydantic_xml.attr()
    value: str


class Identifier(Canonical, tag="identifier", nsmap=NSMAP):
    type: Literal[
        "DEWEY",
        "DOI",
        "ISBN",
        "ISSN",
        "LCC",
        "LCCN",
        "OSIS",
        "SICI",
        "URI",
        "URL",
        "URN",
    ] = pydantic_xml.attr()
    value: str = pydantic_xml.attr(default="")


class Format(Canonical, tag="format", nsmap=NSMAP):
    type: str = pydantic_xml.attr()
    value: str = pydantic_xml.attr()


class Relation(Canonical, tag="relation", nsmap=NSMAP):
    type: str = pydantic_xml.attr()
    value: str = pydantic_xml.attr()


class Rights(Canonical, tag="rights", nsmap=NSMAP):
    type: str = pydantic_xml.attr()
    value: str = pydantic_xml.attr(default="")


class Subject(Canonical, tag="rights", nsmap=NSMAP):
    type: (
        str
        | Literal[
            "ATLA",
            "BILDI",
            "DBC",
            "DDC",
            "EUT",
            "FGT",
            "LCC",
            "LCSH",
            "MeSH",
            "NLSH",
            "RSWK",
            "SEARS",
            "SOG",
            "SWD_RSWK",
            "UDC",
            "VAT",
        ]
    ) = pydantic_xml.attr()
    value: str = pydantic_xml.attr()
    sources: list[str] = pydantic_xml.element(tag="source")


class Caption(Canonical, tag="caption", nsmap=NSMAP):
    ...
    a_elements: list[A] = pydantic_xml.element(tag="a")
    abbreviations: list[Abbreviation] = pydantic_xml.element(tag="abbr")
    divine_names: list[DivineName] = pydantic_xml.element(tag="divineName")
    foreigns: list[Foreign] = pydantic_xml.element(tag="foreign")
    highlights: list[Highlight] = pydantic_xml.element(tag="hi")
    indices: list[Index] = pydantic_xml.element(tag="index")
    line_breaks: list[LineBreak] = pydantic_xml.element(tag="lb")
    milestones: list[Milestone] = pydantic_xml.element(tag="milestone")
    names: list[Name] = pydantic_xml.element(tag="name")
    notes: list[Note] = pydantic_xml.element(tag="note")
    quotations: list[Quote] = pydantic_xml.element(tag="q")
    references: list[Reference] = pydantic_xml.element(tag="reference")
    segments: list[Seg] = pydantic_xml.element(tag="seg")
    words: list[W] = pydantic_xml.element(tag="w")


class Description(Canonical, tag="description", nsmap=NSMAP): ...


class Publisher(Canonical, tag="publisher", nsmap=NSMAP): ...


class Salute(Canonical, Milestoneable, tag="salute", nsmap=NSMAP): ...


class Signed(Canonical, Milestoneable, tag="signed", nsmap=NSMAP): ...


class Speaker(Canonical, tag="speaker", nsmap=NSMAP): ...


class Speech(Canonical, Milestoneable, tag="speech", nsmap=NSMAP): ...


class Figure(Canonical, tag="figure", nsmap=NSMAP):
    src: str = pydantic_xml.attr()
    alt: str = pydantic_xml.attr()
    captions: list[Caption] = pydantic_xml.element(tag="caption")
    indices: list[Index] = pydantic_xml.element(tag="index")
    notes: list[Note] = pydantic_xml.element(tag="note")


class Milestone(Canonical, tag="milestone", nsmap=NSMAP):
    type: Literal["pb", "column", "Cquote", "header", "footer", "line", "halfLine", "screen"] | str = (
        pydantic_xml.attr()
    )
    marker: str = pydantic_xml.attr()
    n: str = pydantic_xml.attr()


class Paragraph(Canonical, tag="p", nsmap=NSMAP):
    a_elements: list[A] = pydantic_xml.element(default_factory=list)
    abbreviations: list[Abbreviation] = pydantic_xml.element(default_factory=list)
    catch_words: list[CatchWord] = pydantic_xml.element(default_factory=list)
    chapters: list[Chapter] = pydantic_xml.element(default_factory=list)
    closers: list[Closer] = pydantic_xml.element(default_factory=list)
    dates: list[Date] = pydantic_xml.element(default_factory=list)
    divine_names: list[DivineName] = pydantic_xml.element(default_factory=list)
    figures: list[Figure] = pydantic_xml.element(default_factory=list)
    foreigns: list[Foreign] = pydantic_xml.element(default_factory=list)
    highlights: list[Highlight] = pydantic_xml.element(default_factory=list)
    indices: list[Index] = pydantic_xml.element(default_factory=list)
    inscriptions: list[Inscription] = pydantic_xml.element(default_factory=list)
    line_breaks: list[LineBreak] = pydantic_xml.element(default_factory=list)
    line_groups: list[LineGroup] = pydantic_xml.element(default_factory=list)
    lists: list[XmlList] = pydantic_xml.element(default_factory=list)
    mentioned: list[Mentioned] = pydantic_xml.element(default_factory=list)
    milestones: list[Milestone] = pydantic_xml.element(default_factory=list)
    names: list[Name] = pydantic_xml.element(default_factory=list)
    notes: list[Note] = pydantic_xml.element(default_factory=list)
    quotations: list[Quote] = pydantic_xml.element(default_factory=list)
    readings: list[Reading] = pydantic_xml.element(default_factory=list)
    reading_groups: list[ReadingGroup] = pydantic_xml.element(default_factory=list)
    references: list[Reference] = pydantic_xml.element(default_factory=list)
    salutes: list[Salute] = pydantic_xml.element(default_factory=list)
    segments: list[Seg] = pydantic_xml.element(default_factory=list)
    signeds: list[Signed] = pydantic_xml.element(default_factory=list)
    speakers: list[Speaker] = pydantic_xml.element(default_factory=list)
    speeches: list[Speech] = pydantic_xml.element(default_factory=list)
    tables: list[Table] = pydantic_xml.element(default_factory=list)
    titles: list[Title] = pydantic_xml.element(default_factory=list)
    trans_changes: list[TransChange] = pydantic_xml.element(default_factory=list)
    verses: list[Verse] = pydantic_xml.element(default_factory=list)
    words: list[W] = pydantic_xml.element(default_factory=list)


class Work(Canonical, tag="work", nsmap=NSMAP):
    osis_work: str = pydantic_xml.attr(name="osisWork")
    titles: list[Title] = pydantic_xml.element(default_factory=list)
    contributors: list[Creator] = pydantic_xml.element(default_factory=list)
    creators: list[Creator] = pydantic_xml.element(default_factory=list)
    dates: list[Date] = pydantic_xml.element(default_factory=list)
    descriptions: list[Description] = pydantic_xml.element(default_factory=list)
    publisher: list[Publisher] = pydantic_xml.element(default_factory=list)
    type: Type = pydantic_xml.element(default_factory=list)
    subjects: list[Subject] = pydantic_xml.element(default_factory=list)
    formats: list[Format] = pydantic_xml.element(default_factory=list)
    identifiers: list[Identifier] = pydantic_xml.element(default_factory=list)
    sources: list[str] = pydantic_xml.element(tag="source", default_factory=list)
    languages: list[Language] = pydantic_xml.element(default_factory=list)
    relations: list[Relation] = pydantic_xml.element(default_factory=list)
    coverages: list[str] = pydantic_xml.element(tag="coverage", default_factory=list)
    rights: list[Rights] = pydantic_xml.element(default_factory=list)
    # TODO: Implement 7.2.15. Non-Dublin Core Elements and Attributes in the Work Declaration
    scopes: list[str] = pydantic_xml.element(tag="scope", default_factory=list)
    cast_lists: list[str] = pydantic_xml.element(tag="castList", default_factory=list)
    tei_headers: list[str] = pydantic_xml.element(tag="teiHeader", default_factory=list)
    ref_systems: list[str] = pydantic_xml.element(tag="refSystem", default_factory=list)


class WorkPrefix(Canonical, tag="workPrefix", nsmap=NSMAP):
    path: str = pydantic_xml.attr()
    osis_work: str = pydantic_xml.attr(name="osisWork")


class RevisionDesc(Canonical, tag="revisionDesc", nsmap=NSMAP):
    # TODO: enforce yyyy.mm.ddThh.mm.ss format, where Thh.mm.ss is optional
    date: datetime.datetime = pydantic_xml.element(tag="date")
    paragraphs: list[Paragraph] = pydantic_xml.element(default_factory=list)
    resp: str = pydantic_xml.attr()

    @pydantic.field_serializer("date")
    def encode_content(self, value: datetime.datetime | str) -> str:
        if isinstance(value, str):
            return value
        return value.isoformat().replace("-", ".")

    @pydantic.field_validator("date", mode="before")
    def decode_content(self, value: str | datetime.datetime) -> datetime.datetime | str:
        # OSIS uses "." as a separator, but Python uses "-"
        if isinstance(value, datetime.datetime):
            return value
        value = value.replace(".", "-")
        try:
            return datetime.datetime.fromisoformat(value)
        except ValueError:
            return value


class Header(Canonical, tag="header", nsmap=NSMAP):
    revision_desc: list[RevisionDesc] = pydantic_xml.element()
    work: list[Work] = pydantic_xml.element()
    work_prefix: list[WorkPrefix] = pydantic_xml.element()


class TitlePage(Canonical, tag="titlePage", nsmap=NSMAP):
    contributors: list[Creator] = pydantic_xml.element()
    coverages: list[str] = pydantic_xml.element(tag="coverage")
    creators: list[Creator] = pydantic_xml.element()
    dates: list[Date] = pydantic_xml.element()
    descriptions: list[Description] = pydantic_xml.element()
    figures: list[Figure] = pydantic_xml.element()
    formats: list[Format] = pydantic_xml.element()
    identifiers: list[Identifier] = pydantic_xml.element()
    languages: list[Language] = pydantic_xml.element()
    milestones: list[Milestone] = pydantic_xml.element()
    paragraphs: list[Paragraph] = pydantic_xml.element()
    publishers: list[Publisher] = pydantic_xml.element()
    relations: list[Relation] = pydantic_xml.element()
    sources: list[str] = pydantic_xml.element(tag="source")
    subjects: list[Subject] = pydantic_xml.element()
    titles: list[Title] = pydantic_xml.element()
    type: Type = pydantic_xml.element()


class Item(Canonical, tag="item", nsmap=NSMAP):
    content: str = ""
    role: str = pydantic_xml.attr()
    a_elements: list[A] = pydantic_xml.element()
    abbreviations: list[Abbreviation] = pydantic_xml.element()
    dates: list[Date] = pydantic_xml.element()
    divine_names: list[DivineName] = pydantic_xml.element()
    foreigns: list[Foreign] = pydantic_xml.element()
    highlights: list[Highlight] = pydantic_xml.element()
    indices: list[Index] = pydantic_xml.element()
    line_breaks: list[LineBreak] = pydantic_xml.element()
    milestones: list[Milestone] = pydantic_xml.element()
    names: list[Name] = pydantic_xml.element()
    notes: list[Note] = pydantic_xml.element()
    quotations: list[Quote] = pydantic_xml.element()
    references: list[Reference] = pydantic_xml.element()
    segments: list[Seg] = pydantic_xml.element()
    titles: list[Title] = pydantic_xml.element()
    trans_changes: list[TransChange] = pydantic_xml.element()
    verses: list[Verse] = pydantic_xml.element()
    words: list[W] = pydantic_xml.element()


class Label(Canonical, tag="label", nsmap=NSMAP):
    content: str = ""
    role: str = pydantic_xml.attr()
    a_elements: list[A] = pydantic_xml.element()
    abbreviations: list[Abbreviation] = pydantic_xml.element()
    dates: list[Date] = pydantic_xml.element()
    divine_names: list[DivineName] = pydantic_xml.element()
    foreigns: list[Foreign] = pydantic_xml.element()
    highlights: list[Highlight] = pydantic_xml.element()
    indices: list[Index] = pydantic_xml.element()
    line_breaks: list[LineBreak] = pydantic_xml.element()
    milestones: list[Milestone] = pydantic_xml.element()
    names: list[Name] = pydantic_xml.element()
    notes: list[Note] = pydantic_xml.element()
    quotations: list[Quote] = pydantic_xml.element()
    references: list[Reference] = pydantic_xml.element()
    segments: list[Seg] = pydantic_xml.element()
    trans_changes: list[TransChange] = pydantic_xml.element()
    words: list[W] = pydantic_xml.element()


class XmlList(Canonical, tag="list", nsmap=NSMAP):
    type: str = pydantic_xml.attr()
    chapters: list[Chapter] = pydantic_xml.element()
    heads: list[Head] = pydantic_xml.element()
    indices: list[Index] = pydantic_xml.element()
    items: list[Item] = pydantic_xml.element()
    line_breaks: list[LineBreak] = pydantic_xml.element()
    lists: list[XmlList] = pydantic_xml.element()
    milestones: list[Milestone] = pydantic_xml.element()
    quotations: list[Quote] = pydantic_xml.element()
    verses: list[Verse] = pydantic_xml.element()


class Cell(Canonical, tag="cell", nsmap=NSMAP):
    align: Literal["left", "right", "center", "justify", "start", "end"] = pydantic_xml.attr()
    content: str  # TODO: Support parsing arbitrary content


class Row(Canonical, tag="row", nsmap=NSMAP):
    type: Literal["label", "data"] = pydantic_xml.attr()
    cells: list[Cell] = pydantic_xml.element(tag="cell")


class Table(Canonical, tag="table", nsmap=NSMAP):
    num_columns: int = pydantic_xml.attr(name="cols")
    num_rows: int = pydantic_xml.attr(name="rows")

    heads: list[Head] = pydantic_xml.element(default_factory=list)
    rows: list[Row] = pydantic_xml.element(default_factory=list)


class Div(Canonical, tag="div", nsmap=NSMAP):
    content: str = ""
    type: (
        Literal[
            "afterword",
            "annotant",
            "appendix",
            "article",
            "back",
            "bibliography",
            "body",
            "book",
            "bookGroup",
            "bridge",
            "chapter",
            "colophon",
            "commentary",
            "concordance",
            "coverPage",
            "dedication",
            "devotional",
            "entry",
            "front",
            "gazetteer",
            "glossary",
            "imprimatur",
            "index",
            "introduction",
            "majorSection",
            "map",
            "outline",
            "paragraph",
            "part",
            "preface",
            "publicationData",
            "section",
            "subSection",
            "summary",
            "tableofContents",
            "titlePage",
        ]
        | str
    ) = pydantic_xml.attr()
    scope: str = pydantic_xml.attr(default="")
    heads: list[Head] = pydantic_xml.element(default_factory=list)
    a_elements: list[A] = pydantic_xml.element(default_factory=list)
    abbrevations: list[Abbreviation] = pydantic_xml.element(default_factory=list)
    chapters: list[Chapter] = pydantic_xml.element(default_factory=list)
    closers: list[Closer] = pydantic_xml.element(default_factory=list)
    dates: list[Date] = pydantic_xml.element(default_factory=list)
    divs: list[Div] = pydantic_xml.element(default_factory=list)
    divine_names: list[DivineName] = pydantic_xml.element(default_factory=list)
    figures: list[Figure] = pydantic_xml.element(default_factory=list)
    foreigns: list[Foreign] = pydantic_xml.element(default_factory=list)
    highlights: list[Highlight] = pydantic_xml.element(default_factory=list)
    indices: list[Index] = pydantic_xml.element(default_factory=list)
    inscriptions: list[Inscription] = pydantic_xml.element(default_factory=list)
    line_breaks: list[LineBreak] = pydantic_xml.element(default_factory=list)
    line_groups: list[LineGroup] = pydantic_xml.element(default_factory=list)
    lists: list[XmlList] = pydantic_xml.element(default_factory=list)
    mentioned: list[Mentioned] = pydantic_xml.element(default_factory=list)
    names: list[Name] = pydantic_xml.element(default_factory=list)
    notes: list[Note] = pydantic_xml.element(default_factory=list)
    paragraphs: list[Paragraph] = pydantic_xml.element(default_factory=list)
    quotations: list[Quote] = pydantic_xml.element(default_factory=list)
    references: list[Reference] = pydantic_xml.element(default_factory=list)
    salute: list[Salute] = pydantic_xml.element(default_factory=list)
    segments: list[Seg] = pydantic_xml.element(default_factory=list)
    signeds: list[Signed] = pydantic_xml.element(default_factory=list)
    speakers: list[Speaker] = pydantic_xml.element(default_factory=list)
    speeches: list[Speech] = pydantic_xml.element(default_factory=list)
    tables: list[Table] = pydantic_xml.element(default_factory=list)
    titles: list[Title] = pydantic_xml.element(default_factory=list)
    trans_changes: list[TransChange] = pydantic_xml.element(default_factory=list)
    verses: list[Verse] = pydantic_xml.element(default_factory=list)
    words: list[W] = pydantic_xml.element(default_factory=list)

    @pydantic.model_validator(mode="after")
    def validate_content(self) -> Div:
        """Validate that a div element only contains chapters if it is a book div."""
        if self.type != "book" and self.chapters:
            raise ValueError("Only a book div can contain chapters.")
        return self


class Chapter(Canonical, Milestoneable, tag="chapter", nsmap=NSMAP):
    content: str = ""
    chapter_title: str = pydantic_xml.attr(default="")
    heads: list[Head] = pydantic_xml.element(default_factory=list)
    a_elements: list[A] = pydantic_xml.element(default_factory=list)
    abbrevations: list[Abbreviation] = pydantic_xml.element(default_factory=list)
    closers: list[Closer] = pydantic_xml.element(default_factory=list)
    dates: list[Date] = pydantic_xml.element(default_factory=list)
    divs: list[Div] = pydantic_xml.element(default_factory=list)
    divine_names: list[DivineName] = pydantic_xml.element(default_factory=list)
    figures: list[Figure] = pydantic_xml.element(default_factory=list)
    foreigns: list[Foreign] = pydantic_xml.element(default_factory=list)
    highlights: list[Highlight] = pydantic_xml.element(default_factory=list)
    indices: list[Index] = pydantic_xml.element(default_factory=list)
    inscriptions: list[Inscription] = pydantic_xml.element(default_factory=list)
    line_breaks: list[LineBreak] = pydantic_xml.element(default_factory=list)
    line_groups: list[LineGroup] = pydantic_xml.element(default_factory=list)
    lists: list[XmlList] = pydantic_xml.element(default_factory=list)
    mentioned: list[Mentioned] = pydantic_xml.element(default_factory=list)
    names: list[Name] = pydantic_xml.element(default_factory=list)
    notes: list[Note] = pydantic_xml.element(default_factory=list)
    paragraphs: list[Paragraph] = pydantic_xml.element(default_factory=list)
    quotations: list[Quote] = pydantic_xml.element(default_factory=list)
    references: list[Reference] = pydantic_xml.element(default_factory=list)
    salute: list[Salute] = pydantic_xml.element(default_factory=list)
    segments: list[Seg] = pydantic_xml.element(default_factory=list)
    signeds: list[Signed] = pydantic_xml.element(default_factory=list)
    speakers: list[Speaker] = pydantic_xml.element(default_factory=list)
    speeches: list[Speech] = pydantic_xml.element(default_factory=list)
    tables: list[Table] = pydantic_xml.element(default_factory=list)
    titles: list[Title] = pydantic_xml.element(default_factory=list)
    trans_changes: list[TransChange] = pydantic_xml.element(default_factory=list)
    verses: list[Verse] = pydantic_xml.element(default_factory=list)
    words: list[W] = pydantic_xml.element(default_factory=list)


class OsisText(Canonical, tag="osisText", nsmap=NSMAP):
    """The root element of an OSIS XML document."""

    osis_id_work: str = pydantic_xml.attr(name="osisIDWork")
    osis_ref_work: str | None = pydantic_xml.attr(name="osisRefWork", default=None)
    xml_lang: language_code.LanguageAlpha2 | None = pydantic_xml.attr(name="lang", ns="xml")
    headers: list[Header] = pydantic_xml.element(default_factory=list)
    title_pages: list[TitlePage] = pydantic_xml.element(default_factory=list)
    divs: list[Div] = pydantic_xml.element(default_factory=list)


class Osis(Canonical, tag="osis", nsmap=NSMAP):
    title_pages: list[TitlePage] = pydantic_xml.element(default_factory=list)
    osis_text: OsisText = pydantic_xml.element()


# Some of the models are mutually recursive, so we need to rebuild them after they are all defined
for cls in Canonical.__canonical_classes__:
    cls.model_rebuild()
