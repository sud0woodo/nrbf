from __future__ import annotations

from typing import TYPE_CHECKING, BinaryIO, Generator

# Local imports
from nrbf.helpers.c_nrbf import c_nrbf
from nrbf.helpers.descriptors import NRBF_DESCRIPTORS
from nrbf.helpers.dynamic_defs import binarymethodcall, binarymethodreturn
from nrbf.helpers.exceptions import DescriptorError, InvalidRecordError

if TYPE_CHECKING:
    from dissect.cstruct import cstruct
    from flow.record import RecordDescriptor


class NRBF:
    def __init__(self, stream: BinaryIO):
        self.stream = stream

    def parse(self) -> Generator[tuple[cstruct, cstruct]]:
        """Parse the stream and yield the records as cstruct objects for further parsing by the user.

        Yields:
            A tuple containing the NRBF record header and the NRBF record itself.

        Raises:
            EOFError: If the stream ending has been reached without a MessageEnd record.
        """

        while True:
            try:
                header = self._header()
            except EOFError:
                # Reached the end of the stream before encountering a MessageEnd record
                break

            if header.Type == c_nrbf.RecordTypeEnumeration.MessageEnd:
                # Reached the end of the stream
                break

            if header.Type == c_nrbf.RecordTypeEnumeration.ObjectNull:
                # This record type holds no data, just keep on trucking
                continue

            record = self._get_record(record_type=header.Type.name)

            # Check if the record is indeed valid
            self._is_valid(header=header.Type, record=record)

            yield header, record

    def records(self) -> Generator[RecordDescriptor]:
        """Parse the stream and yield records as RecordDescriptor objects.

        Returns:
            A generator that yields RecordDescriptor objects.
        """

        nrbfrecords = NRBFRecords(nrbf=self)
        yield from nrbfrecords.records()

    def _header(self) -> cstruct:
        """Get the next record header from the stream."""

        try:
            return c_nrbf.RecordHeader(self.stream.read(1))
        except EOFError:
            raise EOFError("Reached the end of the stream before encountering a MessageEnd record")

    def _get_record(self, record_type: str) -> cstruct:
        """Get the record that is associated with the given record type.

        Some records have dynamic fields and need to be parsed seperately.

        Args:
            record_type: The type of the record that is used to retrieve the associated cstruct definition.

        Returns:
            A cstruct containing the parsed record.

        Raises:
            AttributeError: If the given record type is invalid.
        """

        try:
            # Get the record definition
            record_def = getattr(c_nrbf, record_type)
        except AttributeError:
            raise AttributeError(f"Invalid RecordTypeEnumeration value: {record_type}")

        if record_type == "BinaryMethodCall":
            # BinaryMethodCall is a special case, since it has a dynamic definition
            record = binarymethodcall(stream=self.stream)
        elif record_type == "BinaryMethodReturn":
            record = binarymethodreturn(stream=self.stream)
        else:
            record = record_def(self.stream)

        return record

    def _is_valid(self, header: cstruct, record: cstruct) -> bool:
        """Validates the given record according to the NRBF format.

        This function checks if the given record is valid according to the NRBF format.
        Currently, it only checks if SerializationHeaderRecord has the correct MajorVersion and MinorVersion.
        If the record is not valid, it raises an InvalidRecord exception.

        Args:
            header: The type of the record.
            record: The record to validate.

        Returns:
            bool: True if the record is valid, False otherwise.

        Raises:
            InvalidRecord: If the record is not valid.
        """

        if header == c_nrbf.RecordTypeEnumeration.SerializationHeaderRecord and (
            record.MajorVersion != 1 or record.MinorVersion != 0
        ):
            # SerializationHeaderRecord: these values MUST be set accordingly
            raise InvalidRecordError("Invalid SerializationHeaderRecord")

        return True


class NRBFRecords:
    """Base class to parse the NRBF records with flow.record.

    Args:
        nrbf: An instance of NRBF with an initialized binary stream object.
    """

    def __init__(self, nrbf: NRBF):
        self.nrbf = nrbf

    def records(self) -> Generator[RecordDescriptor]:
        """Parse the stream and yield records.

        This function parses the stream and yields records as RecordDescriptor objects.

        Yields:
            RecordDescriptor: The parsed record.

        Raises:
            DesctiptorError: If the associated record descriptor is not found for the record.
        """
        for header, record in self.nrbf.parse():
            record_type = header.Type.name

            try:
                descriptor = NRBF_DESCRIPTORS[record_type]
            except KeyError:
                raise DescriptorError(f"Unknown descriptor: {record_type} descriptor not supported")

            record_dict = record._values
            record_dict["type"] = record_type

            if record_type == "BinaryMethodCall":
                record_dict = self._parse_binarymethodcall(record_dict=record_dict)
            elif record_type == "BinaryMethodReturn":
                record_dict = self._parse_binarymethodreturn(record_dict=record_dict)
            elif record_type in [
                "ClassWithMembersAndTypes",
                "SystemClassWithMembersAndTypes",
                "SystemClassWithMembers",
                "ClassWithMembers",
            ]:
                # These records share some fields and can be parsed in the same manner
                record_dict = self._parse_classwithmembers(record_dict=record_dict)
            elif record_type in "BinaryArray":
                record_dict = self._parse_binaryarray(record_dict=record_dict)

            record = descriptor.init_from_dict(record_dict)

            yield record

    def _parse_binarymethodcall(self, record_dict: dict) -> dict:
        """Parses the BinaryMethodCall record and returns a dictionary with the parsed data.

        This function takes a dictionary representing a BinaryMethodCall record, extracts the necessary
        information, and returns a new dictionary with the parsed data. It handles the cases where the
        'CallContext' and 'Args' fields might not be present in the record.

        Args:
            record_dict: The dictionary representing the BinaryMethodCall record.

        Returns:
            A dictionary with the parsed data.
        """

        fixed_dict = record_dict
        fixed_dict["MessageEnum"] = str(record_dict["MessageEnum"]).split(".")[1]
        fixed_dict["MethodName"] = record_dict["MethodName"].Value.String
        fixed_dict["TypeName"] = record_dict["TypeName"].Value.String

        try:
            fixed_dict["CallContext"] = record_dict["CallContext"].Value.String
        except KeyError:
            # Field not present in definition
            pass

        try:
            fixed_dict["Args"] = [arg.Value.String for arg in record_dict["Args"]]
        except KeyError:
            # field not present in definition
            pass

        return fixed_dict

    def _parse_binarymethodreturn(self, record_dict: dict) -> dict:
        """Parses the BinaryMethodReturn record and returns a dictionary with the parsed data.

        This function takes a dictionary representing a BinaryMethodReturn record, extracts the necessary
        information, and returns a new dictionary with the parsed data. It handles the cases where the
        'ReturnValue', 'CallContext', and 'Args' fields might not be present in the record.

        Args:
            record_dict: The dictionary representing the BinaryMethodReturn record.

        Returns:
            A dictionary with the parsed data.
        """

        fixed_dict = record_dict
        fixed_dict["MessageEnum"] = str(record_dict["MessageEnum"]).split(".")[1]

        try:
            fixed_dict["ReturnValue"] = record_dict["ReturnValue"].String
        except KeyError:
            # Field not present in definition
            pass

        try:
            fixed_dict["CallContext"] = record_dict["CallContext"].Value.String
        except KeyError:
            # Field not present in definition
            pass

        try:
            fixed_dict["Args"] = [arg.Value.String for arg in record_dict["Args"]]
        except KeyError:
            # field not present in definition
            pass

        return fixed_dict

    def _parse_classwithmembers(self, record_dict: dict) -> dict:
        """Parses the ClassWithMembers record and returns a dictionary with the parsed data.

        This function takes a dictionary representing a ClassWithMembers record, extracts the necessary
        information, and returns a new dictionary with the parsed data. It handles the case where the
        'BinaryTypeEnum' field might not be present in the record.

        Args:
            record_dict: The dictionary representing the ClassWithMembers record.

        Returns:
            A dictionary with the parsed data.
        """

        fixed_dict = record_dict
        fixed_dict["Name"] = record_dict["Name"].String
        fixed_dict["MemberNames"] = [member.String for member in record_dict["MemberNames"]]

        try:
            fixed_dict["BinaryTypeEnum"] = [
                c_nrbf.BinaryTypeEnumeration(type_enum).name for type_enum in record_dict["BinaryTypeEnum"]
            ]
        except KeyError:
            # Field not present in definition
            pass

        return fixed_dict

    def _parse_binaryarray(self, record_dict: dict) -> dict:
        """Parses the BinaryArray record and returns a dictionary with the parsed data.

        This function takes a dictionary representing a BinaryArray record, extracts the necessary
        information, and returns a new dictionary with the parsed data. It currently does not handle
        the 'AdditionalTypeInfo' field.

        Args:
            record_dict: The dictionary representing the BinaryArray record.

        Returns:
            A dictionary with the parsed data.
        """

        fixed_dict = record_dict
        fixed_dict["BinaryArrayTypeEnum"] = c_nrbf.BinaryArrayTypeEnumeration(record_dict["BinaryArrayTypeEnum"]).name
        fixed_dict["Lengths"] = [length for length in record_dict["Lengths"]]
        fixed_dict["LowerBounds"] = [lowerbound for lowerbound in record_dict["LowerBounds"]]
        fixed_dict["TypeEnum"] = c_nrbf.BinaryTypeEnumeration(record_dict["TypeEnum"]).name
        # TODO: parse the AdditionalTypeInfo field
        return fixed_dict
