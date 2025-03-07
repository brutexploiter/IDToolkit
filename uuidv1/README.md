# UUID v1

A powerful command-line script for generating, decoding, and manipulating **UUID v1** values according to [RFC 4122](https://datatracker.ietf.org/doc/html/rfc4122). It allows extracting detailed timestamp, clock sequence, and node information from a UUID v1, as well as generating new UUIDs based on custom parameters.

## Features

- **Decode UUID v1**: Extract and display detailed fields including variant, time_low, time_mid, time_hi_and_version, clock_seq_hi_and_reserved, clock_seq_low, node, timestamp, and clock sequence.
- **Generate UUIDs**: Create new UUID v1 values using raw parameters (timestamp, clock sequence, node) with the ability to specify the variant.
- **Sandwich Mode**: Generate a sequence of UUID v1 values between two given UUIDs, with optional machine-specific adjustments and output file saving.

## Installation

Clone the repository and make the script executable:

```bash
# Clone the repository
git clone https://github.com/brutexploiter/IDToolkit.git
cd IDToolkit/uuidv1

# Make the script executable
chmod +x uuidv1.py
```

## Usage
```bash
python3 uuidv1.py [command] [options]
```

    Command:
    
    decode              Decode a UUID v1 and extract details
    sandwich            Generate all UUIDs between two UUID v1 values
    generate            Generate UUID v1 values based on parameters

### **1. Decode a UUID v1**
Extracts details such as the variant, time_low, time_mid, time_hi_and_version, clock sequence, node, timestamp (raw and human-readable), and the raw clock sequence.
```bash
python3 uuidv1.py decode <UUID>
```
**Example:**
```bash
python3 uuidv1.py decode 55b2e60c-b5a6-11ee-802a-acde48001122
```
**Output:**
```
Field                       Value
-----                       -----
Variant                     RFC4122
time_low                    55b2e60c
time_mid                    b5a6
time_hi_and_version         11ee
clock_seq_hi_and_reserved   80
clock_seq_low               2a
node                        acde48001122 (ac:de:48:00:11:22)
Timestamp                   139248364502050316 (2024-01-18 02:07:30 UTC)
Clock Sequence              42
```

### **2. Generate UUIDs**
Generate UUID v1 values with custom parameters. You supply a timestamp (or range), a raw 14-bit clock sequence (or range), a node value in hexadecimal (or range), and a variant.
```bash
python3 uuidv1.py generate -t <timestamp> -c <clock> -n <node> -v <variant>
```
```bash
Options:
  -t, --timestamp   Timestamp value(s) in 100-nanosecond units (range, single, or comma-separated)
  -c, --clock       Raw 14-bit clock sequence value(s) (range, single, or comma-separated)
  -n, --node        Node value(s) in hexadecimal (range, single, or comma-separated)
  -v, --variant     Variant for generated UUIDs. Options: NCS, RFC4122, Microsoft, Future (default: RFC4122)
  -o, --output      Output file to save generated UUIDs
```
**Example:**
```bash
python3 uuidv1.py generate -t 1704505500 -c 1000 -n ffffffffffff
```
### **3. Generate UUIDs in a Range (Sandwich Mode)**
Generate all UUID v1 values between two specified UUIDs. Optionally, you can specify machine names for machine-specific generation and an output file.
```bash
python3 uuidv1.py sandwich <UUID1> <UUID2> [option]
```
```bash
Options:
  -m, --machines    Comma-separated machine names for machine-specific generation
  -o, --output      Output file to save generated UUIDs
```
**Example:**
```bash
python3 uuidv1.py sandwich 55b2e60c-b5a6-11ee-802a-acde48001122 55b2e612-b5a6-11ee-802a-acde48001122
```
## License
This project is licensed under the Apache License 2.0 - see the [LICENSE](https://github.com/brutexploiter/IDToolkit/blob/main/LICENSE) file for details
