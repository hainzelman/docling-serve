import enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from docling.datamodel.document import ConversionStatus, ErrorItem
from docling.utils.profiling import ProfilingItem
from docling_core.types.doc import DoclingDocument
from docling_jobkit.datamodel.task_meta import TaskProcessingMeta


# Status
class HealthCheckResponse(BaseModel):
    status: str = "ok"


class ClearResponse(BaseModel):
    status: str = "ok"


class DocumentResponse(BaseModel):
    filename: str
    md_content: Optional[str] = None
    json_content: Optional[DoclingDocument] = None
    html_content: Optional[str] = None
    text_content: Optional[str] = None
    doctags_content: Optional[str] = None


class ConvertDocumentResponse(BaseModel):
    document: DocumentResponse
    status: ConversionStatus
    errors: list[ErrorItem] = []
    processing_time: float
    timings: dict[str, ProfilingItem] = {}


class PresignedUrlConvertDocumentResponse(BaseModel):
    status: ConversionStatus
    processing_time: float


class ConvertDocumentErrorResponse(BaseModel):
    status: ConversionStatus


class TaskStatusResponse(BaseModel):
    task_id: str
    task_status: str
    task_position: Optional[int] = None
    task_meta: Optional[TaskProcessingMeta] = None


class MessageKind(str, enum.Enum):
    CONNECTION = "connection"
    UPDATE = "update"
    ERROR = "error"


class WebsocketMessage(BaseModel):
    message: MessageKind
    task: Optional[TaskStatusResponse] = None
    error: Optional[str] = None


class ChunkMetadata(BaseModel):
    """Metadata for a single chunk."""
    start_line: Optional[int] = Field(None, description="Starting line number of the chunk")
    end_line: Optional[int] = Field(None, description="Ending line number of the chunk")
    headers: Optional[List[str]] = Field(None, description="Headers associated with the chunk")
    captions: Optional[List[str]] = Field(None, description="Captions associated with the chunk")
    token_count: Optional[int] = Field(None, description="Number of tokens in the chunk")

class DocumentChunk(BaseModel):
    """A single chunk of a document."""
    text: str = Field(..., description="The chunk text content")
    metadata: ChunkMetadata = Field(default_factory=ChunkMetadata, description="Metadata about the chunk")

class ChunkingResponse(BaseModel):
    """Response model for document chunking."""
    chunks: List[DocumentChunk] = Field(..., description="List of document chunks")
    total_chunks: int = Field(..., description="Total number of chunks")
    method_used: str = Field(..., description="The chunking method that was used")
