# Implementations

This folder implements the explored topics into an SoC with accelerator 'Migen Modules' for 4 chosen kernels in the `kernel_implementations` folder.

Each kernel implementation is thoroughly tested through the SoC's own firmware, with output to the console with the 'serial2console' LiteX module.

### Firmware code & compilation

The folder `firmware` contains the firmware code and compilation script. You should replace the script's variable with your own LiteX cloned-repo path.

### Simulating the LiteX design

Simply compile the bare-metal C firmware and run `simulation.py`, which imports the `soc.py` SoC design and runs it with controlled settings.

```bash
cd firmware/

./compile.sh

cd ..

python simlation.py --kernel firmware/firmware.bin
```