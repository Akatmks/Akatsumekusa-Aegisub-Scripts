// alua
// Copyright (c) Akatsumekusa and contributors

// Permission is hereby granted, free of charge, to any person obtaining a copy
// of this software and associated documentation files (the "Software"), to deal
// in the Software without restriction, including without limitation the rights
// to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
// copies of the Software, and to permit persons to whom the Software is
// furnished to do so, subject to the following conditions:
//
// The above copyright notice and this permission notice shall be included in all
// copies or substantial portions of the Software.
//
// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
// IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
// FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
// AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
// LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
// OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
// SOFTWARE.

use std::iter::Peekable;
use std::str::CharIndices;

pub enum State {
    Regular,
    Commented,
    SingleQuoted,
    DoubleQuoted,
    Bracketed,
    BracketCommented
}

pub enum CharOfInterest {
    NotInterested,
    FirstHyphen,
    SecondHyphen,
    RightSquareBracket,
    Escape
}

#[inline]
pub fn check_comment(it: &mut Peekable<CharIndices>, c: &char, state: &mut State, previous_char: &mut CharOfInterest) -> Result<(), Vec<String>> {
    match c {
        '-' => {
            match state {
                State::Regular => {
                    if let Some((_, '-')) = it.peek() {
                        *state = State::Commented;
                        *previous_char = CharOfInterest::FirstHyphen;
                    } else {
                        *previous_char = CharOfInterest::NotInterested;
                    }
                },
                State::Commented => {
                    *previous_char = match previous_char {
                        CharOfInterest::FirstHyphen => {
                            CharOfInterest::SecondHyphen
                        },
                        _ => {
                            CharOfInterest::NotInterested
                        }
                    }
                },
                _ => {
                    *previous_char = CharOfInterest::NotInterested;
                }
            }
        },
        '[' => {
            match state {
                State::Regular => {
                    if let Some((_, '[')) = it.peek() {
                        *state = State::Bracketed;
                    }
                },
                State::Commented => {
                    if matches!(previous_char, CharOfInterest::SecondHyphen) {
                        *state = State::BracketCommented;
                    }
                },
                _ => ()
            }
            *previous_char = CharOfInterest::NotInterested;
        },
        ']' => {
            match state {
                State::Bracketed | State::BracketCommented => {
                    match previous_char {
                        CharOfInterest::RightSquareBracket => {
                            *state = State::Regular;
                            *previous_char = CharOfInterest::NotInterested;
                        },
                        _ => {
                            if let Some((_, ']')) = it.peek() {
                                *previous_char = CharOfInterest::RightSquareBracket;
                            } else {
                                *previous_char = CharOfInterest::NotInterested
                            };
                        }
                    }
                },
                _ => {
                    *previous_char = CharOfInterest::NotInterested;
                }
            }
        },
        '\'' => {
            match state {
                State::SingleQuoted => {
                    match previous_char {
                        CharOfInterest::Escape => (),
                        _ => {
                            *state = State::Regular;
                        }
                    }
                },
                State::Regular => {
                    *state = State::SingleQuoted;
                },
                _ => ()
            }
            *previous_char = CharOfInterest::NotInterested;
        },
        '"' => {
            match state {
                State::DoubleQuoted => {
                    match previous_char {
                        CharOfInterest::Escape => (),
                        _ => {
                            *state = State::Regular;
                        }
                    }
                },
                State::Regular => {
                    *state = State::DoubleQuoted;
                },
                _ => ()
            }
            *previous_char = CharOfInterest::NotInterested;
        }
        '\\' => {
            match state {
                State::SingleQuoted | State::DoubleQuoted => {
                    *previous_char = match previous_char {
                        CharOfInterest::Escape => {
                            CharOfInterest::NotInterested
                        },
                        _ => {
                            CharOfInterest::Escape
                        }
                    }
                },
                _ => {
                    *previous_char = CharOfInterest::NotInterested;
                }
            }
        }
        '\n' | '\r' => {
            match state {
                State::Commented | State::SingleQuoted | State::DoubleQuoted => {
                    *state = State::Regular;
                },
                _ => ()
            }
            *previous_char = CharOfInterest::NotInterested;
        },
        _ => {
            *previous_char = CharOfInterest::NotInterested;
        }
    }

    Ok(())
}
