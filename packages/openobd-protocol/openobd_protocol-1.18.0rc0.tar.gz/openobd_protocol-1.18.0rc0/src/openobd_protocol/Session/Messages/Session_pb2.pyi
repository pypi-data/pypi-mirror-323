from openobd_protocol.Session.Messages import ServiceResult_pb2 as _ServiceResult_pb2
from google.protobuf import any_pb2 as _any_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class MemoryContext(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    UNDEFINED_CONTEXT: _ClassVar[MemoryContext]
    GLOBAL_CONTEXT: _ClassVar[MemoryContext]
    FUNCTION_CONTEXT: _ClassVar[MemoryContext]
    CONNECTION_CONTEXT: _ClassVar[MemoryContext]
UNDEFINED_CONTEXT: MemoryContext
GLOBAL_CONTEXT: MemoryContext
FUNCTION_CONTEXT: MemoryContext
CONNECTION_CONTEXT: MemoryContext

class SessionToken(_message.Message):
    __slots__ = ("value",)
    VALUE_FIELD_NUMBER: _ClassVar[int]
    value: str
    def __init__(self, value: _Optional[str] = ...) -> None: ...

class SessionContext(_message.Message):
    __slots__ = ("id", "finished", "monitor_token", "authentication_token", "session_result")
    ID_FIELD_NUMBER: _ClassVar[int]
    FINISHED_FIELD_NUMBER: _ClassVar[int]
    MONITOR_TOKEN_FIELD_NUMBER: _ClassVar[int]
    AUTHENTICATION_TOKEN_FIELD_NUMBER: _ClassVar[int]
    SESSION_RESULT_FIELD_NUMBER: _ClassVar[int]
    id: str
    finished: bool
    monitor_token: str
    authentication_token: str
    session_result: _ServiceResult_pb2.ServiceResult
    def __init__(self, id: _Optional[str] = ..., finished: bool = ..., monitor_token: _Optional[str] = ..., authentication_token: _Optional[str] = ..., session_result: _Optional[_Union[_ServiceResult_pb2.ServiceResult, _Mapping]] = ...) -> None: ...

class FunctionId(_message.Message):
    __slots__ = ("value",)
    VALUE_FIELD_NUMBER: _ClassVar[int]
    value: str
    def __init__(self, value: _Optional[str] = ...) -> None: ...

class VariableList(_message.Message):
    __slots__ = ("memory", "prefix", "keys")
    MEMORY_FIELD_NUMBER: _ClassVar[int]
    PREFIX_FIELD_NUMBER: _ClassVar[int]
    KEYS_FIELD_NUMBER: _ClassVar[int]
    memory: MemoryContext
    prefix: str
    keys: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, memory: _Optional[_Union[MemoryContext, str]] = ..., prefix: _Optional[str] = ..., keys: _Optional[_Iterable[str]] = ...) -> None: ...

class Variable(_message.Message):
    __slots__ = ("memory", "key", "value", "object")
    MEMORY_FIELD_NUMBER: _ClassVar[int]
    KEY_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    OBJECT_FIELD_NUMBER: _ClassVar[int]
    memory: MemoryContext
    key: str
    value: str
    object: _any_pb2.Any
    def __init__(self, memory: _Optional[_Union[MemoryContext, str]] = ..., key: _Optional[str] = ..., value: _Optional[str] = ..., object: _Optional[_Union[_any_pb2.Any, _Mapping]] = ...) -> None: ...

class ConfigurationList(_message.Message):
    __slots__ = ("object",)
    OBJECT_FIELD_NUMBER: _ClassVar[int]
    object: _containers.RepeatedCompositeFieldContainer[_any_pb2.Any]
    def __init__(self, object: _Optional[_Iterable[_Union[_any_pb2.Any, _Mapping]]] = ...) -> None: ...
