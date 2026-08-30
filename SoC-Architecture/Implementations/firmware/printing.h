#pragma once

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