#ifndef LIBBASE122_H
#define LIBBASE122_H

#include <stddef.h> /* for size_t */

typedef struct {
  char msg[254];
} base122_error_t;

/* Encodes data in base122.
 * Pass NULL for `out` to determine the exact size required for `out`.
 * Returns -1 on error. */
int base122_encode(const unsigned char *in, size_t in_len, unsigned char *out, size_t out_len,
                   size_t *out_written, base122_error_t *error);

/* Decodes data in base122.
 * Pass NULL for `out` to determine the exact size required for `out`.
 * Returns -1 on error. */
int base122_decode(const unsigned char *in, size_t in_len, unsigned char *out, size_t out_len,
                   size_t *out_written, base122_error_t *error);

#endif /* LIBBASE122_H */
