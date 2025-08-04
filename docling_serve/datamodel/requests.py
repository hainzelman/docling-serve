from enum import Enum
from typing import Annotated, Literal, Optional

from pydantic import BaseModel, Field, model_validator
from pydantic_core import PydanticCustomError
from typing_extensions import Self

from docling_jobkit.datamodel.http_inputs import FileSource, HttpSource
from docling_jobkit.datamodel.s3_coords import S3Coordinates
from docling_jobkit.datamodel.task_targets import (
    InBodyTarget,
    S3Target,
    TaskTarget,
    ZipTarget,
)

from docling_serve.datamodel.convert import ConvertDocumentsRequestOptions
from docling_serve.settings import AsyncEngine, docling_serve_settings

## Sources


class FileSourceRequest(FileSource):
    kind: Literal["file"] = "file"


class HttpSourceRequest(HttpSource):
    kind: Literal["http"] = "http"


class S3SourceRequest(S3Coordinates):
    kind: Literal["s3"] = "s3"


## Multipart targets
class TargetName(str, Enum):
    INBODY = InBodyTarget().kind
    ZIP = ZipTarget().kind


## Aliases
SourceRequestItem = Annotated[
    FileSourceRequest | HttpSourceRequest | S3SourceRequest, Field(discriminator="kind")
]


## Complete Source request
class ConvertDocumentsRequest(BaseModel):
    options: ConvertDocumentsRequestOptions = ConvertDocumentsRequestOptions()
    sources: list[SourceRequestItem]
    target: TaskTarget = InBodyTarget()

    @model_validator(mode="after")
    def validate_s3_source_and_target(self) -> Self:
        for source in self.sources:
            if isinstance(source, S3SourceRequest):
                if docling_serve_settings.eng_kind != AsyncEngine.KFP:
                    raise PydanticCustomError(
                        "error source", 'source kind "s3" requires engine kind "KFP"'
                    )
                if self.target.kind != "s3":
                    raise PydanticCustomError(
                        "error source", 'source kind "s3" requires target kind "s3"'
                    )
        if isinstance(self.target, S3Target):
            for source in self.sources:
                if isinstance(source, S3SourceRequest):
                    return self
            raise PydanticCustomError(
                "error target", 'target kind "s3" requires source kind "s3"'
            )
        return self


class ChunkingMethod(str, Enum):
    HYBRID = "hybrid"
    HIERARCHICAL = "hierarchical"

class ChunkingRequest(BaseModel):
    """Request model for document chunking."""
    method: ChunkingMethod = Field(
        default=ChunkingMethod.HYBRID,
        description="The chunking method to use"
    )
    merge_list_items: Optional[bool] = Field(
        default=True,
        description="Whether to merge list items in hierarchical chunking"
    )
    merge_peers: Optional[bool] = Field(
        default=True,
        description="Whether to merge undersized successive chunks with same headings & captions in hybrid chunking"
    )
    max_tokens: Optional[int] = Field(
        default=512,
        description="Maximum number of tokens per chunk for hybrid chunking"
    )

class Base64FileSource(BaseModel):
    """A file source with base64-encoded content."""
    kind: Literal["file"] = "file"
    base64_string: str = Field(..., description="Base64-encoded file content")
    filename: str = Field(..., description="Original filename")

class PictureDescriptionOptions(BaseModel):
    """Options for picture description enrichment."""
    enabled: bool = Field(
        default=False,
        description="Whether to enable picture description"
    )
    repo_id: str = Field(
        default="HuggingFaceTB/SmolVLM-256M-Instruct",
        description="The model repository ID to use for picture description"
    )
    prompt: str = Field(
        default="Describe this picture in three to five sentences. Be precise and concise.",
        description="The prompt to use for picture description"
    )
    images_scale: int = Field(
        default=2,
        description="Scale factor for image processing"
    )

class OcrOptions(BaseModel):
    """Options for OCR processing."""
    enabled: bool = Field(
        default=False,
        description="Whether to enable OCR processing"
    )
    ocr_languages: Optional[list[str]] = Field(
        default=None,
        description="List of languages to use for OCR (e.g. ['eng', 'fra']). If None, will try to auto-detect."
    )
    dpi: Optional[int] = Field(
        default=None,
        description="DPI to use for OCR processing. Higher values may improve accuracy but increase processing time."
    )

class ChunkingSourceRequest(BaseModel):
    """Request model for document chunking with base64 support."""
    sources: list[Base64FileSource]
    method: ChunkingMethod = Field(
        default=ChunkingMethod.HYBRID,
        description="The chunking method to use"
    )
    merge_list_items: Optional[bool] = Field(
        default=True,
        description="Whether to merge list items in hierarchical chunking"
    )
    merge_peers: Optional[bool] = Field(
        default=True,
        description="Whether to merge undersized successive chunks with same headings & captions in hybrid chunking"
    )
    max_tokens: Optional[int] = Field(
        default=512,
        description="Maximum number of tokens per chunk for hybrid chunking"
    )
    picture_description: Optional[PictureDescriptionOptions] = Field(
        default=None,
        description="Options for picture description enrichment"
    )
    ocr: Optional[OcrOptions] = Field(
        default=None,
        description="Options for OCR processing"
    )
