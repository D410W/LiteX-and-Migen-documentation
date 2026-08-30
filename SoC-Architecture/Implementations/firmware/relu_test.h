#pragma once

#include <generated/csr.h>
#include <generated/mem.h>

#include <stdarg.h>

#include "printing.h"

#ifndef BRAM_BASE
#define BRAM_BASE SHARED_RAM_BASE
#endif

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