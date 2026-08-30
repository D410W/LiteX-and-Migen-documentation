#pragma once

#include <generated/csr.h>
#include <generated/mem.h>

#include <stdarg.h>

#include "printing.h"

#ifndef BRAM_BASE
#define BRAM_BASE SHARED_RAM_BASE
#endif

void run_maxpooling_test(void) {
  volatile int32_t *bram = (volatile int32_t *)BRAM_BASE;
  
  // partition boundaries
  const uint32_t IN_OFFSET = 0;
  const uint32_t OUT_OFFSET = 512;

  const uint32_t M_WIDTH = 8;
  const uint32_t M_HEIGHT = 8;
  const uint32_t KERNEL_SIZE = 2;
  const uint32_t KERNEL_AREA = KERNEL_SIZE * KERNEL_SIZE;
  
  const uint32_t INPUT_SIZE = M_WIDTH * M_HEIGHT; // number of elements to test
  const uint32_t OUTPUT_SIZE = INPUT_SIZE / KERNEL_AREA;
  const uint32_t ELEMENT_SIZE = sizeof(int32_t);

  // writing input matrix to BRAM
  printf("Input:\n");
  for (uint32_t i = 0; i < INPUT_SIZE; i++) {
    bram[IN_OFFSET + i] = (i % 2 == 0) ? (int32_t)(-i * 2) : (int32_t)(i * 3);

    printf("%d ", bram[IN_OFFSET + i]);
    if ((i+1) % M_WIDTH == 0) {
      printf("\n");
    }
  }
  printf("\n");

  maxpooling_csr_width_write(8);
  maxpooling_csr_height_write(8);
  
  // source
  dma_writer_base_write((uint32_t)&bram[OUT_OFFSET]);
  dma_writer_length_write(OUTPUT_SIZE * ELEMENT_SIZE);
  dma_writer_enable_write(1);

  // arm reader (sink)
  dma_reader_base_write((uint32_t)&bram[IN_OFFSET]);
  dma_reader_length_write(INPUT_SIZE * ELEMENT_SIZE);
  dma_reader_enable_write(1);

  // wait for completion
  while (!dma_reader_done_read());
  printf("DMA Reader finished.\n");

  while (!dma_writer_done_read());
  printf("DMA Writer finished.\n");

  dma_reader_enable_write(0);
  dma_writer_enable_write(0);
  
  printf("Output:\n");
  for (uint32_t i = 0; i < OUTPUT_SIZE; i++) {
    printf("%d ", bram[OUT_OFFSET + i]);
    if ((i+1) % (M_WIDTH/KERNEL_SIZE) == 0) {
      printf("\n");
    }
  }
  printf("\n");

  return;
}