from collections.abc import Callable, Mapping, Sequence
import enum

from numpy.typing import ArrayLike

import sgl


class AccessType(enum.Enum):
    _new_member_ = __new__

    _use_args_: bool = False

    _member_names_: list = ['none', 'read', 'write', 'readwrite']

    _member_map_: dict = ...

    _value2member_map_: dict = ...

    _unhashable_values_: list = []

    _value_repr_: None = None

    none = 0

    read = 1

    write = 2

    readwrite = 3

class CallContext(sgl.Object):
    def __init__(self, device: sgl.Device, call_shape: Shape, call_mode: CallMode) -> None:
        """N/A"""

    @property
    def device(self) -> sgl.Device:
        """N/A"""

    @property
    def call_shape(self) -> Shape:
        """N/A"""

    @property
    def call_mode(self) -> CallMode:
        """N/A"""

class CallMode(enum.Enum):
    _new_member_ = __new__

    _use_args_: bool = False

    _member_names_: list = ['prim', 'bwds', 'fwds']

    _member_map_: dict = ...

    _value2member_map_: dict = ...

    _unhashable_values_: list = []

    _value_repr_: None = None

    prim = 0

    bwds = 1

    fwds = 2

class FunctionNodeType(enum.Enum):
    _new_member_ = __new__

    _use_args_: bool = False

    _member_names_: list = ['unknown', 'uniforms', 'kernelgen', 'this']

    _member_map_: dict = ...

    _value2member_map_: dict = ...

    _unhashable_values_: list = []

    _value_repr_: None = None

    unknown = 0

    uniforms = 1

    kernelgen = 2

    this = 3

class NativeBoundCallRuntime(sgl.Object):
    def __init__(self) -> None:
        """N/A"""

    @property
    def args(self) -> list[NativeBoundVariableRuntime]:
        """N/A"""

    @args.setter
    def args(self, arg: Sequence[NativeBoundVariableRuntime], /) -> None: ...

    @property
    def kwargs(self) -> dict[str, NativeBoundVariableRuntime]:
        """N/A"""

    @kwargs.setter
    def kwargs(self, arg: Mapping[str, NativeBoundVariableRuntime], /) -> None: ...

    def find_kwarg(self, arg: str, /) -> NativeBoundVariableRuntime:
        """N/A"""

    def calculate_call_shape(self, arg0: int, arg1: list, arg2: dict, /) -> Shape:
        """N/A"""

    def read_call_data_post_dispatch(self, arg0: CallContext, arg1: dict, arg2: list, arg3: dict, /) -> None:
        """N/A"""

    def write_raw_dispatch_data(self, arg0: dict, arg1: dict, /) -> None:
        """N/A"""

class NativeBoundVariableRuntime(sgl.Object):
    def __init__(self) -> None:
        """N/A"""

    @property
    def access(self) -> tuple[AccessType, AccessType]:
        """N/A"""

    @access.setter
    def access(self, arg: tuple[AccessType, AccessType], /) -> None: ...

    @property
    def transform(self) -> Shape:
        """N/A"""

    @transform.setter
    def transform(self, arg: Shape, /) -> None: ...

    @property
    def python_type(self) -> NativeMarshall:
        """N/A"""

    @python_type.setter
    def python_type(self, arg: NativeMarshall, /) -> None: ...

    @property
    def vector_type(self) -> NativeSlangType:
        """N/A"""

    @vector_type.setter
    def vector_type(self, arg: NativeSlangType, /) -> None: ...

    @property
    def shape(self) -> Shape:
        """N/A"""

    @shape.setter
    def shape(self, arg: Shape, /) -> None: ...

    @property
    def variable_name(self) -> str:
        """N/A"""

    @variable_name.setter
    def variable_name(self, arg: str, /) -> None: ...

    @property
    def children(self) -> dict[str, NativeBoundVariableRuntime] | None:
        """N/A"""

    @children.setter
    def children(self, arg: Mapping[str, NativeBoundVariableRuntime], /) -> None: ...

    def populate_call_shape(self, arg0: Sequence[int], arg1: object, /) -> None:
        """N/A"""

    def read_call_data_post_dispatch(self, arg0: CallContext, arg1: dict, arg2: object, /) -> None:
        """N/A"""

    def write_raw_dispatch_data(self, arg0: dict, arg1: object, /) -> None:
        """N/A"""

    def read_output(self, arg0: CallContext, arg1: object, /) -> object:
        """N/A"""

class NativeCallData(sgl.Object):
    def __init__(self) -> None:
        """N/A"""

    @property
    def device(self) -> sgl.Device:
        """N/A"""

    @device.setter
    def device(self, arg: sgl.Device, /) -> None: ...

    @property
    def kernel(self) -> sgl.ComputeKernel:
        """N/A"""

    @kernel.setter
    def kernel(self, arg: sgl.ComputeKernel, /) -> None: ...

    @property
    def call_dimensionality(self) -> int:
        """N/A"""

    @call_dimensionality.setter
    def call_dimensionality(self, arg: int, /) -> None: ...

    @property
    def runtime(self) -> NativeBoundCallRuntime:
        """N/A"""

    @runtime.setter
    def runtime(self, arg: NativeBoundCallRuntime, /) -> None: ...

    @property
    def call_mode(self) -> CallMode:
        """N/A"""

    @call_mode.setter
    def call_mode(self, arg: CallMode, /) -> None: ...

    @property
    def last_call_shape(self) -> Shape:
        """N/A"""

    def call(self, opts: NativeCallRuntimeOptions, *args, **kwargs) -> object:
        """N/A"""

    def append_to(self, opts: NativeCallRuntimeOptions, command_buffer: sgl.CommandBuffer, *args, **kwargs) -> object:
        """N/A"""

class NativeCallDataCache(sgl.Object):
    def __init__(self) -> None:
        """N/A"""

    def get_value_signature(self, builder: SignatureBuilder, o: object) -> None:
        """N/A"""

    def get_args_signature(self, builder: SignatureBuilder, *args, **kwargs) -> None:
        """N/A"""

    def find_call_data(self, signature: str) -> NativeCallData:
        """N/A"""

    def add_call_data(self, signature: str, call_data: NativeCallData) -> None:
        """N/A"""

    def lookup_value_signature(self, o: object) -> str | None:
        """N/A"""

class NativeCallRuntimeOptions(sgl.Object):
    def __init__(self) -> None:
        """N/A"""

    @property
    def uniforms(self) -> list:
        """N/A"""

    @uniforms.setter
    def uniforms(self, arg: list, /) -> None: ...

class NativeFunctionNode(NativeObject):
    def __init__(self, parent: NativeFunctionNode | None, type: FunctionNodeType, data: object | None) -> None:
        """N/A"""

    @property
    def _native_parent(self) -> NativeFunctionNode: ...

    @property
    def _native_type(self) -> FunctionNodeType: ...

    @property
    def _native_data(self) -> object: ...

    def _find_native_root(self) -> NativeFunctionNode:
        """N/A"""

    def _native_build_call_data(self, cache: NativeCallDataCache, *args, **kwargs) -> NativeCallData:
        """N/A"""

    def _native_call(self, cache: NativeCallDataCache, *args, **kwargs) -> object:
        """N/A"""

    def _native_append_to(self, cache: NativeCallDataCache, command_buffer: sgl.CommandBuffer, *args, **kwargs) -> None:
        """N/A"""

    def generate_call_data(self, *args, **kwargs) -> NativeCallData:
        """N/A"""

    def read_signature(self, builder: SignatureBuilder) -> None:
        """N/A"""

    def gather_runtime_options(self, options: NativeCallRuntimeOptions) -> None:
        """N/A"""

class NativeMarshall(sgl.Object):
    def __init__(self) -> None:
        """N/A"""

    @property
    def concrete_shape(self) -> Shape:
        """N/A"""

    @concrete_shape.setter
    def concrete_shape(self, arg: Shape, /) -> None: ...

    @property
    def slang_type(self) -> NativeSlangType:
        """N/A"""

    @slang_type.setter
    def slang_type(self, arg: NativeSlangType, /) -> None: ...

    def write_shader_cursor_pre_dispatch(self, context: CallContext, binding: NativeBoundVariableRuntime, cursor: sgl.ShaderCursor, value: object, read_back: list) -> None:
        """N/A"""

    def create_calldata(self, arg0: CallContext, arg1: NativeBoundVariableRuntime, arg2: object, /) -> object:
        """N/A"""

    def read_calldata(self, arg0: CallContext, arg1: NativeBoundVariableRuntime, arg2: object, arg3: object, /) -> None:
        """N/A"""

    def create_output(self, arg0: CallContext, arg1: NativeBoundVariableRuntime, /) -> object:
        """N/A"""

    def read_output(self, arg0: CallContext, arg1: NativeBoundVariableRuntime, arg2: object, /) -> object:
        """N/A"""

class NativeNDBuffer(NativeObject):
    def __init__(self, arg0: sgl.Device, arg1: NativeNDBufferDesc, /) -> None: ...

    @property
    def device(self) -> sgl.Device: ...

    @property
    def dtype(self) -> NativeSlangType: ...

    @property
    def shape(self) -> Shape: ...

    @property
    def strides(self) -> Shape: ...

    @property
    def element_count(self) -> int: ...

    @property
    def usage(self) -> sgl.ResourceUsage: ...

    @property
    def memory_type(self) -> sgl.MemoryType: ...

    @property
    def storage(self) -> sgl.Buffer: ...

    def to_numpy(self) -> ArrayLike:
        """N/A"""

    def from_numpy(self, data: ArrayLike) -> None:
        """N/A"""

class NativeNDBufferDesc:
    def __init__(self) -> None: ...

    @property
    def dtype(self) -> NativeSlangType: ...

    @dtype.setter
    def dtype(self, arg: NativeSlangType, /) -> None: ...

    @property
    def element_stride(self) -> int: ...

    @element_stride.setter
    def element_stride(self, arg: int, /) -> None: ...

    @property
    def shape(self) -> Shape: ...

    @shape.setter
    def shape(self, arg: Shape, /) -> None: ...

    @property
    def strides(self) -> Shape: ...

    @strides.setter
    def strides(self, arg: Shape, /) -> None: ...

    @property
    def usage(self) -> sgl.ResourceUsage: ...

    @usage.setter
    def usage(self, arg: sgl.ResourceUsage, /) -> None: ...

    @property
    def memory_type(self) -> sgl.MemoryType: ...

    @memory_type.setter
    def memory_type(self, arg: sgl.MemoryType, /) -> None: ...

class NativeNDBufferMarshall(NativeMarshall):
    def __init__(self, dims: int, writable: bool, slang_type: NativeSlangType, slang_element_type: NativeSlangType, element_stride: int) -> None:
        """N/A"""

    @property
    def dims(self) -> int: ...

    @property
    def writable(self) -> bool: ...

    @property
    def slang_element_type(self) -> NativeSlangType: ...

class NativeNumpyMarshall(NativeNDBufferMarshall):
    def __init__(self, dims: int, slang_type: NativeSlangType, slang_element_type: NativeSlangType, element_stride: int, numpydtype: object) -> None:
        """N/A"""

    @property
    def dtype(self) -> "dlpack::dtype": ...

class NativeObject(sgl.Object):
    def __init__(self) -> None:
        """N/A"""

    @property
    def slangpy_signature(self) -> str: ...

    @slangpy_signature.setter
    def slangpy_signature(self, arg: str, /) -> None: ...

    def read_signature(self, builder: SignatureBuilder) -> None:
        """N/A"""

class NativeSlangType(sgl.Object):
    def __init__(self) -> None:
        """N/A"""

    @property
    def type_reflection(self) -> sgl.TypeReflection:
        """N/A"""

    @type_reflection.setter
    def type_reflection(self, arg: sgl.TypeReflection, /) -> None: ...

    @property
    def shape(self) -> Shape:
        """N/A"""

    @shape.setter
    def shape(self, arg: Shape, /) -> None: ...

class NativeValueMarshall(NativeMarshall):
    def __init__(self) -> None:
        """N/A"""

class Shape:
    def __init__(self, *args) -> None:
        """N/A"""

    def __add__(self, arg: Shape, /) -> Shape:
        """N/A"""

    def __getitem__(self, index: int) -> int:
        """N/A"""

    def __len__(self) -> int:
        """N/A"""

    @property
    def valid(self) -> bool:
        """N/A"""

    @property
    def concrete(self) -> bool:
        """N/A"""

    def as_tuple(self) -> tuple:
        """N/A"""

    def as_list(self) -> list[int]:
        """N/A"""

    def __repr__(self) -> str:
        """N/A"""

    def __str__(self) -> str:
        """N/A"""

    def __eq__(self, arg: object, /) -> bool:
        """N/A"""

class SignatureBuilder(sgl.Object):
    def __init__(self) -> None:
        """N/A"""

    def add(self, value: str) -> None:
        """N/A"""

    @property
    def str(self) -> str:
        """N/A"""

    @property
    def bytes(self) -> bytes:
        """N/A"""

def hash_signature(value_to_id: Callable[[object], str], *args, **kwargs) -> str:
    """N/A"""

def pack_arg(arg: object, unpacked_arg: object) -> None:
    """N/A"""

def unpack_arg(arg: object) -> object:
    """N/A"""

def unpack_args(*args) -> list:
    """N/A"""

def unpack_kwargs(**kwargs) -> dict:
    """N/A"""
