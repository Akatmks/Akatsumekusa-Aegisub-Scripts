# aae-export-base122
# Copyright (c) Kevin Albertson, Akatsumekusa and contributors

# ------------------------------------------------------------------------
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ------------------------------------------------------------------------

TEMPLATE = lib
CONFIG += shared
CONFIG -= qt

SOURCES += \
    aae-export-base122.c \
    base122.c

HEADERS += \
    aae-export-base122.h \
    base122.h \
    util.h

TARGET = base122
VERSION = 1.0

macx:QMAKE_APPLE_DEVICE_ARCHS = x86_64 arm64

QMAKE_CFLAGS += -std=c89

DISTFILES += \
    LICENSE
