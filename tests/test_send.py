"""
Testdata (sending of data when remote method is invoked):

0000 00 01 00 00 00 FF FF FF FF 01 00 00 00 00 00 00 .....ÿÿÿÿ.......
0010 00 15 14 00 00 00 12 0B 53 65 6E 64 41 64 64 72 ........SendAddr
0020 65 73 73 12 6F 44 4F 4A 52 65 6D 6F 74 69 6E 67 ess.oDOJRemoting
0030 4D 65 74 61 64 61 74 61 2E 4D 79 53 65 72 76 65 Metadata.MyServe
0040 72 2C 20 44 4F 4A 52 65 6D 6F 74 69 6E 67 4D 65 r, DOJRemotingMe
0050 74 61 64 61 74 61 2C 20 56 65 72 73 69 6F 6E 3D tadata, Version=
0060 31 2E 30 2E 32 36 32 32 2E 33 31 33 32 36 2C 20 1.0.2622.31326,
0070 43 75 6C 74 75 72 65 3D 6E 65 75 74 72 61 6C 2C Culture=neutral,
0080 20 50 75 62 6C 69 63 4B 65 79 54 6F 6B 65 6E 3D PublicKeyToken=
0090 6E 75 6C 6C 10 01 00 00 00 01 00 00 00 09 02 00 null............
00A0 00 00 0C 03 00 00 00 51 44 4F 4A 52 65 6D 6F 74 .......QDOJRemot
00B0 69 6E 67 4D 65 74 61 64 61 74 61 2C 20 56 65 72 ingMetadata, Ver
00C0 73 69 6F 6E 3D 31 2E 30 2E 32 36 32 32 2E 33 31 sion=1.0.2622.31
00D0 33 32 36 2C 20 43 75 6C 74 75 72 65 3D 6E 65 75 326, Culture=neu
00E0 74 72 61 6C 2C 20 50 75 62 6C 69 63 4B 65 79 54 tral, PublicKeyT
00F0 6F 6B 65 6E 3D 6E 75 6C 6C 05 02 00 00 00 1B 44 oken=null......D
0100 4F 4A 52 65 6D 6F 74 69 6E 67 4D 65 74 61 64 61 OJRemotingMetada
0110 74 61 2E 41 64 64 72 65 73 73 04 00 00 00 06 53 ta.Address.....S
0120 74 72 65 65 74 04 43 69 74 79 05 53 74 61 74 65 treet.City.State
0130 03 5A 69 70 01 01 01 01 03 00 00 00 06 04 00 00 .Zip............
0140 00 11 4F 6E 65 20 4D 69 63 72 6F 73 6F 66 74 20 ..One Microsoft
0150 57 61 79 06 05 00 00 00 07 52 65 64 6D 6F 6E 64 Way......Redmond
0160 06 06 00 00 00 02 57 41 06 07 00 00 00 05 39 38 ......WA......98
0170 30 35 34 0B                                     054.
"""

from io import BytesIO

# External dependencies
import pytest

# Local imports
from nrbf.helpers.c_nrbf import c_nrbf
from nrbf.nrbf import NRBF

TESTBUFFER = bytes.fromhex(
    "0001000000FFFFFFFF01000000000000001514000000120B53656E6441646472657373126F444F4A52656D6F74696E674D657461646174612E4D795365727665722C20444F4A52656D6F74696E674D657461646174612C2056657273696F6E3D312E302E323632322E33313332362C2043756C747572653D6E65757472616C2C205075626C69634B6579546F6B656E3D6E756C6C10010000000100000009020000000C0300000051444F4A52656D6F74696E674D657461646174612C2056657273696F6E3D312E302E323632322E33313332362C2043756C747572653D6E65757472616C2C205075626C69634B6579546F6B656E3D6E756C6C05020000001B444F4A52656D6F74696E674D657461646174612E4164647265737304000000065374726565740443697479055374617465035A697001010101030000000604000000114F6E65204D6963726F736F6674205761790605000000075265646D6F6E64060600000002574106070000000539383035340B"
)


def test_record_parsing():
    stream = BytesIO(TESTBUFFER)
    nrbf = NRBF(stream=stream)
    records = [record_type.Type.name for record_type, _ in nrbf.parse()]

    assert records == [
        "SerializationHeaderRecord",
        "BinaryMethodCall",
        "ArraySingleObject",
        "MemberReference",
        "BinaryLibrary",
        "ClassWithMembersAndTypes",
        "BinaryObjectString",
        "BinaryObjectString",
        "BinaryObjectString",
        "BinaryObjectString",
    ]


def test_valid_serializationheaderrecord():
    stream = BytesIO(bytes.fromhex("0001000000FFFFFFFF0100000000000000"))
    nrbf = NRBF(stream=stream)
    for record_type, record in nrbf.parse():
        assert record_type.Type == c_nrbf.RecordTypeEnumeration.SerializationHeaderRecord
        assert record.RootId == 0x1
        assert record.HeaderId == 0xFFFFFFFF
        assert record.MajorVersion == 0x1
        assert record.MinorVersion == 0x0


def test_invalid_serializationheaderrecord():
    # MajorVersion invalid: 0x0
    stream = BytesIO(bytes.fromhex("0001000000FFFFFFFF0000000000000000"))
    nrbf = NRBF(stream=stream)
    with pytest.raises(Exception) as err:
        for _, _ in nrbf.parse():
            continue

        assert str(err.value) == "Invalid SerializationHeaderRecord"


def test_binarymethodcallrecord():
    stream = BytesIO(
        b"\x15\x14\x00\x00\x00\x12\x0bSendAddress\x12oDOJRemotingMetadata.MyServer, DOJRemotingMetadata, Version=1.0.2622.31326, Culture=neutral, PublicKeyToken=null"
    )
    nrbf = NRBF(stream=stream)
    for record_type, record in nrbf.parse():
        assert record_type.Type == c_nrbf.RecordTypeEnumeration.BinaryMethodCall
        assert record.MessageEnum.value == 20
        assert record.MethodName.Value.String == b"SendAddress"
        assert (
            record.TypeName.Value.String
            == b"DOJRemotingMetadata.MyServer, DOJRemotingMetadata, Version=1.0.2622.31326, Culture=neutral, PublicKeyToken=null"
        )


def test_arraysingleobject():
    stream = BytesIO(b"\x10\x01\x00\x00\x00\x01\x00\x00\x00")
    nrbf = NRBF(stream=stream)
    for record_type, record in nrbf.parse():
        assert record_type.Type == c_nrbf.RecordTypeEnumeration.ArraySingleObject
        assert record.ObjectId == 0x1
        assert record.Length == 0x1


def test_memberreference():
    stream = BytesIO(b"\x09\x02\x00\x00\x00")
    nrbf = NRBF(stream=stream)
    for record_type, record in nrbf.parse():
        assert record_type.Type == c_nrbf.RecordTypeEnumeration.MemberReference
        assert record.IdRef == 0x2


def test_binarylibrary():
    stream = BytesIO(
        b"\x0C\x03\x00\x00\x00QDOJRemotingMetadata, Version=1.0.2622.31326, Culture=neutral, PublicKeyToken=null"
    )
    nrbf = NRBF(stream=stream)
    for record_type, record in nrbf.parse():
        assert record_type.Type == c_nrbf.RecordTypeEnumeration.BinaryLibrary
        assert record.LibraryId == 0x3
        assert (
            record.LibraryName == b"DOJRemotingMetadata, Version=1.0.2622.31326, Culture=neutral, PublicKeyToken=null"
        )


def test_classwithmembersandtypes():
    stream = BytesIO(
        b"\x05\x02\x00\x00\x00\x1bDOJRemotingMetadata.Address\x04\x00\x00\x00\x06Street\x04City\x05State\x03Zip\x01\x01\x01\x01\x03\x00\x00\x00"
    )
    nrbf = NRBF(stream=stream)
    for record_type, record in nrbf.parse():
        assert record_type.Type == c_nrbf.RecordTypeEnumeration.ClassWithMembersAndTypes
        assert record.ObjectId == 0x2
        assert record.Name.String == b"DOJRemotingMetadata.Address"
        assert record.MemberCount == 0x4
        assert record.MemberNames[0].String == b"Street"
        assert record.MemberNames[1].String == b"City"
        assert record.MemberNames[2].String == b"State"
        assert record.MemberNames[3].String == b"Zip"
        assert record.BinaryTypeEnum == [1, 1, 1, 1]
        assert record.LibraryId == 0x3


def test_binaryobjectstring():
    stream = BytesIO(b"\x06\x04\x00\x00\x00\x11One Microsoft Way")
    nrbf = NRBF(stream=stream)
    for record_type, record in nrbf.parse():
        assert record_type.Type == c_nrbf.RecordTypeEnumeration.BinaryObjectString
        assert record.ObjectId == 0x4
        assert record.Value == b"One Microsoft Way"
