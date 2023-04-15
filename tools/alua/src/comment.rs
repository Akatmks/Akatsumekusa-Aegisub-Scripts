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

pub enum State {
    Regular,
    Commented,
    SingleQuoted,
    DoubleQuoted,
    Bracketed
}

pub enum CharOfInterest {
    NotInterested,
    Hyphen,
    LeftSquareBracket,
    RightSquareBracket,
    Escape
}

#[inline]
pub fn check_comment(c: &char, state: &mut State, last_interested_char: &mut CharOfInterest) {
    match c {
        '-' => {
            match state {
                State::Regular => {
                    match last_interested_char {
                        CharOfInterest::Hyphen => {
                            *state = State::Commented;
                        },
                        _ => {
                            *last_interested_char = CharOfInterest::Hyphen
                        }
                    }
                },
                _ => {
                    *last_interested_char = CharOfInterest::NotInterested;
                }
            }
        },
        '[' => {
            match state {
                State::Regular => {
                    match last_interested_char {
                        CharOfInterest::LeftSquareBracket => {
                            *state = State::Bracketed;
                        },
                        _ => {
                            *last_interested_char = CharOfInterest::LeftSquareBracket;
                        }
                    }
                },
                State::Commented => {
                    match last_interested_char {
                        CharOfInterest::Hyphen => {
                            *last_interested_char = CharOfInterest::LeftSquareBracket;
                        },
                        CharOfInterest::LeftSquareBracket => {
                            *state = State::Bracketed;
                        },
                        _ => {
                            *last_interested_char = CharOfInterest::NotInterested;
                        }
                    }
                },
                _ => {
                    *last_interested_char = CharOfInterest::NotInterested;
                }
            }
        },
        ']' => {
            match state {
                State::Bracketed => {
                    match last_interested_char {
                        CharOfInterest::RightSquareBracket => {
                            *state = State::Regular;
                        },
                        _ => {
                            *last_interested_char = CharOfInterest::RightSquareBracket;
                        }
                    }
                },
                _ => {
                    *last_interested_char = CharOfInterest::NotInterested;
                }
            }
        },
        '\'' => {
            match state {
                State::SingleQuoted => {
                    match last_interested_char {
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
            *last_interested_char = CharOfInterest::NotInterested;
        },
        '"' => {
            match state {
                State::DoubleQuoted => {
                    match last_interested_char {
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
            *last_interested_char = CharOfInterest::NotInterested;
        }
        '\\' => {
            match state {
                State::SingleQuoted | State::DoubleQuoted => {
                    match last_interested_char {
                        CharOfInterest::Escape => {
                            *last_interested_char = CharOfInterest::NotInterested;
                        },
                        _ => {
                            *last_interested_char = CharOfInterest::Escape;
                        }
                    }
                },
                _ => {
                    *last_interested_char = CharOfInterest::NotInterested;
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
            *last_interested_char = CharOfInterest::NotInterested;
        },
        _ => {
            *last_interested_char = CharOfInterest::NotInterested;
        }
    }
}
