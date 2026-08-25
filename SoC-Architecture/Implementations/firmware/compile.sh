LITEX_PATH="../../../../litex-repo/litex/litex"
GENERATED="../build/software/include/generated"

cp $GENERATED/output_format.ld .
cp $GENERATED/regions.ld .

riscv64-unknown-elf-gcc -march=rv32i_zicsr -mabi=ilp32 -Os \
  -nostdlib -fno-builtin \
  -Wl,--no-warn-rwx-segments \
  -Tlinker.ld \
  -I../build/software/include \
  -L../build/software/include \
  -I$LITEX_PATH/soc/cores/cpu/vexriscv/ \
  -I$LITEX_PATH/soc/software/include/ \
  $LITEX_PATH/soc/cores/cpu/vexriscv/crt0.S main.c \
  -lgcc \
  -o firmware.elf

# REPLACE 'LITEX_PATH' ABOVE WITH YOUR LITEX REPO PATH

riscv64-unknown-elf-objcopy -O binary firmware.elf firmware.bin