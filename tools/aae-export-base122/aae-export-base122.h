/* aae-export-base122
 * Copyright (c) Kevin Albertson, Akatsumekusa and contributors
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */


#ifndef AAE_EXPORT_BASE122_H
#define AAE_EXPORT_BASE122_H

#include <stddef.h>


/**
 * @brief decode
 * @param data The base122 string
 * @param size The size of the base122 string
 * @param output_buffer The buffer for the decoded content
 * @param output_buffer_size The size of the buffer
 * @return actual size the decoded content occupies
 */
extern size_t decode(const unsigned char* const data, const size_t size,
                     unsigned char* const output_buffer, const size_t output_buffer_size);

#endif /* AAE_EXPORT_BASE122_H */

