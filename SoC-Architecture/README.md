# LiteX & Migen Vision Accelerator Co-Design

A progressive curriculum covering digital hardware design and System-on-Chip (SoC) construction, from register-transfer logic in **Migen** to building a DMA-driven 2D convolution/vision accelerator integrated with a 32-bit RISC-V softcore using **LiteX**.

## Architectural Motivation

Real-time 2D spatial filtering (such as Sobel edge detection or Gaussian blur) requires $K \times K$ pixel lookups per output pixel. 

- **The Problem (CPU Bottleneck):** Having a softcore CPU read pixels from off-chip DRAM across a shared bus creates severe memory contention and stalls the processor.
- **The Solution (Hardware/Software Co-Design):** 
  - **Control Plane:** The CPU only coordinates jobs, configures image dimensions/kernel weights via memory-mapped **CSRs**, and sleeps until an **IRQ** fires.
  - **Data Plane:** Autonomous **DMA engines** stream raw raster lines into on-chip **Block RAM (BRAM) line buffers**, reconstructing $3 \times 3$ sliding windows on-the-fly and processing 1 pixel per clock cycle at full line rate.

## Roadmap

| Phase | Focus | Core Concepts | Key Deliverable |
| :--- | :--- | :--- | :--- |
| **01. Foundations & Toolchain** | Environment setup & flow | LiteX/Migen setup, Verilator, Yosys/Vivado | Working simulation & LED blinker |
| **02. LiteX SoC Architecture** | System integration | `SoCCore`, Wishbone/AXI interconnect, VexRiscv | Bootable RISC-V SoC with BIOS |
| **03. Control Plane (CSRs)** | Hardware/software interface | `CSRStorage`, `CSRStatus`, interrupts, `csr.h` | Peripheral driven by bare-metal C |
| **04. Data Plane (DMA & IP)** | High-throughput streaming | LiteDRAM, `stream.Endpoint`, DMA engines | Bulk memory-to-FIFO streaming |
| **05. Custom Accelerator** | Applied Capstone | Line buffers, convolution/DSP pipeline | Hardware vision filter vs. C model |

## System Architecture

The SoC architecture decouples low-bandwidth control orchestration from high-bandwidth streaming dataflow, eliminating CPU bus contention during heavy processing.

### 1. Control Plane (CPU & CSRs)
- **RISC-V Softcore (VexRiscv):** Runs bare-metal C firmware to configure frame buffer pointers and launch acceleration batches.
- **CSR Bus (Control & Status Registers):**
  - `CSRStorage`: CPU-writable registers for image width, height, filter coefficients, base source/destination addresses, and the `start` pulse.
  - `CSRStatus`: Read-only telemetry registers exposing busy flags and cycle-accurate execution counters.
  - `IRQ`: Hardware interrupt line asserted upon frame completion to wake the CPU.

### 2. Data Plane (Memory & DMA)
- **Main Memory (LiteDRAM):** Stores raw frame buffers and processed output images in off-chip DRAM.
- **DMA Reader:** Autonomously fetches sequential blocks from DRAM and converts them into point-to-point streaming transactions (`valid` / `ready` handshake).
- **DMA Writer:** Ingests the processed output stream and commits packed words back into destination DRAM buffer.


### 3. Accelerator Pipeline (BRAM & DSP Core)
- **Line Buffers (On-Chip BRAM):** Buffers incoming 1D raster-scan rows in dual-port FPGA Block RAM to build real-time $K \times K$ 2D spatial windows on-the-fly.
- **Compute Engine:** Fully pipelined arithmetic datapath performing mathematical transformations (e.g., Sobel convolution) with single-cycle throughput.
- **Elastic Output FIFO:** Absorbs write-side DRAM bus latency and arbitration jitter to prevent stalling the internal pipeline.

## Directory Structure

SoC/ \
├── 01_foundations/         # Toolchain scripts & blinker \
├── 02_litex_soc/           # Base SoCCore targets & memory maps \
├── 03_control_plane/       # CSR peripherals & bare-metal C drivers \
├── 04_data_plane/          # DMA streaming pipelines & LiteDRAM integration \
├── 05_custom_accelerator/  # Capstone DSP/vision accelerator & benchmark tests \
└── Implementations/        # Reference implementations of the entire vision accelerator structure
