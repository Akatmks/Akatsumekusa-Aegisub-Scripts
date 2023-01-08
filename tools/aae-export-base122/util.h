#ifndef LIBBASE_122_UTIL_H
#define LIBBASE_122_UTIL_H

#include <assert.h>
#include <stddef.h> /* for size_t */

typedef struct {
  const unsigned char *in;
  size_t len;
  size_t curBit;
} bitreader_t;

/* bitreader_read reads nbits bits from reader.
 * nbits must be [1,8].
 * out is set to the output bits starting from the right. The left most bits (if any) are set to 0.
 * Example: read 3 bits of input 11111111. *out is initially 01010101. Results in *out set to
 * 00000111.
 * Returns the number of bits read.
 */
static size_t bitreader_read(bitreader_t *reader, size_t nbits, unsigned char *out) {

  /* Do not read more bits than stored. */
  size_t bitLen = reader->len * 8;
  size_t maxNbits = bitLen - reader->curBit;
  size_t firstByteIndex;
  size_t firstByteCurBit;
  unsigned short twoBytes;
  unsigned char mask;

  assert(nbits > 0);
  assert(nbits <= 8);

  if (nbits > maxNbits) {
    nbits = maxNbits;
  }

  if (nbits == 0) {
    *out = 0;
    return 0;
  }

  /* Example of reading 6 bits:
   *
   * Read two bytes. Use 0 as second byte if only one byte is available.
   *
   * abcdefgh ijklmnop
   *    ^
   *    firstByteCurBit
   *
   * Shift right until only nbits requested remain.
   *
   * 0000000a bcdefghi
   *
   * Mask the second byte with nbits of 1's.
   *
   * 00000000 00defghi
   *
   * Output the second byte.
   */

  firstByteIndex = reader->curBit / 8;
  firstByteCurBit = reader->curBit % 8;
  twoBytes = reader->in[firstByteIndex];
  twoBytes = (unsigned short)(twoBytes << 8);
  if (firstByteIndex + 1 < reader->len) {
    size_t secondByteIndex = firstByteIndex + 1;
    twoBytes = (unsigned short)(twoBytes | reader->in[secondByteIndex]);
  }
  twoBytes = (unsigned short)(twoBytes >> ((8 - firstByteCurBit) + (8 - nbits)));
  mask = (unsigned char)(~(255u << nbits));
  *out = (unsigned char)(twoBytes & mask);

  reader->curBit += nbits;

  return nbits;
}

/* TODO: consider combining both types into a bitstream_t */
typedef struct {
  unsigned char *out; /* May be NULL if countOnly is true */
  size_t len /* May be 0 if countOnly is true */;
  size_t curBit;
  int countOnly; /* If 1, only count written bits. Do not write. */
  int padding;
} bitwriter_t;

/* bitwriter_write writes nbits bits to writer.
 * nbits must be [1,8].
 * input bits start at the rightmost bit.
 * Returns -1 if the target buffer does not have capacity */
static int bitwriter_write(bitwriter_t *writer, size_t nbits, unsigned char in) {
  size_t bitLen = writer->len * 8;
  size_t firstByteIndex = writer->curBit / 8;
  size_t firstByteCurBit = writer->curBit % 8;
  unsigned short twoBytes;
  unsigned char mask;

  assert(nbits > 0);
  assert(nbits <= 8);

  if (writer->countOnly == 1) {
    writer->curBit += nbits;
    return 0;
  }

  if (writer->curBit + nbits > bitLen) {
    return -1;
  }

  /* Example of writing 6 bits (abcdef) when firstByteCurBit == 3:
   *
   * Create two bytes. Last byte written is first. Use 0 as second byte.
   *
   * xyz00000 00000000
   *    ^
   *    firstByteCurBit
   *
   * Mask input and left shift 8 + (8 - firstByteCurBit) - nbits
   *
   * 000abcde f0000000
   *
   * Or them together
   *
   * xyzabcde f0000000
   *
   * Output first byte.
   * If firstByteCurBit + nbits > 8, then output second byte.
   */

  mask = (unsigned char)(~(255u >> firstByteCurBit));
  twoBytes = writer->out[firstByteIndex] & mask;
  twoBytes = (unsigned short)(twoBytes << 8);

  mask = (unsigned char)(~(255u << nbits));
  twoBytes |= (unsigned short)((in & mask) << (8 + (8 - firstByteCurBit) - nbits));

  writer->out[firstByteIndex] = (unsigned char)(twoBytes >> 8);
  if (firstByteCurBit + nbits > 8) {
    writer->out[firstByteIndex + 1] = (unsigned char)twoBytes;
  }
  writer->curBit += nbits;
  return 0;
}

#endif /* LIBBASE_122_UTIL_H */
