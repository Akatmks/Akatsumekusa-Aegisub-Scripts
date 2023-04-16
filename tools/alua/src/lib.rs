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
    if let Some(first) = find_closure(&content, &0)? {
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

/// Find closure starting from position.
fn find_closure(content: &str, start: &usize) -> Result<Option<Vec<Closure>>, Vec<String>> {
    let mut state = comment::State::Regular;
    let mut last_interested_char = comment::CharOfInterest::NotInterested;

    // last_left_bracket logged whether there is a left parenthesis immediately before the current
    // char. '(' section sets it to true, while all other sections except ' ' | '\n' | '\r' | '\t'
    // section set it to false.
    let mut last_left_bracket: Option<usize> = None;
    // dashed is a special situation for the last_left_bracket. A comment shouldn't set
    // last_left_bracket to false, and there needs to be a way to differentiate the first dash of a
    // comment and a regular subtraction operator. The first time we encounter a dash in
    // State::Regular, we set dashed to true. If we encounter a pipe immediately afterwards, this
    // will set last_left_bracket to false. If we instead encounter other characters or a Commented
    // section immediately afterwards, this will set dashed to false.
    let mut dashed = false;

    let mut start_braket: Option<usize> = None;
    let mut first_pipe: Option<usize> = None;
    let mut second_pipe: Option<usize> = None;
    let mut end_bracket: Option<usize> = None;

    let mut level: Option<usize> = None;

    let mut return_vec: Vec<Closure> = Vec::new();

    let mut it = content.char_indices();
    while let Some((i, c)) = it.next() {
        if i < *start {
            continue;
        }

        comment::check_comment(&c, &mut state, &mut last_interested_char);
        match state {
            comment::State::Regular => {
                match c {
                    '(' => {
                        last_left_bracket = Some(i);
                        level = match level {
                            Some(l) => Some(l + 1),
                            None => None
                        };
                        dashed = false;
                    },
                    '|' => {
                        if let None = first_pipe {
                            if dashed {
                                last_left_bracket = None;
                            }
                            if let Some(l) = last_left_bracket {
                                start_braket = Some(l);
                                first_pipe = Some(i);
                                level = Some(0);
                            } else {
                                return Err(vec![format!("A pipe character '{orange}|{reset}' is found on line {linen}, but there is no parenthesis '{green}({reset}' immediately before the pipe character.",
                                                        linen = content[..i+1].lines().count(), // Because we know it is a pipe character at that position, it's safe to do +1
                                                        orange = if cfg!(feature = "ansi_color_code") { "\x1b[33m" } else { "" },
                                                        green = if cfg!(feature = "ansi_color_code") { "\x1b[32m" } else { "" },
                                                        reset = if cfg!(feature = "ansi_color_code") { "\x1b[0m" } else { "" }),
                                                "A pair of parenthesis is required around the alua closure to mark where it starts and ends.".to_string()]);
                            }
                        } else if let None = second_pipe {
                            if let Some(0) = level {
                                second_pipe = Some(i);
                            } else {
                                match find_closure(&content, last_left_bracket.as_ref().unwrap_or(&i)) {
                                    Ok(result) => {
                                        let result = result.unwrap();
                                        while { let (j, _) = it.next().unwrap(); j < result[0].end_bracket } {}
                                        level = match level {
                                            Some(l) => Some(l - 1),
                                            None => {
                                                panic!();
                                            }
                                        };
                                        return_vec.extend(result);
                                    },
                                    Err(mut msg) => {
                                        msg.push(format!("{grey}Traceback: closure starting from line {linen} is a nested closure inside closure starting from line {prev_linen}.{reset}",
                                                        linen = content[..i+1].lines().count(),
                                                        prev_linen = content[..first_pipe.unwrap()+1].lines().count(),
                                                        grey = if cfg!(feature = "ansi_color_code") { "\x1b[38;5;246m" } else { "" },
                                                        reset = if cfg!(feature = "ansi_color_code") { "\x1b[0m" } else { "" }));
                                        return Err(msg);
                                    }
                                }
                            }
                        } else {
                            if let Some(0) = level {
                                return Err(vec![format!("A pipe character '{orange}|{reset}' is found on line {linen} within the previous closure starting from line {prev_linen}, but there is no parenthesis '{green}({reset}' immediately before this pipe character.",
                                                        linen = content[..i+1].lines().count(),
                                                        prev_linen = content[..first_pipe.unwrap()+1].lines().count(),
                                                        orange = if cfg!(feature = "ansi_color_code") { "\x1b[33m" } else { "" },
                                                        green = if cfg!(feature = "ansi_color_code") { "\x1b[32m" } else { "" },
                                                        reset = if cfg!(feature = "ansi_color_code") { "\x1b[0m" } else { "" }),
                                                "A pair of parenthesis is required around the alua closure to mark where it starts and ends.".to_string()]);
                            } else {
                                match find_closure(&content, last_left_bracket.as_ref().unwrap_or(&i)) {
                                    Ok(result) => {
                                        let result = result.unwrap();
                                        while { let (j, _) = it.next().unwrap(); j < result[0].end_bracket } {}
                                        level = match level {
                                            Some(l) => Some(l - 1),
                                            None => {
                                                panic!();
                                            }
                                        };
                                        return_vec.extend(result);
                                    },
                                    Err(mut msg) => {
                                        msg.push(format!("{grey}Traceback: closure starting from line {linen} is a nested closure inside closure starting from line {prev_linen}.{reset}",
                                                        linen = content[..i+1].lines().count(),
                                                        prev_linen = content[..first_pipe.unwrap()+1].lines().count(),
                                                        grey = if cfg!(feature = "ansi_color_code") { "\x1b[38;5;246m" } else { "" },
                                                        reset = if cfg!(feature = "ansi_color_code") { "\x1b[0m" } else { "" }));
                                        return Err(msg);
                                    }
                                }
                            }
                        }
                        dashed = false;
                        last_left_bracket = None;
                    },
                    ')' => {
                        if let Some(0) = level {
                            if let None = second_pipe {
                                return Err(vec![format!("Between the left parenthesis '{orange}({reset}' on line {start_braket_linen} and the pairing right parenthesis '{orange}){reset}' on line {linen}, a pipe character '{orange}|{reset}' is found on line {first_pipe_linen} immediately after the left parenthesis, indicating the start of the closure's parameter list, but a second pipe character could not be found before the end of the closure to mark the end of the closure's parameter list.",
                                                        linen = content[..i+1].lines().count(),
                                                        first_pipe_linen = content[..first_pipe.unwrap()+1].lines().count(),
                                                        start_braket_linen = content[..start_braket.unwrap()+1].lines().count(),
                                                        orange = if cfg!(feature = "ansi_color_code") { "\x1b[33m" } else { "" },
                                                        reset = if cfg!(feature = "ansi_color_code") { "\x1b[0m" } else { "" })]);
                            } else {
                                end_bracket = Some(i);
                                return_vec.push(Closure {
                                    start_braket: start_braket.unwrap(),
                                    first_pipe: first_pipe.unwrap(),
                                    second_pipe: second_pipe.unwrap(),
                                    end_bracket: end_bracket.unwrap()
                                });
                                return Ok(Some(return_vec));
                            }
                        } else {
                            level = match level {
                                Some(l) => Some(l - 1),
                                None => None
                            }
                        }
                        dashed = false;
                        last_left_bracket = None;
                    },
                    ' ' | '\n' | '\r' | '\t' => (),
                    '-' => {
                        dashed = true;
                    },
                    _ => {
                        dashed = false;
                        last_left_bracket = None;
                    }
                }
            },
            comment::State::Commented => {
                if dashed {
                    dashed = false;
                }
            },
            _ => ()
        }
    }
    Ok(None)
}

