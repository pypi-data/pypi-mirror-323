"""Data models for the Unstructured Platform API."""

from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, UUID4


class PublicSourceConnectorType(str, Enum):
    """Source connector types available in the public API."""
    AZURE = "azure"
    COUCHBASE = "couchbase"
    CONFLUENCE = "confluence"
    DATABRICKS_VOLUMES = "databricks_volumes"
    DROPBOX = "dropbox"
    ELASTICSEARCH = "elasticsearch"
    GCS = "gcs"
    GOOGLE_DRIVE = "google_drive"
    MONGODB = "mongodb"
    ONEDRIVE = "onedrive"
    OUTLOOK = "outlook"
    POSTGRES = "postgres"
    S3 = "s3"
    SALESFORCE = "salesforce"
    SHAREPOINT = "sharepoint"


class PublicDestinationConnectorType(str, Enum):
    """Destination connector types available in the public API."""
    AZURE_AI_SEARCH = "azure_ai_search"
    ASTRADB = "astradb"
    COUCHBASE = "couchbase"
    DATABRICKS_VOLUMES = "databricks_volumes"
    DELTA_TABLE = "delta_table"
    ELASTICSEARCH = "elasticsearch"
    GCS = "gcs"
    MILVUS = "milvus"
    MONGODB = "mongodb"
    PINECONE = "pinecone"
    POSTGRES = "postgres"
    QDRANT_CLOUD = "qdrant-cloud"
    S3 = "s3"
    WEAVIATE = "weaviate"
    ONEDRIVE = "onedrive"


class WorkflowState(str, Enum):
    """Workflow states."""
    ACTIVE = "active"
    INACTIVE = "inactive"


class WorkflowAutoStrategy(str, Enum):
    """Workflow auto-processing strategies."""
    BASIC = "basic"
    ADVANCED = "advanced"
    PLATINUM = "platinum"


class CronTabEntry(BaseModel):
    """Crontab entry for workflow scheduling."""
    cron_expression: str


class WorkflowSchedule(BaseModel):
    """Workflow schedule configuration."""
    crontab_entries: List[CronTabEntry]


class BaseConnector(BaseModel):
    """Base class for connector models."""
    id: UUID4
    name: str
    config: Dict[str, Any]
    created_at: datetime
    updated_at: Optional[datetime] = None


class SourceConnector(BaseConnector):
    """Source connector model."""
    type: PublicSourceConnectorType


class DestinationConnector(BaseConnector):
    """Destination connector model."""
    type: PublicDestinationConnectorType


class JobInformation(BaseModel):
    """Job information model."""
    id: UUID4
    workflow_id: UUID4
    workflow_name: str
    status: str
    created_at: datetime
    runtime: Optional[str] = None


class WorkflowInformation(BaseModel):
    """Workflow information model."""
    id: UUID4
    name: str
    sources: List[UUID4]
    destinations: List[UUID4]
    workflow_type: WorkflowAutoStrategy
    schedule: Optional[WorkflowSchedule] = None
    status: WorkflowState
    created_at: datetime
    updated_at: Optional[datetime] = None
    jobs: List[JobInformation] = [] 