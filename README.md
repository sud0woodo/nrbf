# nrbf

Python script to parse Microsoft NRBF serialized streams into records or stdout.

## Background

From the [Microsoft documentation](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-nrbf/75b9fe09-be15-475f-85b8-ae7b7558cfe5?redirectedfrom=MSDN):

> The .NET Remoting: Binary Format Data Structure defines a set of structures that represent object graph or method invocation information as an octet stream.

While working on a malware implant the `NRBF` format was encountered which was a little bit annoying to parse using some poor Python file parsing, and proved not giving back the data in the format that was easier to parse using existing `Python` implementations. This tool was thus created to have some reference code to parse the Microsoft `NRBF` format, while also allowing extendability and usability with the support for [flow.record](https://github.com/fox-it/flow.record).

## Installation

Installing can be done using `pip`:

```sh
python -m pip install .
```

## CLI Usage

The script can be used straight from the command line, or by using the API. Since the script supports the output in the form of `flow.record`, `rdump` can be used to format the output if necessary. For `rdump` usage examples you can check out the [rdump documentation](https://docs.dissect.tools/en/latest/tools/rdump.html).

Simply print the records in the given hex stream to `stdout`:

```sh
$ nrbf-extract --hex 000000000000000000010000000000000016110800001210416464726573732072656365697665640B stdout
<nrbf/serializationheader type='SerializationHeaderRecord' RootId=0 HeaderId=0 MajorVersion=1 MinorVersion=0>
<nrbf/binarymethodreturn type='BinaryMethodReturn' MessageEnum='ReturnValueInline|NoContext|NoArgs' ReturnValue='Address received' CallContext=None Args=None>
```

Print the records in the given file to `stdout`:

```sh
nrbf-extract --file nrbf_addr_received_buffer.bin stdout
<nrbf/serializationheader type='SerializationHeaderRecord' RootId=0 HeaderId=0 MajorVersion=1 MinorVersion=0>
<nrbf/binarymethodreturn type='BinaryMethodReturn' MessageEnum='ReturnValueInline|NoContext|NoArgs' ReturnValue='Address received' CallContext=None Args=None>
```

Output `BinaryObjectString` records from the specified hex stream using `rdump`:

```sh
$ nrbf-extract --hex 0001000000FFFFFFFF01000000000000001514000000120B53656E6441646472657373126F444F4A52656D6F74696E674D657461646174612E4D795365727665722C20444F4A52656D6F74696E674D657461646174612C2056657273696F6E3D312E302E323632322E33313332362C2043756C747572653D6E65757472616C2C205075626C69634B6579546F6B656E3D6E756C6C10010000000100000009020000000C0300000051444F4A52656D6F74696E674D657461646174612C2056657273696F6E3D312E302E323632322E33313332362C2043756C747572653D6E65757472616C2C205075626C69634B6579546F6B656E3D6E756C6C05020000001B444F4A52656D6F74696E674D657461646174612E4164647265737304000000065374726565740443697479055374617465035A697001010101030000000604000000114F6E65204D6963726F736F6674205761790605000000075265646D6F6E64060600000002574106070000000539383035340B records | rdump -s "'BinaryObjectString' in r.type"
[reading from stdin]
<nrbf/binaryobjectstring type='BinaryObjectString' ObjectId=4 Value='One Microsoft Way'>
<nrbf/binaryobjectstring type='BinaryObjectString' ObjectId=5 Value='Redmond'>
<nrbf/binaryobjectstring type='BinaryObjectString' ObjectId=6 Value='WA'>
<nrbf/binaryobjectstring type='BinaryObjectString' ObjectId=7 Value='98054'>
```

## API Usage

The script was made to be easy in use when parsing `NRBF` streams as well.

```python
from io import BytesIO

from nrbf.nrbf import NRBF

stream = BytesIO(bytes.fromhex("000000000000000000010000000000000016110800001210416464726573732072656365697665640B"))
nrbf = NRBF(stream=stream)
nrbfrecords = NRBFRecords(nrbf=nrbf)
for record in nrbfrecords.records():
    # Do something with the record
```

## TODO

- Some records may not be parsed entirely correctly yet, please open an issue if you encounter errors :)
- Some record implementations need to be added to the `NRBFRecords` class to parse them correctly as some fields are added dynamically (e.g. `SystemClassWithMembersAndTypes` record type's `AdditionalInfos` field)
