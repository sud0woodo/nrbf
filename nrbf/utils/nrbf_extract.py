from __future__ import annotations

import argparse
from io import BytesIO
from typing import TYPE_CHECKING

# External dependencies
from flow.record import RecordWriter

# Local imports
from nrbf.nrbf import NRBF, NRBFRecords

if TYPE_CHECKING:
    from argparse import Namespace

    from nrbf.nrbf import NRBF


def parse_as_records(args: Namespace, nrbf: NRBF):
    """Parses the NRBF records and writes them to a writer or stdout.

    This function takes the parsed arguments and an NRBF object, iterates over the records in the NRBF object,
    and writes each record to a writer or stdout based on the arguments. If a writer is specified, it also
    flushes and closes the writer after all records have been processed.

    Parameters:
        args: The parsed arguments. It should have 'write', 'format', and 'stdout' attributes.
        nrbf: The NRBF object to parse the records from.
    """

    writer = RecordWriter()
    if args.write:
        path = f"{args.format}://{args.write}" if args.format in ["jsonfile", "csvfile", "xlsx"] else args.write
        writer = RecordWriter(path)

    nrbfrecords = NRBFRecords(nrbf=nrbf)
    for record in nrbfrecords.records():
        writer.write(record)

    if writer:
        writer.flush()
        writer.close()


def parse_as_plain(args: Namespace, nrbf: NRBF):
    """Parses the NRBF records and prints them to stdout.

    This function takes the parsed arguments and an NRBF object, iterates over the records in the NRBF object,
    and prints each record to stdout.

    Parameters:
        args: The parsed arguments.
        nrbf: The NRBF object to parse the records from.
    """

    nrbfrecords = NRBFRecords(nrbf=nrbf)
    for record in nrbfrecords.records():
        print(record)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", required=False, help="File containing .NET stream to parse")
    parser.add_argument("--hex", required=False, help="Hex string containing .NET stream to parse")

    subparser = parser.add_subparsers(dest="output_format")

    # Arguments for records
    records_parser = subparser.add_parser("records")
    records_parser.add_argument("--write", required=False, help="Write records to specified file")
    records_parser.add_argument(
        "--format",
        required=False,
        choices=["jsonfile", "csvfile", "xlsx", "records"],
        default="records",
        help="Write records using specified format, supported formats: json, csv, records. [default: records]",
    )
    records_parser.add_argument(
        "--silent", required=False, action="store_true", help="Don't print records to stdout [default: False]"
    )
    records_parser.set_defaults(func=parse_as_records)

    # Arguments for stdout
    stdout_parser = subparser.add_parser("stdout")
    stdout_parser.set_defaults(func=parse_as_plain)

    args = parser.parse_args()

    if not args.output_format:
        parser.print_help()
        exit(1)

    stream = open(args.file, "rb") if args.file else BytesIO(bytes.fromhex(args.hex))
    nrbf = NRBF(stream=stream)

    args.func(args=args, nrbf=nrbf)

    stream.close()


if __name__ == "__main__":
    main()
