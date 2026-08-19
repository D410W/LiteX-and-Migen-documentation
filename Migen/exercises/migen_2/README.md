# Migen exercise 2: Circular BRAM Trace Buffer with Post-Trigger Capture

## Objective

Create a module TraceBuffer that continuously stores 16-bit incoming data samples in a circular Block RAM buffer. Upon receiving an external trigger strobe, it continues sampling for $k$ post-trigger clock cycles before halting execution.

After your module is complete, test it out with the provided testbench simulation.

### Concepts Covered

- FPGA RAM primitives using migen.fhdl.specials.Memory

- Sequential state and pointer management using self.sync

- Countdown timing using migen.genlib.misc.WaitTimer

## Specifications

### Module parameters:

`depth=X`, `sample_width=Y`, `post_trigger_cycles=Z`.

### Input Interface:

sample_in: Signal(sample_width) (Data input).

trigger: Signal() (1-cycle pulse marking trigger event).

### Output:

halted: Signal() (Asserts when capture has completed).

halt_address: Signal(max=depth) (Final memory write pointer).

## Hints:

<details>
<summary>Step 1</summary>
Write samples continuously into memory at wr_ptr. Increment wr_ptr every cycle (wrapping at depth-1).
</details>

<details>
<summary>Step 2</summary>
When trigger is asserted, start WaitTimer(t=post_trigger_cycles).
</details>

<details>
<summary>Step 3</summary>
When WaitTimer.done asserts, freeze the write pointer and set halted = 1.
</details>