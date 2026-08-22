"""
Pydantic schema for resume layout/ATS-parsability analysis.
"""
from pydantic import BaseModel


class LayoutAnalysis(BaseModel):
    """
    Structural signals about how likely a resume is to be parsed
    correctly by a real ATS parsing engine - independent of content
    quality. These are the failure modes real ATS systems are known
    to choke on: multi-column layouts, tables, contact info that only
    exists in a header/footer (many ATS strip these before parsing),
    and garbled/non-text content (e.g. a resume that's mostly an
    embedded image).
    """

    multi_column: bool = False
    has_tables: bool = False
    contact_only_in_header_footer: bool = False
    garbled_text_ratio: float = 0.0
    notes: list[str] = []