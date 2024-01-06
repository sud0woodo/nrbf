# External dependencies
from dissect.cstruct import cstruct

nrbf_def = """
// https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-nrbf/75b9fe09-be15-475f-85b8-ae7b7558cfe5?redirectedfrom=MSDN

typedef struct LengthPrefixedString {
    uint8_t Length : 7;    // This is so retarded, Microsoft...
    char String[Length];
};

/* ======== Common Definitions ======== */
typedef enum RecordTypeEnumeration : uint8_t {
    SerializationHeaderRecord = 0
    ClassWithId = 1
    SystemClassWithMembers = 2
    ClassWithMembers = 3
    SystemClassWithMembersAndTypes = 4
    ClassWithMembersAndTypes = 5
    BinaryObjectString = 6
    BinaryArray = 7
    MemberPrimitiveTyped = 8
    MemberReference = 9
    ObjectNull = 10
    MessageEnd = 11
    BinaryLibrary = 12
    ObjectNullMultiple256 = 13
    ObjectNullMultiple = 14
    ArraySinglePrimitive = 15
    ArraySingleObject = 16
    ArraySingleString = 17
    BinaryMethodCall = 21
    BinaryMethodReturn = 22
};

typedef enum BinaryTypeEnumeration : uint8_t {
    Primitive = 0,
    String = 1,
    Object = 2,
    SystemClass = 3,
    Class = 4,
    ObjectArray = 5,
    StringArray = 6,
    PrimitiveArray = 7
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

typedef struct RecordHeader {
    RecordTypeEnumeration Type;
};

/* ======== Method Invocation Records ======== */
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

typedef struct BinaryMethodCall {
    MessageFlags MessageEnum;
    StringValueWithCode MethodName;
    StringValueWithCode TypeName;
    /*
        These fields are optional, depending on the MessageFlags
        therefore we will parse these in the code instead of in the struct itself.

        StringValueWithCode CallContext;
        ArrayOfValueWithCode Args;
    */
};

typedef struct MethodCallArray {
    uint32_t Length;
    BinaryMethodCall Methods[Length];
};

typedef struct BinaryMethodReturn {
    MessageFlags MessageEnum;
    /*
        These fields are optional, depending on the MessageFlags
        therefore we will parse these in the code instead of in the struct itself.
        
        ValueWithCode ReturnValue;
        StringValueWithCode CallContext;
        ArrayOfValueWithCode Args;
    */
};

typedef struct MethodReturnCallArray {
    uint32_t Length;
    BinaryMethodReturn Returns[Length];
};

/* ======== Class Records ======== */
typedef struct ClassInfo {
    uint32_t ObjectId;
    LengthPrefixedString Name;
    uint32_t MemberCount;
    LengthPrefixedString MemberNames[MemberCount];
};

typedef struct MemberTypeInfo {
    BinaryTypeEnumeration BinaryTypeEnum;
};

// Combined with ClassInfo for easier parsing
typedef struct ClassWithMembersAndTypes {
    uint32_t ObjectId;
    LengthPrefixedString Name;
    uint32_t MemberCount;
    LengthPrefixedString MemberNames[MemberCount];
    BinaryTypeEnumeration BinaryTypeEnum[MemberCount];
    uint32_t LibraryId;
};

// Combined with ClassInfo for easier parsing
typedef struct ClassWithMembers {
    uint32_t ObjectId;
    LengthPrefixedString Name;
    uint32_t MemberCount;
    LengthPrefixedString MemberNames[MemberCount];
    uint32_t LibraryId;
};

// Combined with ClassInfo and MemberTypeInfo for easier parsing
typedef struct SystemClassWithMembersAndTypes {
    uint32_t ObjectId;
    LengthPrefixedString Name;
    uint32_t MemberCount;
    LengthPrefixedString MemberNames[MemberCount];
    BinaryTypeEnumeration BinaryTypeEnum[MemberCount];
    // AdditionalInfos must be parsed seperately
};

// Combined with ClassInfo for easier parsing
typedef struct SystemClassWithMembers {
    uint32_t ObjectId;
    LengthPrefixedString Name;
    uint32_t MemberCount;
    LengthPrefixedString MemberNames[MemberCount];
};

typedef struct ClassWithId {
    uint32_t ObjectId;
    uint32_t MetadataId;
};

/* ======== Array Records ======== */
typedef enum BinaryArrayTypeEnumeration : uint8_t {
    Single = 0,
    Jagged = 1,
    Rectangular = 2,
    SingleOffset = 3,
    JaggedOffset = 4,
    RectangularOffset = 5
};

typedef struct ArrayInfo {
    uint32_t ObjectId;
    uint32_t Length;
};

typedef struct BinaryArray {
    uint32_t ObjectId;
    BinaryArrayTypeEnumeration BinaryArrayTypeEnum;
    uint32_t Rank;
    uint32_t Lengths[Rank];
    int32_t LowerBounds[Rank];
    BinaryTypeEnumeration TypeEnum;
    // BinaryTypeEnumeration AdditionalTypeInfo; -> Not encountered yet, need to test
};

typedef struct ArraySingleObject {
    uint32_t ObjectId;
    uint32_t Length;
};

typedef struct ArraySinglePrimitive {
    ArrayInfo ArrayInfo;
    PrimitiveTypeEnumeration PrimitiveTypeEnum;
};

typedef struct ArraySingleString {
    ArrayInfo ArrayInfo;
};

/* ======== Member Reference Records ======== */
typedef struct MemberPrimitiveTyped {
    PrimitiveTypeEnumeration PrimitiveTypeEnum;
};

typedef struct MemberReference {
    uint32_t IdRef;
};

// Just here for completeness
typedef struct ObjectNull {
    RecordTypeEnumeration RecordTypeEnum;
};

typedef struct ObjectNullMultiple {
    uint32_t NullCount;
};

typedef struct ObjectNullMultiple256 {
    uint8_t NullCount;
};

typedef struct BinaryObjectString {
    uint32_t ObjectId;
    uint8_t Length : 7;
    char Value[Length];
};

/* ======== Other Records ======== */
typedef struct SerializationHeaderRecord {
    uint32_t RootId;
    uint32_t HeaderId;
    uint32_t MajorVersion;
    uint32_t MinorVersion;
};

typedef struct BinaryLibrary {
    uint32_t LibraryId;
    uint8_t Length : 7;
    char LibraryName[Length];
};

// Just here for completeness
typedef struct MessageEnd {
    // RecordTypeEnumeration RecordTypeEnum;
};
"""

c_nrbf = cstruct()
c_nrbf.load(nrbf_def)
