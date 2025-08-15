from typing import Generic, TypeVar, Optional
from pydantic import BaseModel, ConfigDict

T = TypeVar("T")
 
class ApiResponse(BaseModel, Generic[T]):
	success: bool = True
	data: Optional[T] = None
	message: Optional[str] = None
	error: Optional[str] = None
	details: Optional[dict] = None

class PaginationParams(BaseModel):
    page: int = 1
    size: int = 10
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "page": 1,
                "size": 10
            }
        }
    )
    
    def validate_page_size(self):
        if self.page < 1:
            self.page = 1
        if self.size < 1:
            self.size = 1
        elif self.size > 20:
            self.size = 20

class PaginationMeta(BaseModel):
    page: int
    size: int
    total: int
    total_pages: int
    has_next: bool
    has_previous: bool
    
    @classmethod
    def create(cls, page: int, size: int, total: int):
        total_pages = (total + size - 1) // size 
        return cls(
            page=page,
            size=size,
            total=total,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_previous=page > 1
        )

class PaginatedResponse(BaseModel, Generic[T]):
    data: list[T]
    meta: PaginationMeta 