from typing import Optional
from pydantic import BaseModel

from savant_models.user_management_models.models.tab_permissions import TabPermissions


class UserPrivileges(BaseModel):
    batches: Optional[TabPermissions] = TabPermissions()
    projects: Optional[TabPermissions] = TabPermissions()
    admin: Optional[TabPermissions] = TabPermissions()
    file_uploads: Optional[TabPermissions] = TabPermissions()
    labels: Optional[TabPermissions] = TabPermissions()
    profiles: Optional[TabPermissions] = TabPermissions()
    videos: Optional[TabPermissions] = TabPermissions()
