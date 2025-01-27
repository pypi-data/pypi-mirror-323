from ilderness.solo.model import account_pb2 as _account_pb2
from ilderness.solo.model import credential_pb2 as _credential_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class AccountRq(_message.Message):
    __slots__ = ("credential",)
    CREDENTIAL_FIELD_NUMBER: _ClassVar[int]
    credential: _credential_pb2.Credential
    def __init__(self, credential: _Optional[_Union[_credential_pb2.Credential, _Mapping]] = ...) -> None: ...

class AccountRs(_message.Message):
    __slots__ = ("account",)
    ACCOUNT_FIELD_NUMBER: _ClassVar[int]
    account: _account_pb2.Account
    def __init__(self, account: _Optional[_Union[_account_pb2.Account, _Mapping]] = ...) -> None: ...
