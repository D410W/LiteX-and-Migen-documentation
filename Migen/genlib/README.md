# genlib

migen.genlib is basically Migen's 'standard library', it contains essential pre-built classes commonly used in any design.\
Some key modules inside genlib are:

- fifo : Provides synchronous and asynchronous First-In-First-Out (FIFO) queues.

- fsm : Provides a high-level syntax for describing state machines.

- cdc : Primitives designed to eliminate metastability when transferring signals across different clock trees.

- record : Groups multiple related Signal objects into a single object (similar to a VHDL record). It's heavily used throughout LiteX to define bus interfaces.

- resetsync : Used to solve reset metastability when bringing an FPGA out of reset.

- coding : Encodes active lines to binary numbers and vice-versa.

- roundrobin : Arbiters that grant shared resource access fairly among multiple requesting channels.

- divider : Optimized division modules with control signals and latency configuration.

- misc : Contains small, self-contained hardware modules for common DSP, control, and signal-generation tasks.