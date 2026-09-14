# Study Folder

This folder contains materials to study and get knowledge about basic computing components like UCP, RAM and SRAM memory, chip, SoCs, etc. It covers from basic concepts like digital logic till microprocessors and computer architecture. We really recommend you study this material before move to the next folders and dive into the project. Furthermore, we also recommend install the tools and practice the subjects you study here, gaining insights and getting prepared to contribute to the project.

# What is a computer?

A computer is any device that is able to **receive, store, compute and show** data. Examples of computers are: a simple hand calculator, a personal computer, a smartphone, etc. Their main processors and other chips are made using logic circuits (layer above physical transistors). In summary, they are built using a set of logic gates, which are a set of transistors in reality. In this project we are working only with digital logic, so transistos will not be so much explored. 

# Basic logic gates

## And gate

The and gate is one of the basic building blocks of the digital systems. It is made of inputs, output and logic. The output signal will be 1 if all inputs are 1, 0 in another case. The figure below show The and gate, its logic and the set of transistors used to build this logic gate.

![And gate](images/andgate.png)


## Data bus

A data bus is a communication system used to exchange data between different componentes inside a computer (like data being transferred between processor and mother board). There are 3 kinds of data bus: control bus, address bus and data bus. Image below show a schematich.

![Computer bus](images/computerBus.webp)

### Address bus

It is a set of tracks (wires) used to identify blocks of memory, locating the right memory address. It transports memory address used by the processor to access these address, writting or reading dada from them. It is an unidirectional bus (only one direction).

### Data bus

Set of tracks used to send/receive data from one component to another, like from processor and memory or I/O devices. It is a bidirectional bus, so data can be sent and received by same bus.

### Control bus

Set of tracks used to transport control and time data between the UCP and other devices. 
