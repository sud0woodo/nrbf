# Local imports
from typing import BinaryIO

# External dependencies
from dissect.cstruct import cstruct

# Local imports
from nrbf.helpers.c_nrbf import c_nrbf
from nrbf.helpers.exceptions import InvalidTypeError

c_def = """
typedef enum DateTimeKind : uint16_t {
    NotSpecified = 0,
    UTC = 1,
    Local = 2,
};

typedef struct DateTime {
    int64_t Ticks;
    DateTimeKind Kind;
};

typedef struct LengthPrefixedString {
    uint8_t Length : 7;    // This is so retarded, Microsoft...
    char String[Length];
};

typedef flag MessageFlags : uint32_t {
    NoArgs = 0x1,
    ArgsInline = 0x2,
    ArgsIsArray = 0x4,
    ArgsInArray = 0x8,
    NoContext = 0x10,
    ContextInline = 0x20,
    ContextInArray = 0x40,
    MethodSignatureInArray = 0x80,
    PropertiesInArray = 0x100,
    NoReturnValue = 0x200,
    ReturnValueVoid = 0x400,
    ReturnValueInline = 0x800,
    ReturnValueInArray = 0x1000,
    ExceptionInArray = 0x2000,
    GenericMethod = 0x4000
};

typedef enum PrimitiveTypeEnumeration : uint8_t {
    Boolean = 1,
    Byte = 2,
    Char = 3,
    Decimal = 5,
    Double = 6,
    Int16 = 7,
    Int32 = 8,
    Int64 = 9,
    SByte = 10,
    Single = 11,
    TimeSpan = 12,
    DateTime = 13,
    UInt16 = 14,
    UInt32 = 15,
    UInt64 = 16,
    Null = 17,
    String = 18
};

typedef struct ValueWithCode {
    PrimitiveTypeEnumeration PrimitiveTypeEnum;
    uint32_t Value;
};

typedef struct StringValueWithCode {
    PrimitiveTypeEnumeration PrimitiveTypeEnum;
    LengthPrefixedString Value;
};

typedef struct ArrayOfValueWithCode {
    uint32_t Length;
    ValueWithCode Values[Length];
};
"""


PRIMITIVETYPE_TRANSLATE_TABLE = {
    "Boolean": "uint8_t",
    "Byte": "byte",
    "Char": "char",
    "Decimal": "LengthPrefixedString",
    "Double": "uint64",
    "Int16": "int16",
    "Int32": "int32",
    "Int64": "int64",
    "SByte": "int8",
    "Single": "uint32",
    "TimeSpan": "int64",
    "DateTime": "DateTime",
    "UInt16": "uint16_t",
    "UInt32": "uint32_t",
    "UInt64": "uint64_t",
    "Null": "byte",
    "String": "LengthPrefixedString",
}


def binarymethodcall(stream: BinaryIO) -> cstruct:
    """Parse a BinaryMethodCall record from the stream.

    Because this record has fields that rely on the MessageFlags field, we need to parse it manually.
    This whole thing is quite hacky, but it works. Would like to find a better method to parse these.

    Args:
        stream: The NRBF stream containing the records.

    Returns:
        A cstruct containing the parsed BinaryMethodCall record.
    """

    binarymethod_def = c_def

    offset = stream.tell()
    messageflag = int.from_bytes(stream.read(4), "little")
    stream.seek(offset)

    _binarymethodcall = """
    typedef struct DynamicBinaryMethodCall {
        MessageFlags MessageEnum;
        StringValueWithCode MethodName;
        StringValueWithCode TypeName;
    """

    # Dynamic fields
    callcontext = "\tStringValueWithCode CallContext;\n"
    args = "\tArrayOfValueWithCode Args;\n"

    if messageflag & c_nrbf.MessageFlags.ContextInline:
        # CallContext field is present
        _binarymethodcall += callcontext

    if messageflag & c_nrbf.MessageFlags.ArgsInline:
        # Args field is present
        _binarymethodcall += args

    _binarymethodcall += "};\n"

    binarymethod_def += _binarymethodcall

    c_binarymethodcall = cstruct()
    c_binarymethodcall.load(binarymethod_def)

    # Assign to a new variable so we can delete the definition to prevent duplicate types in cstruct
    binarymethodcall_cstruct = c_binarymethodcall.DynamicBinaryMethodCall(stream)
    del c_binarymethodcall

    return binarymethodcall_cstruct


def binarymethodreturn(stream: BinaryIO) -> cstruct:
    """Parse a BinaryMethodReturn record from the stream.

    Because this record has fields that rely on the MessageFlags field, we need to parse it manually.
    This whole thing is quite hacky, but it works. Would like to find a better method to parse these.

    Args:
        stream: The NRBF stream containing the records.

    Returns:
        A cstruct containing the parsed BinaryMethodReturn record.
    """

    binarymethod_def = c_def

    offset = stream.tell()
    messageflag = int.from_bytes(stream.read(4), "little")
    stream.seek(offset)

    _binarymethodreturn = """
    typedef struct DynamicBinaryMethodReturnCall {
        MessageFlags MessageEnum;
    """

    # Dynamic fields
    # returnvalue = "\tValueWithCode ReturnValue;\n"
    callcontext = "\tStringValueWithCode CallContext;\n"
    args = "\tArrayOfValueWithCode Args;\n"

    if messageflag & c_nrbf.MessageFlags.ReturnValueInline:
        # ReturnValue field is present
        primitive_type = parse_primitivetype(stream=stream, offset=offset + 4)
        returnvalue = f"\tuint8_t ReturnValueType;\n\t{primitive_type}, ReturnValue;\n"
        _binarymethodreturn += returnvalue

    if messageflag & c_nrbf.MessageFlags.ContextInline:
        # CallContext field is present
        _binarymethodreturn += callcontext

    if messageflag & c_nrbf.MessageFlags.ArgsInline:
        # Args field is present
        _binarymethodreturn += args

    _binarymethodreturn += "};\n"

    binarymethod_def += _binarymethodreturn

    c_binarymethodreturncall = cstruct()
    c_binarymethodreturncall.load(binarymethod_def)

    # Reset the offset to start of the record
    stream.seek(offset)

    # Assign to a new variable so we can delete the definition to prevent duplicate types in cstruct
    binarymethodreturn_cstruct = c_binarymethodreturncall.DynamicBinaryMethodReturnCall(stream)
    del c_binarymethodreturncall

    return binarymethodreturn_cstruct


def parse_primitivetype(stream: BinaryIO, offset: int) -> str:
    """Translates the PrimitiveTypeEnumeration to its corresponding string representation.

    This function reads a byte from the given binary stream at the specified offset, interprets it as a
    PrimitiveTypeEnumeration value, and then translates it to its corresponding string representation
    according to the NRBF format.

    Args:
        stream: The binary stream to read from.
        offset: The offset in the stream to start reading from.

    Returns:
        The string representation of the PrimitiveTypeEnumeration value.

    Raises:
        InvalidTypeError: If the PrimitiveTypeEnumeration value is not recognized.
    """

    stream.seek(offset)
    primitive_type = int.from_bytes(stream.read(1), "little")

    try:
        return PRIMITIVETYPE_TRANSLATE_TABLE[c_nrbf.PrimitiveTypeEnumeration(primitive_type).name]
    except KeyError:
        raise InvalidTypeError(f"Invalid PrimitiveType: {primitive_type}")
