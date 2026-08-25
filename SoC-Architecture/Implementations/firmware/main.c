#include <generated/csr.h>
#include <generated/mem.h>

#include <stdarg.h>

void isr(void) {}
void litex_startup_init(void) {}

static void uart_putc(char c) {
  while (uart_txfull_read());
  uart_rxtx_write(c);
}

static void print_str(const char *s) {
  while (*s) {
    if (*s == '\n') uart_putc('\r');
    uart_putc(*s++);
  }
}

static void print_dec(int val) {
  if (val < 0) { uart_putc('-'); val = -val; }
  if (val == 0) { uart_putc('0'); return; }
  char buf[11];
  int i = 0;
  while (val > 0) {
    buf[i++] = '0' + (val % 10);
    val /= 10;
  }
  while (i > 0) uart_putc(buf[--i]);
}

static void print_hex(unsigned int val, int digits) {
  for (int i = (digits - 1) * 4; i >= 0; i -= 4) {
    int nibble = (val >> i) & 0xF;
    uart_putc(nibble < 10 ? '0' + nibble : 'a' + nibble - 10);
  }
}

int printf(const char *fmt, ...) {
  va_list ap;
  va_start(ap, fmt);
  while (*fmt) {
    if (*fmt == '%' && *(fmt + 1)) {
      fmt++;
      if (*fmt == 'd')      print_dec(va_arg(ap, int));
      else if (*fmt == 'x') print_hex(va_arg(ap, unsigned int), 8); // 8-digit hex
      else if (*fmt == 's') print_str(va_arg(ap, const char *));
      else if (*fmt == 'c') uart_putc((char)va_arg(ap, int));
      else if (*fmt == '%') uart_putc('%');
    } else {
      if (*fmt == '\n') uart_putc('\r');
      uart_putc(*fmt);
    }
    fmt++;
  }
  va_end(ap);
  return 0;
}

#define BRAM_BASE SHARED_RAM_BASE

int run_relu_test(void) {
    volatile uint32_t *bram = (volatile uint32_t *)BRAM_BASE;
    
    // Define your partition boundaries (e.g., first half input, second half output)
    const uint32_t IN_OFFSET  = 0;
    const uint32_t OUT_OFFSET = 512;
    const uint32_t TEST_SIZE  = 16; // Number of elements to test

    // Phase 1: Write input test vectors to BRAM
    for (uint32_t i = 0; i < TEST_SIZE; i++) {
        bram[IN_OFFSET + i] = i * 2; // Test pattern
    }

    int32_t input = -1;
    int32_t result;

    relu_i_write(input);
    result = relu_o_read();
    printf("ReLU result: %d\n", result);

    return result;
}

int main(void) {
    printf("Testing ReLU accelerator.\n");

    run_relu_test();

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