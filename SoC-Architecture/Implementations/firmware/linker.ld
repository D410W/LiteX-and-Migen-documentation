INCLUDE output_format.ld
INCLUDE regions.ld

SECTIONS
{
    .text :
    {
        _ftext = .;
        KEEP(*(.text.start))
        *(.text .stub .text.* .gnu.linkonce.t.*)
        _etext = .;
    } > main_ram

    .rodata :
    {
        . = ALIGN(4);
        _frodata = .;
        *(.rodata .rodata.* .gnu.linkonce.r.*)
        *(.srodata .srodata.*)
        _erodata = .;
    } > main_ram

    .data :
    {
        . = ALIGN(4);
        _fdata = .;
        *(.data .data.* .gnu.linkonce.d.*)
        *(.sdata .sdata.* .gnu.linkonce.s.*)
        _edata = .;
    } > main_ram

    .bss :
    {
        . = ALIGN(4);
        _fbss = .;
        *(.bss .bss.* .gnu.linkonce.b.*)
        *(.sbss .sbss.* .gnu.linkonce.sb.*)
        *(COMMON)
        *(.scommon)
        _ebss = .;
    } > main_ram
}

PROVIDE(_fdata_rom = _fdata);
PROVIDE(_fstack = (ORIGIN(main_ram) + LENGTH(main_ram) - 16) & ~0xF);