from enum import Enum

class VerificationStatusEnum(Enum):
    PENDING = "Pending"
    REJECTED = "Rejected"
    ACCEPTED = "Accepted"

default_status = VerificationStatusEnum.PENDING

__all__ = ['VerificationStatusEnum', 'default_status']