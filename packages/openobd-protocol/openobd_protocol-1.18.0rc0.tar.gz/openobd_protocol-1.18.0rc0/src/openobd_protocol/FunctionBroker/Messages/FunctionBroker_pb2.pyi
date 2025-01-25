from openobd_protocol.SessionController.Messages import SessionController_pb2 as _SessionController_pb2
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class FunctionUpdateResponse(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    FUNCTION_UPDATE_UNDEFINED: _ClassVar[FunctionUpdateResponse]
    FUNCTION_UPDATE_SUCCESS: _ClassVar[FunctionUpdateResponse]
    FUNCTION_UPDATE_FAILED: _ClassVar[FunctionUpdateResponse]
    FUNCTION_UPDATE_UNAVAILABLE: _ClassVar[FunctionUpdateResponse]
    FUNCTION_UPDATE_UNAUTHORIZED: _ClassVar[FunctionUpdateResponse]

class FunctionUpdateType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    FUNCTION_UPDATE_TYPE_UNDEFINED: _ClassVar[FunctionUpdateType]
    FUNCTION_UPDATE_TYPE_REQUEST: _ClassVar[FunctionUpdateType]
    FUNCTION_UPDATE_TYPE_RESPONSE: _ClassVar[FunctionUpdateType]
    FUNCTION_UPDATE_TYPE_PING: _ClassVar[FunctionUpdateType]

class FunctionRegistrationState(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    FUNCTION_REGISTRATION_STATE_UNDEFINED: _ClassVar[FunctionRegistrationState]
    FUNCTION_REGISTRATION_STATE_ONLINE: _ClassVar[FunctionRegistrationState]
    FUNCTION_REGISTRATION_STATE_OFFLINE: _ClassVar[FunctionRegistrationState]
    FUNCTION_REGISTRATION_STATE_UNAVAILABLE: _ClassVar[FunctionRegistrationState]
FUNCTION_UPDATE_UNDEFINED: FunctionUpdateResponse
FUNCTION_UPDATE_SUCCESS: FunctionUpdateResponse
FUNCTION_UPDATE_FAILED: FunctionUpdateResponse
FUNCTION_UPDATE_UNAVAILABLE: FunctionUpdateResponse
FUNCTION_UPDATE_UNAUTHORIZED: FunctionUpdateResponse
FUNCTION_UPDATE_TYPE_UNDEFINED: FunctionUpdateType
FUNCTION_UPDATE_TYPE_REQUEST: FunctionUpdateType
FUNCTION_UPDATE_TYPE_RESPONSE: FunctionUpdateType
FUNCTION_UPDATE_TYPE_PING: FunctionUpdateType
FUNCTION_REGISTRATION_STATE_UNDEFINED: FunctionRegistrationState
FUNCTION_REGISTRATION_STATE_ONLINE: FunctionRegistrationState
FUNCTION_REGISTRATION_STATE_OFFLINE: FunctionRegistrationState
FUNCTION_REGISTRATION_STATE_UNAVAILABLE: FunctionRegistrationState

class FunctionBrokerToken(_message.Message):
    __slots__ = ("value",)
    VALUE_FIELD_NUMBER: _ClassVar[int]
    value: str
    def __init__(self, value: _Optional[str] = ...) -> None: ...

class FunctionUpdate(_message.Message):
    __slots__ = ("type", "function_registration", "function_call", "function_broker_token", "response", "response_description")
    TYPE_FIELD_NUMBER: _ClassVar[int]
    FUNCTION_REGISTRATION_FIELD_NUMBER: _ClassVar[int]
    FUNCTION_CALL_FIELD_NUMBER: _ClassVar[int]
    FUNCTION_BROKER_TOKEN_FIELD_NUMBER: _ClassVar[int]
    RESPONSE_FIELD_NUMBER: _ClassVar[int]
    RESPONSE_DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    type: FunctionUpdateType
    function_registration: FunctionRegistration
    function_call: FunctionCall
    function_broker_token: FunctionBrokerToken
    response: FunctionUpdateResponse
    response_description: str
    def __init__(self, type: _Optional[_Union[FunctionUpdateType, str]] = ..., function_registration: _Optional[_Union[FunctionRegistration, _Mapping]] = ..., function_call: _Optional[_Union[FunctionCall, _Mapping]] = ..., function_broker_token: _Optional[_Union[FunctionBrokerToken, _Mapping]] = ..., response: _Optional[_Union[FunctionUpdateResponse, str]] = ..., response_description: _Optional[str] = ...) -> None: ...

class FunctionRegistration(_message.Message):
    __slots__ = ("id", "state", "version", "description")
    ID_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    id: str
    state: FunctionRegistrationState
    version: str
    description: str
    def __init__(self, id: _Optional[str] = ..., state: _Optional[_Union[FunctionRegistrationState, str]] = ..., version: _Optional[str] = ..., description: _Optional[str] = ...) -> None: ...

class FunctionCall(_message.Message):
    __slots__ = ("id", "session_info")
    ID_FIELD_NUMBER: _ClassVar[int]
    SESSION_INFO_FIELD_NUMBER: _ClassVar[int]
    id: str
    session_info: _SessionController_pb2.SessionInfo
    def __init__(self, id: _Optional[str] = ..., session_info: _Optional[_Union[_SessionController_pb2.SessionInfo, _Mapping]] = ...) -> None: ...
