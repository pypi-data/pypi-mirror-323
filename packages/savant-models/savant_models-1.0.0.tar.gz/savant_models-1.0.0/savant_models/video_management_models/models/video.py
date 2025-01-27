from datetime import datetime
from typing import List, Optional

from pydantic import ConfigDict, BaseModel, Field

from savant_models.video_management_models.models.deframer_job import DeframerJob
from savant_models.video_management_models.enums.video_source import VideoSource
from savant_models.video_management_models.models.ada_metadata import AdaMetadata
from savant_models.video_management_models.models.video_registry_annotations import VideoRegistryAnnotations

class Video(BaseModel):
    id: str = Field(alias="_id")
    name: str
    annotations: Optional[VideoRegistryAnnotations] = VideoRegistryAnnotations()
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    duration: Optional[int] = None
    surgeon_code: Optional[str] = None
    institution_code: Optional[str] = None
    device_uuid: Optional[str] = None
    path_to_mp4: Optional[str] = None
    path_to_hls: Optional[str] = None
    video_tags: Optional[List[dict]] = None
    medical_code: Optional[str] = None
    ada_metadata: Optional[AdaMetadata] = None
    linked_video_id: Optional[str] = None
    stereo_calibration_path: Optional[str] = None
    datetime_ingested: Optional[datetime] = None
    deframer_jobs: Optional[List[DeframerJob]] = []
    source: Optional[VideoSource] = None

    model_config = ConfigDict(populate_by_name=True)