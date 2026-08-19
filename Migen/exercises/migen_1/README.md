# Migen exercise 1: Configurable Packet Field Extractor

## Objective

Design a combinational module HeaderParser that receives a raw 32-bit packet word, slices it into distinct sub-fields, identifies active alert flags using a priority encoder, and dynamically extracts a user-selected payload byte.

After your module is complete, test it out with the provided testbench simulation.

### Concepts Covered

- Bit-slicing with migen.genlib.misc.split

- Dynamic multiplexing with migen.genlib.misc.chooser

- Priority encoding with migen.genlib.coding.PriorityEncoder

- Sizing helpers with migen.fhdl.bitcontainer.bits_for


## Specifications

### Input Interface:

raw_packet: Signal(32) (Top-level input packet).

byte_sel: Signal(2) (Selects which payload byte to extract: 0, 1, or 2).

### Sub-field Layout (from LSB to MSB):

valid: 1 bit (raw_packet[0])

prio: 3 bits (raw_packet[1:4])

flags: 4 bits (raw_packet[4:8])

payload: 24 bits (raw_packet[8:32])

### Output:

Each of the packet sub-fields

Index of the highest flag (Signal(2))

A check for "are all flags disabled?" (Signal(1))

Selected byte from the payload (Signal(8))

## Hints:

<details>
<summary>Step 1</summary>
Use split to partition raw_packet into the 4 sub-fields.
</details>

<details>
<summary>Step 2</summary>
Connect flags to a PriorityEncoder(width=4). Expose highest_flag_idx (Signal(2)) and flags_empty (Signal(1)).
</details>

<details>
<summary>Step 3</summary>
Use chooser to route the selected 8-bit byte from payload to selected_byte (Signal(8)).
</details>