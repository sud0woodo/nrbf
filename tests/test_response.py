"""
Testdata (receiving of data when remote method is invoked):

0000 00 00 00 00 00 00 00 00 00 01 00 00 00 00 00 00 ................
0010 00 16 11 08 00 00 12 10 41 64 64 72 65 73 73 20 ........Address
0020 72 65 63 65 69 76 65 64 0B                      received.
"""

from io import BytesIO

# Local imports
from nrbf.helpers.c_nrbf import c_nrbf
from nrbf.nrbf import NRBF

TESTBUFFER = bytes.fromhex("000000000000000000010000000000000016110800001210416464726573732072656365697665640B")


def test_record_parsing():
    stream = BytesIO(TESTBUFFER)
    nrbf = NRBF(stream=stream)
    records = [record_type.Type.name for record_type, _ in nrbf.parse()]

    assert records == ["SerializationHeaderRecord", "BinaryMethodReturn"]


def test_binarymethodreturn():
    stream = BytesIO(b"\x16\x11\x08\x00\x00\x12\x10Address received\x0b")
    nrbf = NRBF(stream=stream)
    for record_type, record in nrbf.parse():
        assert record_type.Type == c_nrbf.RecordTypeEnumeration.BinaryMethodReturn
        assert record.MessageEnum.value == 2065
        assert record.ReturnValue.String == b"Address received"
