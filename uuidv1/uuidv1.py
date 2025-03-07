#!/usr/bin/env python3

import datetime
import sys
import argparse

# Define custom help texts.
custom_main_help = """
Usage:
  uuidv1.py <command> [option]

Commands:
  decode      Decode a UUID v1 and extract details
  sandwich    Generate all UUIDs between two UUID v1 values
  generate    Generate UUID v1 values based on parameters

Options:
  -h, --help  Display this help message
"""
custom_decode_help = """
Usage:
  uuidv1.py decode <uuid>
"""
custom_sandwich_help = """
Usage:
  uuidv1.py sandwich <uuid1> <uuid2> [option]

Options:
  -m, --machines    Comma-separated machine names for machine-specific generation
  -o, --output      Output file to save generated UUIDs
"""
custom_generate_help = """
Usage:
  uuidv1.py generate -t <timestamp> -c <clock> -n <node> -v <variant>

Parameters:
  -t, --timestamp   Timestamp value(s) in 100-nanosecond units (range, single, or comma-separated)
  -c, --clock       Raw 14-bit clock sequence value(s) (range, single, or comma-separated)
  -n, --node        Node value(s) in hexadecimal (range, single, or comma-separated)
  -v, --variant     Variant for generated UUIDs. Options: NCS, RFC4122, Microsoft, Future (default: RFC4122)
  -o, --output      Output file to save generated UUIDs
"""

# Create the main parser.
parser = argparse.ArgumentParser(usage=custom_main_help, add_help=False,
                                 formatter_class=argparse.RawTextHelpFormatter)
# Override print_help to only show our custom text.
parser.print_help = lambda: sys.stdout.write(custom_main_help)
parser.add_argument("-h", "--help", action="help", help="Display this help message and exit.")

subparsers = parser.add_subparsers(dest="command", metavar="")

# Create decode subcommand.
decode_parser = subparsers.add_parser(
    "decode",
    usage="uuidv1.py decode <uuid>",
    add_help=False,
    formatter_class=argparse.RawTextHelpFormatter
)
decode_parser.add_argument("uuid", help="The UUID v1 to decode.")
decode_parser.add_argument("-h", "--help", action="help", help="Display this help message and exit.")
decode_parser.print_help = lambda: sys.stdout.write(custom_decode_help)
decode_parser.epilog = custom_decode_help

# Create sandwich subcommand.
sandwich_parser = subparsers.add_parser(
    "sandwich",
    usage="uuidv1.py sandwich <uuid1> <uuid2> [-m MACHINES] [-o OUTPUT]",
    add_help=False,
    formatter_class=argparse.RawTextHelpFormatter
)
sandwich_parser.add_argument("uuid1", help="Starting UUID v1.")
sandwich_parser.add_argument("uuid2", help="Ending UUID v1.")
sandwich_parser.add_argument("-m", "--machines", help="Comma-separated machine names.")
sandwich_parser.add_argument("-o", "--output", help="Output file; if provided, UUIDs are saved and not printed.")
sandwich_parser.add_argument("-h", "--help", action="help", help="Display this help message and exit.")
sandwich_parser.print_help = lambda: sys.stdout.write(custom_sandwich_help)
sandwich_parser.epilog = custom_sandwich_help

# Create generate subcommand.
generate_parser = subparsers.add_parser(
    "generate",
    usage="uuidv1.py generate -t <TIMESTAMP> -c <CLOCK> -n <NODE> [-v VARIANT] [-o OUTPUT]",
    add_help=False,
    formatter_class=argparse.RawTextHelpFormatter
)
generate_parser.add_argument("-t", "--timestamp", required=True,
                             help="Timestamp (range, single, or comma-separated).")
generate_parser.add_argument("-c", "--clock", required=True,
                             help="Raw 14-bit clock sequence value (range, single, or comma-separated).")
generate_parser.add_argument("-n", "--node", required=True,
                             help="Node value in hex (range, single, or comma-separated).")
generate_parser.add_argument("-v", "--variant", default="RFC4122",
                             help="Variant for generated UUIDs. Options: NCS, RFC4122, Microsoft, Future (default: RFC4122).")
generate_parser.add_argument("-o", "--output", help="Output file to save generated UUIDs.")
generate_parser.add_argument("-h", "--help", action="help", help="Display this help message and exit.")
generate_parser.print_help = lambda: sys.stdout.write(custom_generate_help)
generate_parser.epilog = custom_generate_help

args = parser.parse_args()

def decode_uuid_v1(uuid_str):
    try:
        # Remove hyphens and validate length
        uuid_str = uuid_str.replace("-", "")
        if len(uuid_str) != 32:
            print("Error: Invalid UUID length")
            return

        # Convert hex string to bytes.
        raw_bytes = bytes.fromhex(uuid_str)
        time_low_int = int.from_bytes(raw_bytes[0:4], byteorder="big")
        time_mid_int = int.from_bytes(raw_bytes[4:6], byteorder="big")
        time_hi_and_version_int = int.from_bytes(raw_bytes[6:8], byteorder="big")
        clock_seq_hi_and_reserved_int = raw_bytes[8]
        clock_seq_low_int = raw_bytes[9]
        node_bytes = raw_bytes[10:]

        # Format fields as hex strings.
        time_low_str = f"{time_low_int:08x}"
        time_mid_str = f"{time_mid_int:04x}"
        time_hi_and_version_str = f"{time_hi_and_version_int:04x}"
        clock_seq_hi_and_reserved_str = f"{clock_seq_hi_and_reserved_int:02x}"
        clock_seq_low_str = f"{clock_seq_low_int:02x}"
        node_str = "".join(f"{b:02x}" for b in node_bytes)
        node_mac = ":".join(f"{b:02x}" for b in node_bytes)

        # Determine variant.
        cshr = clock_seq_hi_and_reserved_int
        if (cshr & 0x80) == 0:
            variant_str = "NCS"
        elif (cshr & 0xC0) == 0x80:
            variant_str = "RFC4122"
        elif (cshr & 0xE0) == 0xC0:
            variant_str = "Microsoft"
        else:
            variant_str = "Future"

        # Compute the 60-bit timestamp.
        timestamp_raw = ((time_hi_and_version_int & 0x0FFF) << 48) | (time_mid_int << 32) | time_low_int
        timestamp_seconds = (timestamp_raw - 0x01b21dd213814000) // 10000000
        timestamp_human = datetime.datetime.fromtimestamp(timestamp_seconds, datetime.UTC).strftime('%Y-%m-%d %H:%M:%S UTC')

        # Get the clock sequence as a 14-bit integer.
        clock_seq_int = int.from_bytes(raw_bytes[8:10], byteorder="big") & 0x3FFF

        col_width = 28
        print(f"{'Field'.ljust(col_width)}Value")
        print(f"{'-'*5:<{col_width}}{'-'*5}")
        print(f"{'Variant'.ljust(col_width)}{variant_str}")
        print(f"{'time_low'.ljust(col_width)}{time_low_str}")
        print(f"{'time_mid'.ljust(col_width)}{time_mid_str}")
        print(f"{'time_hi_and_version'.ljust(col_width)}{time_hi_and_version_str}")
        print(f"{'clock_seq_hi_and_reserved'.ljust(col_width)}{clock_seq_hi_and_reserved_str}")
        print(f"{'clock_seq_low'.ljust(col_width)}{clock_seq_low_str}")
        print(f"{'node'.ljust(col_width)}{node_str} ({node_mac})")
        print(f"{'Timestamp'.ljust(col_width)}{timestamp_raw} ({timestamp_human})")
        print(f"{'Clock Sequence'.ljust(col_width)}{clock_seq_int}")
    except ValueError:
        print("Error: Invalid UUID format")

def get_info(uuid_str):
    uuid_str = uuid_str.replace("-", "")
    raw_bytes = bytes.fromhex(uuid_str)
    time_low = int.from_bytes(raw_bytes[0:4], byteorder="big")
    time_mid = int.from_bytes(raw_bytes[4:6], byteorder="big")
    time_hi_and_version = int.from_bytes(raw_bytes[6:8], byteorder="big")
    timestamp = ((time_hi_and_version & 0x0FFF) << 48) | (time_mid << 32) | time_low
    clock_seq = int.from_bytes(raw_bytes[8:10], byteorder="big") & 0x3FFF
    node = "".join(f"{b:02x}" for b in raw_bytes[10:])
    return timestamp, clock_seq, node

def get_uuid(timestamp, clock_seq, node, variant="RFC4122", version=1):
    time_low = timestamp & 0xffffffff
    time_mid = (timestamp >> 32) & 0xffff
    time_hi = (timestamp >> 48) & 0x0fff
    time_hi_and_version = (version << 12) | time_hi
    cs = clock_seq & 0x3FFF
    cs_low = cs & 0xff
    cs_hi = (cs >> 8) & 0x3F
    variant_upper = variant.upper()
    if variant_upper == "NCS":
        cs_hi = cs_hi | 0x40
    elif variant_upper == "RFC4122":
        cs_hi = cs_hi | 0x80
    elif variant_upper == "MICROSOFT":
        cs_hi = cs_hi | 0xC0
    elif variant_upper == "FUTURE":
        cs_hi = cs_hi | 0xE0
    else:
        cs_hi = cs_hi | 0x80
    clock_seq_field = f"{cs_hi:02x}{cs_low:02x}"
    return f"{time_low:08x}-{time_mid:04x}-{time_hi_and_version:04x}-{clock_seq_field}-{node}"

def parse_value(value, is_hex=False):
    if "-" in value:
        start, end = value.split("-")
        return range(int(start, 16) if is_hex else int(start),
                     (int(end, 16) if is_hex else int(end)) + 1)
    elif "," in value:
        return [int(v, 16) if is_hex else int(v) for v in value.split(",")]
    else:
        return [int(value, 16) if is_hex else int(value)]

def generate_uuids(timestamps, clock_sequences, nodes, variant, output_file=None):
    def uuid_generator():
        for timestamp in timestamps:
            for clock_seq in clock_sequences:
                for node_hex in nodes:
                    yield get_uuid(timestamp, clock_seq, node_hex, variant=variant)
    if output_file:
        with open(output_file, "w") as f:
            for uuid_val in uuid_generator():
                f.write(uuid_val + "\n")
    else:
        for uuid_val in uuid_generator():
            print(uuid_val)

def generate_uuids_file(uuid1, uuid2, filename="uuids.txt", quiet=False):
    t1, clock_seq, node = get_info(uuid1)
    t2, _, _ = get_info(uuid2)
    with open(filename, "w") as f:
        for ts in range(t1, t2 + 1):
            f.write(get_uuid(ts, clock_seq, node) + "\n")
    if not quiet:
        print(f"UUIDs saved to {filename}")

if args.command == "decode":
    decode_uuid_v1(args.uuid)
elif args.command == "sandwich":
    if args.machines:
        machines = args.machines.split(",")
        for machine in machines:
            if args.output:
                output_filename = f"{machine}-{args.output}"
                machine_uuid1 = args.uuid1[:24] + machine
                machine_uuid2 = args.uuid2[:24] + machine
                generate_uuids_file(machine_uuid1, machine_uuid2, filename=output_filename, quiet=True)
            else:
                machine_uuid1 = args.uuid1[:24] + machine
                machine_uuid2 = args.uuid2[:24] + machine
                t1, cs, node = get_info(machine_uuid1)
                t2, _, _ = get_info(machine_uuid2)
                for ts in range(t1, t2 + 1):
                    print(get_uuid(ts, cs, node))
    else:
        if args.output:
            generate_uuids_file(args.uuid1, args.uuid2, filename=args.output, quiet=True)
        else:
            t1, cs, node = get_info(args.uuid1)
            t2, _, _ = get_info(args.uuid2)
            for ts in range(t1, t2 + 1):
                print(get_uuid(ts, cs, node))
elif args.command == "generate":
    timestamps = parse_value(args.timestamp)
    clock_sequences = parse_value(args.clock)
    nodes = [f"{n:012x}" for n in parse_value(args.node, is_hex=True)]
    generate_uuids(timestamps, clock_sequences, nodes, args.variant, output_file=args.output)
else:
    parser.print_help()
