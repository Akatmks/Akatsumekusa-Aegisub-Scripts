#include "base122.h"
#include "util.h"

#include <assert.h>
#include <stdio.h>
#include <string.h>

/* strncpy_safe is like strncpy, except dest is always NULL terminated. */
static void strncpy_safe(char *dest, const char *src, size_t n) {
#ifdef _WIN32
  strncpy_s(dest, n, src, _TRUNCATE);
#else
  strncpy(dest, src, n);
  dest[n - 1] = '\0';
#endif
}

static unsigned char illegals[] = {
    0 /* null */,          10 /* newline */,   13 /* carriage return */,
    34 /* double quote */, 38 /* ampersand */, 92 /* backslash */
};

static int is_illegal(unsigned char val) {
  size_t i;
  for (i = 0; i < sizeof(illegals) / sizeof(illegals[0]); i++) {
    if (illegals[i] == val) {
      return 1;
    }
  }
  return 0;
}

static unsigned char get_illegal_index(unsigned char val) {
  unsigned char i;
  for (i = 0; i < sizeof(illegals) / sizeof(illegals[0]); i++) {
    if (illegals[i] == val) {
      return i;
    }
  }
  assert(0 && "unreachable");
  return 255;
}

int base122_encode(const unsigned char *in, size_t in_len, unsigned char *out, size_t out_len,
                   size_t *out_written, base122_error_t *error) {
  bitreader_t reader = {0};
  size_t nbits;
  unsigned char bits;
  size_t out_index = 0;
  int countOnly = 0;

  assert(in);
  assert(out_written);

  if (out == NULL) {
    countOnly = 1;
  }

  reader.in = in;
  reader.len = in_len;
  *out_written = 0;

#define OUTPUT_BYTE(b)                                                                             \
  if (countOnly == 1) {                                                                            \
    (*out_written)++;                                                                              \
  } else {                                                                                         \
    if (out_index == out_len) {                                                                    \
      strncpy_safe(error->msg, "output does not have sufficient size", sizeof(error->msg));        \
      return -1;                                                                                   \
    }                                                                                              \
    out[out_index] = b;                                                                            \
    (*out_written)++;                                                                              \
    out_index++;                                                                                   \
  }

  while ((nbits = bitreader_read(&reader, 7, &bits)) > 0) {
    if (nbits < 7) {
      /* Align the first bit to start at position 6.
       * E.g. if nbits = 3: 0abc0000 */
      bits = (unsigned char)(bits << (7 - nbits));
    }

    if (is_illegal(bits)) {
      unsigned char illegal_index = get_illegal_index(bits);
      unsigned char next_bits;
      unsigned char b1 = 0xC2; /* 11000010 */
      unsigned char b2 = 0x80; /* 10000000 */
      unsigned char first_bit;

      /* This will be a two byte character. Try to get the next 7 bits. */
      size_t next_nbits = bitreader_read(&reader, 7, &next_bits);
      /* Align the first bit to start at position 6.
       * E.g. if nbits = 3: 0abc0000 */
      next_bits = (unsigned char)(next_bits << (7 - next_nbits));

      if (next_nbits == 0) {
        b1 |= 0x7 << 2; /* 11100 */
        next_bits = bits;
      } else {
        b1 = (unsigned char)(b1 | (illegal_index << 2));
      }

      /* Push the first bit onto the first byte */
      first_bit = (next_bits >> 6) & 1;
      b1 |= first_bit;
      b2 = (unsigned char)(b2 | (next_bits & 0x3F /* 00111111 */));

      OUTPUT_BYTE(b1)
      OUTPUT_BYTE(b2)

    } else {
      OUTPUT_BYTE(bits);
    }
  }

#undef OUTPUT_BYTE

  return 0;
}

/* write_last_7 writes the last 7 bits of byteVal for decoding.
 * Sets an error if byteVal has 1 bits exceeding the last byte boundary. */
static int write_last_7(bitwriter_t *writer, unsigned char byteVal, base122_error_t *error) {
  size_t nbits = 7;
  unsigned char mask;
  /* Last input byte. */
  /* Do not write extra bytes. Write up to the nearest bit boundary. */
  nbits = 8 - (writer->curBit % 8);
  if (nbits == 8) {
    strncpy_safe(error->msg, "Decoded data is not a byte multiple", sizeof(error->msg));
    return -1;
  }
  /* Error if any bits after the last input bits are 1.
   * Example: nbits = 2
   * byteVal of 01100001 is an error. The rightmost 1 bit is unexpected. */
  mask = (unsigned char)~(0xFFu << (7 - nbits));
  if ((byteVal & mask) > 0) {
    strncpy_safe(error->msg, "Encoded data is malformed. Last byte has extra data.",
                 sizeof(error->msg));
    return -1;
  }
  /* Shift bits to write. */
  byteVal = (unsigned char)(byteVal >> (7 - nbits));
  if (bitwriter_write(writer, nbits, byteVal) == -1) {
    strncpy_safe(error->msg, "Output does not have sufficient size", sizeof(error->msg));
    return -1;
  }
  return 0;
}

int base122_decode(const unsigned char *in, size_t in_len, unsigned char *out, size_t out_len,
                   size_t *out_written, base122_error_t *error) {
  bitwriter_t writer = {0};
  size_t curByte;

  assert(in);
  assert(out_written);

  writer.out = out;
  writer.len = out_len;
  writer.curBit = 0;

  if (out == NULL) {
    writer.countOnly = 1;
  }

  for (curByte = 0; curByte < in_len; curByte++) {

#define WRITE_7(val)                                                                               \
  if (1) {                                                                                         \
    if (curByte + 1 == in_len) {                                                                   \
      if (-1 == write_last_7(&writer, val, error)) {                                               \
        return -1;                                                                                 \
      }                                                                                            \
    } else if (bitwriter_write(&writer, 7, val) == -1) {                                           \
      strncpy_safe(error->msg, "Output does not have sufficient size", sizeof(error->msg));        \
      return -1;                                                                                   \
    }                                                                                              \
  } else                                                                                           \
    ((void)0)

    if (in[curByte] >> 7 == 0) {
      /* One byte sequence. */
      unsigned char curByteVal = in[curByte];

      WRITE_7(curByteVal);
    } else {
      /* Two byte sequence. */
      unsigned char curByteVal = in[curByte];
      unsigned char nextByteVal;
      unsigned char illegalIndex;
      /* Expect first byte to have form 110xxx1y. */
      if ((curByteVal & 0xE2) /* 11100010 */ != 0xC2 /* 11000010 */) {
        strncpy_safe(error->msg, "First byte of two byte sequence malformed", sizeof(error->msg));
        return -1;
      }
      if (curByte + 1 == in_len) {
        strncpy_safe(error->msg, "Two byte sequence is missing second byte", sizeof(error->msg));
        return -1;
      }
      curByte++;
      nextByteVal = in[curByte];
      /* Expect second byte to have form 10xxxxxx. */
      if ((nextByteVal & 0xC0) /* 11000000 */ != 0x80 /* 10000000 */) {
        strncpy_safe(error->msg, "Second byte of two byte sequence malformed", sizeof(error->msg));
        return -1;
      }

      illegalIndex = (curByteVal & 0x1Cu /* 00011100 */) >> 2;
      if (illegalIndex == 0x7 /* 111 */) {
        unsigned char lastByteVal;

        /* This is a shortened two byte sequence. */
        if (curByte + 1 != in_len) {
          strncpy_safe(error->msg, "Got unexpected extra data after shortened two byte sequence",
                       sizeof(error->msg));
          return -1;
        }

        {
          lastByteVal = curByteVal;
          lastByteVal = (unsigned char)(lastByteVal << 0x6u);
          lastByteVal = (unsigned char)(lastByteVal | (nextByteVal & 0x3Fu /* 00111111 */));
        }

        WRITE_7(lastByteVal);
      } else if (illegalIndex < sizeof(illegals) / sizeof(illegals[0])) {
        unsigned char secondByteVal;

        if (-1 == bitwriter_write(&writer, 7, illegals[illegalIndex])) {
          strncpy_safe(error->msg, "Output does not have sufficient size", sizeof(error->msg));
          return -1;
        }

        secondByteVal = curByteVal;
        secondByteVal = (unsigned char)(secondByteVal << 0x6u);
        secondByteVal = (unsigned char)(secondByteVal | (nextByteVal & 0x3Fu /* 00111111 */));
        WRITE_7(secondByteVal);
      } else {
        strncpy_safe(error->msg, "Got unrecognized illegal index", sizeof(error->msg));
        return -1;
      }
    }
  }

  *out_written = writer.curBit / 8;
  return 0;
}
