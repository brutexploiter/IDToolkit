# UUID v1

A powerful command-line script for generating, decoding **UUID v1**. This script allows you to extract timestamp, clock sequence, and node information from UUID v1 values, as well as generate UUIDs based on specific parameters.

## Features
- **Decode UUID v1**: Extract timestamp, clock sequence, and node (MAC/random).
- **Generate UUIDs**: Create new UUID v1 values with flexible input options.

## Installation

```bash
# Clone the repository
git clone https://github.com/brutexploiter/IDToolkit.git
cd IDToolkit/uuidv1

# Make the script executable
chmod +x uuidv1.py
```

## Usage
Run the script using:
```bash
python3 uuidv1.py [command] [options]
```

    Command:
    
    decode              Decode a UUID v1 and extract details
    sandwich            Generate all UUIDs between two UUID v1 values
    generate            Generate UUID v1 values based on parameters

### **1. Decode a UUID v1**
Extracts details such as timestamp, clock sequence, and node.
```bash
python3 uuidv1.py decode <UUID>
```
**Example:**
```bash
python3 uuidv1.py decode 55b2e60c-b5a6-11ee-802a-acde48001122
```
**Output:**
```
Timestamp:- 1704505500123456 : 2024-01-05 12:45:00 UTC
Clock Sequence:- 3282
Node (MAC or Random):- acde48001122 : ac:de:48:00:11:22
```

### **2. Generate UUIDs**
Generate UUID v1 values with custom timestamp, clock sequence, and node.
```bash
python3 uuidv1.py generate -t <timestamp> -c <clock_seq> -n <node> [-o output_file]
```
**Example:**
```bash
python3 uuidv1.py generate -t 1704505500 -c 1000 -n ffffffffffff
```

### **3. Generate UUIDs in a Range (Sandwich Mode)**
Generate all UUIDs between two given UUID v1 values.
```bash
python3 uuidv1.py sandwich <UUID1> <UUID2> [-o OUTPUT] [-m MACHINES]
```

## License
This project is open-source and licensed under the [MIT License](LICENSE).
