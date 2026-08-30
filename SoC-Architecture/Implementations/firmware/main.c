#include <generated/csr.h>
#include <generated/mem.h>

#include <stdarg.h>

void isr(void) {}
void litex_startup_init(void) {}

#define BRAM_BASE SHARED_RAM_BASE

#include "printing.h"
#include "relu_test.h"
#include "maxpooling_test.h"

static inline uint32_t read_cycles(void) {
  uint32_t cycles;
  asm volatile ("rdcycle %0" : "=r"(cycles));
  return cycles;
}

int main(void) {
  printf("Testing MaxPooling accelerator.\n");

  // run_relu_test();
  run_maxpooling_test();

  printf("Finished test.\n");

  // exit simulation
  #ifdef CSR_CTRL_FINISH_ADDR
  ctrl_finish_write(1);
  #endif
  
  // if running on physical hardware
  while (1) {
    #if defined(__riscv)
    __asm__ volatile("wfi"); // "wait for interrupt"
    #endif
  }

  return 0;
}