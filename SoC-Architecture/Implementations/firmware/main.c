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

static inline uint32_t read_cycles(void) {
    uint32_t cycles;
    asm volatile ("rdcycle %0" : "=r"(cycles));
    return cycles;
}

void run_relu_test(void) {
    volatile int32_t *bram = (volatile int32_t *)BRAM_BASE;
    volatile int16_t *bram16 = (volatile int16_t*)bram;
    
    // partition boundaries
    const uint32_t IN_OFFSET = 0;
    const uint32_t OUT_OFFSET = 512;
    const uint32_t TEST_SIZE = 16; // number of elements to test
    const uint32_t ELEMENT_SIZE = sizeof(int32_t);

    // writing input test vectors to BRAM
    printf("Input: ");
    for (uint32_t i = 0; i < TEST_SIZE; i++) {
      uint32_t index = 2 * (IN_OFFSET + i);

      bram16[index] = (i % 2 == 0) ? (int16_t)(-i * 2) : (int16_t)(i * 3);
      bram16[index + 1] = (i % 2 == 0) ? (int16_t)(-i * 7) : (int16_t)(i * 11);

      printf("(%d, %d) ", bram16[index], bram16[index + 1]);
    }
    printf("\n");
    
    dma_writer_base_write((uint32_t)&bram[OUT_OFFSET]);
    dma_writer_length_write(TEST_SIZE * ELEMENT_SIZE);
    dma_writer_enable_write(1);

    // arm reader (source)
    dma_reader_base_write((uint32_t)&bram[IN_OFFSET]);
    dma_reader_length_write(TEST_SIZE * ELEMENT_SIZE);
    dma_reader_enable_write(1);

    // wait for completion
    while (!dma_writer_done_read());

    for (volatile int i = 0; i < 10000; ++i) {}

    printf("Output: ");
    for (uint32_t i = 0; i < TEST_SIZE; i++) {
      uint32_t index = 2 * (OUT_OFFSET + i);
      printf("(%d, %d) ", bram16[index], bram16[index + 1]);
    }
    printf("\n");

    return;
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