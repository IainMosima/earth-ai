from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel


class SignedUrlsResponse(BaseModel):
    ground_photo_signed_url: Optional[str]
    aerial_photo_signed_url: Optional[str]

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            ground_photo_signed_url=data["ground_photo_signed_url"],
            aerial_photo_signed_url=data["aerial_photo_signed_url"],
        )


class S3Callback(BaseModel):
    user_id: int
    ground_photo_url: Optional[str]
    ground_photo_key: Optional[str]
    aerial_photo_url: Optional[str]
    aerial_photo_key: Optional[str]
    created_at: datetime = datetime.now(timezone.utc)
    # image_type: Optional[ImageTypeEnum]




#
# class S3signedUrls(BaseModel):
#     """
#     Model for the response from generate_signed_urls function
#     """
#     ground_photo_signed: str
#     aerial_photo_signed: str
#     ground_photo_key: str
#     aerial_photo_key: str
#     user_id: str
#
#     created_at: datetime = datetime.now(timezone.utc)
#
#     @classmethod
#     def from_dict(cls, data: dict) -> "S3signedUrls":
#         return cls(**data)


