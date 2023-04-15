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

use std::borrow::Cow;

mod comment;

/// Process the alua string into vanilla lua string.
pub fn process<'a>(content: &'a str) -> Result<Cow<'a, str>, Vec<String>> {
    if let Some(first) = find_closure(content, 0) {
        let mut output = String::with_capacity(content.len() * 6 / 5);
        Ok(Cow::Owned(output))
    } else {
        Ok(Cow::Borrowed(content))
    }
}

struct Closure {
    start_braket: usize,
    first_pipe: usize,
    second_pipe: usize,
    end_bracket: usize
}

/// Find closure
fn find_closure(content: &str, start: usize) -> Result<Option<Closure>, Vec<String>> {
    let mut state = comment::State::Regular;
    let mut last_interested_char = comment::CharOfInterest::NotInterested;

    let mut last_left_bracket: Option<usize> = None;

    let mut start_braket: Option<usize> = None;
    let mut first_pipe: Option<usize> = None;
    let mut second_pipe: Option<usize> = None;
    let mut end_bracket: Option<usize> = None;

    let mut level: Option<usize> = None;

    for (i, c) in content[start..].char_indices() {
        comment::check_comment(&c, &mut state, &mut last_interested_char);
        if matches!(state, comment::State::Regular) {
            match c {
                '(' => {
                    last_left_bracket = Some(i);
                    level = match level {
                        Some(l) => Some(l + 1),
                        None => None
                    };
                },
                '|' => {
                    if let None = first_pipe {
                        if let Some(l) = last_left_bracket {
                            start_braket = Some(l);
                            first_pipe = Some(i);
                            level = Some(0);
                        } else {
                            return Err(vec![format!("A pipe character '{orange}|{reset}' is found on line {linen}, but there is no parenthesis '{green}({reset}' immediately before the pipe character.",
                                                    linen = content[..i+1].lines().count(),
                                                    orange = if cfg!(feature = "ansi_color_code") { "\x1b[33m" } else { "" },
                                                    green = if cfg!(feature = "ansi_color_code") { "\x1b[32m" } else { "" },
                                                    reset = if cfg!(feature = "ansi_color_code") { "\x1b[0m" } else { "" }),
                                            "A pair of parenthesis is required around the alua closure to mark where it starts and ends.".to_string()]);
                        }
                    } else if let None = second_pipe {
                        if let Some(0) = level {
                            second_pipe = Some(i);
                        } else {
                            // todo Nested closure
                        }
                    } else {
                        if let Some(0) = level {
                            return Err(vec![format!("A pipe character '{orange}|{reset}' is found on line {linen} within the previous closure starting from line {prev_linen}, but there is no parenthesis '{green}({reset}' immediately before this pipe character.",
                                                    linen = content[..i+1].lines().count(),
                                                    prev_linen = content[..first_pipe.unwrap()].lines().count(),
                                                    orange = if cfg!(feature = "ansi_color_code") { "\x1b[33m" } else { "" },
                                                    green = if cfg!(feature = "ansi_color_code") { "\x1b[32m" } else { "" },
                                                    reset = if cfg!(feature = "ansi_color_code") { "\x1b[0m" } else { "" }),
                                            "A pair of parenthesis is required around the alua closure to mark where it starts and ends.".to_string()]);
                        } else {
                            // todo Nested closure
                        }
                    }
                },
                ')' => {
                }
            }
        }
    }
    Ok(None)
}

