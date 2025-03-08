from enum import Enum

class VerificationStatusEnum(Enum):
    PENDING = "Pending"
    REJECTED = "Rejected"
    ACCEPTED = "Accepted"

default_status = VerificationStatusEnum.PENDING

class ImageTypeEnum(Enum):
    GROUNDPHOTO = "GroundPhoto"
    AERIALPHOTO = "AerialPhoto"

__all__ = [
    'VerificationStatusEnum',
    'default_status',
    'ImageTypeEnum'
]
