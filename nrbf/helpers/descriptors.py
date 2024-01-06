# External dependencies
from flow.record import RecordDescriptor

NRBF_DESCRIPTORS = {
    "SerializationHeaderRecord": RecordDescriptor(
        "nrbf/serializationheader",
        [
            ("string", "type"),
            ("varint", "RootId"),
            ("varint", "HeaderId"),
            ("varint", "MajorVersion"),
            ("varint", "MinorVersion"),
        ],
    ),
    "BinaryMethodReturn": RecordDescriptor(
        "nrbf/binarymethodreturn",
        [
            ("string", "type"),
            ("string", "MessageEnum"),
            ("string", "ReturnValue"),
            ("string", "CallContext"),
            ("stringlist", "Args"),
        ],
    ),
    "BinaryMethodCall": RecordDescriptor(
        "nrbf/binarymethodcall",
        [
            ("string", "type"),
            ("string", "MessageEnum"),
            ("string", "MethodName"),
            ("string", "TypeName"),
            ("string", "CallContext"),
            ("stringlist", "Args"),
        ],
    ),
    "ArraySingleObject": RecordDescriptor(
        "nrbf/arraysingleobject",
        [
            ("string", "type"),
            ("varint", "ObjectId"),
            ("varint", "Length"),
        ],
    ),
    "MemberReference": RecordDescriptor(
        "nrbf/memberreference",
        [
            ("string", "type"),
            ("varint", "IdRef"),
        ],
    ),
    "BinaryLibrary": RecordDescriptor(
        "nrbf/binarylibrary",
        [
            ("string", "type"),
            ("varint", "LibraryId"),
            ("string", "LibraryName"),
        ],
    ),
    "ClassWithMembersAndTypes": RecordDescriptor(
        "nrbf/classwithmembersandtypes",
        [
            ("string", "type"),
            ("string", "Name"),
            ("varint", "MemberCount"),
            ("stringlist", "MemberNames"),
            ("stringlist", "BinaryTypeEnum"),
            ("varint", "LibraryId"),
        ],
    ),
    "BinaryObjectString": RecordDescriptor(
        "nrbf/binaryobjectstring",
        [
            ("string", "type"),
            ("varint", "ObjectId"),
            ("string", "Value"),
        ],
    ),
    "ClassWithMembers": RecordDescriptor(
        "nrbf/classwithmembers",
        [
            ("string", "type"),
            ("varint", "ObjectId"),
            ("string", "Name"),
            ("varint", "MemberCount"),
            ("stringlist", "MemberNames"),
            ("varint", "LibraryId"),
        ],
    ),
    "SystemClassWithMembersAndTypes": RecordDescriptor(
        "nrbf/systemclasswithmembersandtypes",
        [
            ("string", "type"),
            ("varint", "ObjectId"),
            ("string", "Name"),
            ("varint", "MemberCount"),
            ("stringlist", "MemberNames"),
            ("stringlist", "BinaryTypeEnum"),
        ],
    ),
    "SystemClassWithMembers": RecordDescriptor(
        "nrbf/systemclasswithmembers",
        [
            ("string", "type"),
            ("varint", "ObjectId"),
            ("string", "Name"),
            ("varint", "MemberCount"),
            ("stringlist", "MemberNames"),
        ],
    ),
    "ClassWithId": RecordDescriptor(
        "nrbf/classwithid",
        [
            ("string", "type"),
            ("varint", "ObjectId"),
            ("varint", "MetadataId"),
        ],
    ),
    "BinaryArray": RecordDescriptor(
        "nrbf/binaryarray",
        [
            ("string", "type"),
            ("varint", "ObjectId"),
            ("string", "BinaryArrayTypeEnum"),
            ("varint", "Rank"),
            ("stringlist", "Lengths"),
            ("stringlist", "LoverBounds"),
            ("string", "TypeEnum"),
            ("string", "AdditionalTypeInfo"),
        ],
    ),
}
