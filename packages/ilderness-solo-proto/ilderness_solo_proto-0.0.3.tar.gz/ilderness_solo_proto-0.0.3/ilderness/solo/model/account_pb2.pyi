from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class Account(_message.Message):
    __slots__ = ("accountId", "accountTitle", "createdAt", "balance")
    ACCOUNTID_FIELD_NUMBER: _ClassVar[int]
    ACCOUNTTITLE_FIELD_NUMBER: _ClassVar[int]
    CREATEDAT_FIELD_NUMBER: _ClassVar[int]
    BALANCE_FIELD_NUMBER: _ClassVar[int]
    accountId: int
    accountTitle: str
    createdAt: int
    balance: float
    def __init__(self, accountId: _Optional[int] = ..., accountTitle: _Optional[str] = ..., createdAt: _Optional[int] = ..., balance: _Optional[float] = ...) -> None: ...
