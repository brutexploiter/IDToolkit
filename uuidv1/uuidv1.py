#!/usr/bin/env python3

import datetime
import sys
import argparse

def decode_uuid_v1(uuid_str):
    """Decodes a UUID v1 to extract timestamp, clock sequence, and node."""
    try:
        uuid_str = uuid_str.replace("-", "")

        if len(uuid_str) != 32:
            print("Error: Invalid UUID length")
            return
        
        raw_bytes = bytes.fromhex(uuid_str)

        # Extract timestamp
        time_low = int.from_bytes(raw_bytes[0:4], byteorder="big")
        time_mid = int.from_bytes(raw_bytes[4:6], byteorder="big")
        time_high_and_version = int.from_bytes(raw_bytes[6:8], byteorder="big")
        timestamp_raw = ((time_high_and_version & 0x0FFF) << 48) | (time_mid << 32) | time_low
        timestamp = (timestamp_raw - 0x01b21dd213814000) // 10000000
        timestamp_human = datetime.datetime.fromtimestamp(timestamp, datetime.UTC).strftime('%Y-%m-%d %H:%M:%S UTC')

        # Extract clock sequence
        clock_seq = int.from_bytes(raw_bytes[8:10], byteorder="big") & 0x3FFF

        # Extract node
        node_raw = "".join(f"{b:02x}" for b in raw_bytes[10:])
        node_mac = ":".join(f"{b:02x}" for b in raw_bytes[10:])

        print(f"Timestamp:- {timestamp_raw} : {timestamp_human}")
        print(f"Clock Sequence:- {clock_seq}")
        print(f"Node (MAC or Random):- {node_raw} : {node_mac}")

    except ValueError:
        print("Error: Invalid UUID format")

def get_uuid(timestamp, clock_seq, node, save="1"):
    """Reconstructs a UUID v1 from timestamp, clock sequence, and node."""
    hex_timestamp = f"{timestamp:015x}"
    high, mid, low = hex_timestamp[:3], hex_timestamp[3:7], hex_timestamp[7:]
    return f"{low}-{mid}-{save}{high}-{clock_seq:04x}-{node}"

def parse_value(value, is_hex=False):
    """Parses input values for range, single, or multiple values. Supports hex for nodes."""
    if "-" in value:
        start, end = value.split("-")
        return range(int(start, 16) if is_hex else int(start), int(end, 16) if is_hex else int(end) + 1)
    elif "," in value:
        return [int(v, 16) if is_hex else int(v) for v in value.split(",")]
    else:
        return [int(value, 16) if is_hex else int(value)]

def generate_uuids(timestamps, clock_sequences, nodes, output_file=None):
    """Generates UUIDs efficiently using a generator."""
    def uuid_generator():
        for timestamp in timestamps:
            for clock_seq in clock_sequences:
                for node in nodes:
                    yield get_uuid(timestamp, clock_seq, node)

    if output_file:
        with open(output_file, "w") as f:
            for uuid in uuid_generator():
                f.write(uuid + "\n")
        print(f"\nUUIDs saved to {output_file}")
    else:
        for uuid in uuid_generator():
            print(uuid)

def get_info(uuid_str):
    """Extracts timestamp, clock sequence, and node from UUID v1."""
    uuid_str = uuid_str.replace("-", "")
    raw_bytes = bytes.fromhex(uuid_str)

    # Extract timestamp
    time_low = int.from_bytes(raw_bytes[0:4], byteorder="big")
    time_mid = int.from_bytes(raw_bytes[4:6], byteorder="big")
    time_high_and_version = int.from_bytes(raw_bytes[6:8], byteorder="big")
    timestamp = ((time_high_and_version & 0x0FFF) << 48) | (time_mid << 32) | time_low

    # Extract clock sequence
    clock_seq = int.from_bytes(raw_bytes[8:10], byteorder="big") & 0x3FFF

    # Extract node
    node = "".join(f"{b:02x}" for b in raw_bytes[10:])

    # Save version byte
    save = f"{(time_high_and_version >> 12):x}"

    return timestamp, clock_seq, node, save

def generate_uuids_file(uuid1, uuid2, filename="uuids.txt"):
    """Generates all possible UUIDs in the range between UUID1 and UUID2 and saves them to a file."""
    t1, clock_seq, node, save = get_info(uuid1)
    t2, _, _, _ = get_info(uuid2)

    with open(filename, "w") as f:
        for timestamp in range(t1, t2 + 1):
            f.write(get_uuid(timestamp, clock_seq, node, save) + "\n")
    
    print(f"UUIDs saved to {filename}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UUID v1 Tool - Generate, decrypt, and manipulate UUID v1 values.")
    subparsers = parser.add_subparsers(dest="command")

    # Decrypt Mode
    decrypt_parser = subparsers.add_parser("decrypt", help="Decrypt a UUID v1 and extract details",usage="uuidv1.py decrypt uuid")
    decrypt_parser.add_argument("uuid", help="The UUID v1 to decrypt")

    # Sandwich Mode
    sandwich_parser = subparsers.add_parser("sandwich", help="Generate all UUIDs between two UUID v1 values", usage="uuidv1.py sandwich uuid1 uuid2 [-o OUTPUT] [-m MACHINES]")
    sandwich_parser.add_argument("uuid1", help="Starting UUID v1")
    sandwich_parser.add_argument("uuid2", help="Ending UUID v1")
    sandwich_parser.add_argument("-m", "--machines", help="Comma-separated machine names")
    sandwich_parser.add_argument("-o", "--output", help="Output file to save generated UUIDs (default: uuids.txt)")

    # Generate Mode
    generate_parser = subparsers.add_parser("generate", help="Generate UUID v1 values based on parameters",usage="uuidv1.py generate -t TIMESTAMP -c CLOCK -n NODE [-o OUTPUT]")
    generate_parser.add_argument("-t", "--timestamp", required=True, help="Timestamp (range, single, or multiple values)")
    generate_parser.add_argument("-c", "--clock", required=True, help="Clock sequence (range, single, or multiple values)")
    generate_parser.add_argument("-n", "--node", required=True, help="Node (range, single, or multiple values)")
    generate_parser.add_argument("-o", "--output", help="Output file to save generated UUIDs")

    args = parser.parse_args()

    if args.command == "decrypt":
        decode_uuid_v1(args.uuid)

    elif args.command == "sandwich":
        if args.machines:
            machines = args.machines.split(",")
            for machine in machines:
                output_filename = f"{machine}-{args.output}" if args.output else f"{machine}-uuids.txt"
                machine_uuid1 = args.uuid1[:24] + machine  
                machine_uuid2 = args.uuid2[:24] + machine
                generate_uuids_file(machine_uuid1, machine_uuid2, filename=output_filename)
        else:
            generate_uuids_file(args.uuid1, args.uuid2, filename=args.output if args.output else "uuids.txt")

    elif args.command == "generate":
        timestamps = parse_value(args.timestamp)
        clock_sequences = parse_value(args.clock)
        nodes = [f"{n:012x}" for n in parse_value(args.node, is_hex=True)]  

        generate_uuids(timestamps, clock_sequences, nodes, output_file=args.output)

    else:
        parser.print_help()
