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

use lazy_static::lazy_static;
use regex::Regex;
mod comment;

lazy_static! {
    static ref RE_RETURN: Regex = Regex::new(r"(?:^|[\W])return(?:$|[\W])").unwrap();
}

/// Process the alua string into vanilla lua string.
pub fn process(content: &str) -> Result<String, Vec<String>> {
    let mut output = String::with_capacity(content.len() * 5 / 4);
    let mut head: usize = 0;

    while head < content.len() {
        head = process_closure(&content, &head, &mut output)?;
    }
    Ok(output)
}

/// Find the first closure starting from start.
fn process_closure(content: &str, start: &usize, output: &mut String) -> Result<usize, Vec<String>> {
    let mut comment_state = comment::State::Regular;
    let mut previous_char = comment::CharOfInterest::NotInterested;

    let mut last_left_parenthesis: Option<usize> = None;
    let mut since_last_left_parenthesis = String::new();
    let mut start_parenthesis: Option<usize> = None;
    let mut first_pipe: Option<usize> = None;
    let mut level: Option<usize> = None;
    let mut second_pipe: Option<usize> = None;
    let mut return_position: Option<usize> = None;
    let mut since_return_position = String::new();
    let mut end_parenthesis: Option<usize> = None;

    let mut it = content.char_indices().peekable();
    while let Some((i, c)) = it.next() {
        if i < *start {
            continue;
        }

        comment::check_comment(&mut it, &c, &mut comment_state, &mut previous_char)?;
        match comment_state {
            comment::State::Regular => {
                match c {
                    '(' => {
                        if let Some(_) = last_left_parenthesis {
                            output.push_str(&since_last_left_parenthesis);
                            since_last_left_parenthesis.clear();
                        }
                        last_left_parenthesis = Some(i);
                        since_last_left_parenthesis.push(c);
                        if let Some(_) = return_position { since_return_position.push_str(&since_last_left_parenthesis); }

                        level = match level {
                            Some(l) => Some(l + 1),
                            None => None
                        };
                    },
                    '|' => {
                        if let None = first_pipe {
                            if let Some(l) = last_left_parenthesis {
                                start_parenthesis = Some(l);
                                first_pipe = Some(i);
                                level = Some(0);

                                output.push_str(&since_last_left_parenthesis);
                                last_left_parenthesis = None; since_last_left_parenthesis.clear();
                                output.push_str("function(");
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

                                if let Some(_) = last_left_parenthesis {
                                    output.push_str(&since_last_left_parenthesis);
                                    last_left_parenthesis = None; since_last_left_parenthesis.clear();
                                }
                                output.push(')');

                                return_position = Some(output.len());
                            } else {
                                match process_closure(content, last_left_parenthesis.as_ref().unwrap_or(&i), output) {
                                    Ok(end) => {
                                        while {
                                            it.next();
                                            if let Some((j, _)) = it.peek() {
                                               *j < end
                                            } else {
                                                false
                                            }
                                        } {}

                                        if let Some(_) = last_left_parenthesis {
                                            last_left_parenthesis = None; since_last_left_parenthesis.clear();
                                        }

                                        level = match level {
                                            Some(l) => Some(l - 1),
                                            None => {
                                                panic!();
                                            }
                                        };
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
                                match process_closure(content, last_left_parenthesis.as_ref().unwrap_or(&i), output) {
                                    Ok(end) => {
                                        while {
                                            it.next();
                                            if let Some((j, _)) = it.peek() {
                                                *j < end
                                            } else {
                                                false
                                            }
                                        } {}

                                        if let Some(_) = last_left_parenthesis {
                                            last_left_parenthesis = None; since_last_left_parenthesis.clear();
                                        }

                                        level = match level {
                                            Some(l) => Some(l - 1),
                                            None => {
                                                panic!();
                                            }
                                        };
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
                    },
                    ')' => {
                        if let Some(0) = level {
                            if let None = second_pipe {
                                return Err(vec![format!("Between the left parenthesis '{orange}({reset}' on line {start_parenthesis_linen} and the pairing right parenthesis '{orange}){reset}' on line {linen}, a pipe character '{orange}|{reset}' is found on line {first_pipe_linen} immediately after the left parenthesis, indicating the start of the closure's parameter list, but a second pipe character could not be found before the end of the closure to mark the end of the closure's parameter list.",
                                                        linen = content[..i+1].lines().count(),
                                                        first_pipe_linen = content[..first_pipe.unwrap()+1].lines().count(),
                                                        start_parenthesis_linen = content[..start_parenthesis.unwrap()+1].lines().count(),
                                                        orange = if cfg!(feature = "ansi_color_code") { "\x1b[33m" } else { "" },
                                                        reset = if cfg!(feature = "ansi_color_code") { "\x1b[0m" } else { "" })]);
                            } else {
                                end_parenthesis = Some(i);

                                if let Some(_) = last_left_parenthesis {
                                    output.push_str(&since_last_left_parenthesis);
                                    last_left_parenthesis = None; since_last_left_parenthesis.clear();
                                }
                                output.push_str(" end)");
                                since_return_position.push_str(" end)");
                                if !RE_RETURN.is_match(&since_return_position) {
                                    output.insert_str(return_position.unwrap(), " return");
                                }
                            }
                        } else {
                            if let Some(_) = last_left_parenthesis {
                                output.push_str(&since_last_left_parenthesis);
                                last_left_parenthesis = None; since_last_left_parenthesis.clear();
                            }
                            output.push(')');
                            if let Some(_) = return_position { since_return_position.push(')'); }

                            level = match level {
                                Some(l) => Some(l - 1),
                                None => None
                            }
                        }
                    },
                    ' ' | '\n' | '\r' | '\t' => {
                        if let Some(_) = last_left_parenthesis {
                            since_last_left_parenthesis.push(c);
                        } else {
                            output.push(c);
                        }
                        if let Some(_) = return_position { since_return_position.push(c) };
                    },
                    _ => {
                        if let Some(_) = last_left_parenthesis {
                            output.push_str(&since_last_left_parenthesis);
                            last_left_parenthesis = None; since_last_left_parenthesis.clear();
                        }
                        output.push(c);
                        if let Some(_) = return_position { since_return_position.push(c) };
                    }
                }
            },
            comment::State::Commented | comment::State::BracketCommented => {
                if let Some(_) = last_left_parenthesis {
                    since_last_left_parenthesis.push(c);
                } else {
                    output.push(c);
                }
            }
            _ => {
                if let Some(_) = last_left_parenthesis {
                    output.push_str(&since_last_left_parenthesis);
                    last_left_parenthesis = None; since_last_left_parenthesis.clear();
                }
;                output.push(c);
            }
        }

        if let Some(_) = end_parenthesis {
            if let Some((j, _)) = it.peek() {
                return Ok(*j);
            }
        }

    }
    
    if let Some(_) = end_parenthesis {
        Ok(content.len())
    } else if let Some(_) = second_pipe {
        Err(vec![format!("A pipe character '{orange}|{reset}' is found on line {first_pipe_linen} immediately after a left parenthesis '{orange}({reset}' on line {start_parenthesis_linen}, indicating the start of a closure. The pairing pipe character is found on line {second_pipe_linen}, but the pairing right parenthesis '{green}){reset}' could not be found before end of file.",
                         start_parenthesis_linen = content[..start_parenthesis.unwrap()+1].lines().count(),
                         first_pipe_linen = content[..first_pipe.unwrap()+1].lines().count(),
                         second_pipe_linen = content[..second_pipe.unwrap()+1].lines().count(),
                         orange = if cfg!(feature = "ansi_color_code") { "\x1b[33m" } else { "" },
                         green = if cfg!(feature = "ansi_color_code") { "\x1b[32m" } else { "" },
                         reset = if cfg!(feature = "ansi_color_code") { "\x1b[0m" } else { "" })])
    } else if let Some(_) = first_pipe {
        Err(vec![format!("A pipe character '{orange}|{reset}' is found on line {first_pipe_linen} immediately after a left parenthesis '{orange}({reset}' on line {start_parenthesis_linen}, indicating the start of a closure, but the pairing pipe character and right parenthesis '{green}){reset}' could not be found before end of file.",
                         start_parenthesis_linen = content[..start_parenthesis.unwrap()+1].lines().count(), // Because we know it is a pipe character at that position, it's safe to do +1
                         first_pipe_linen = content[..first_pipe.unwrap()+1].lines().count(),
                         orange = if cfg!(feature = "ansi_color_code") { "\x1b[33m" } else { "" },
                         green = if cfg!(feature = "ansi_color_code") { "\x1b[32m" } else { "" },
                         reset = if cfg!(feature = "ansi_color_code") { "\x1b[0m" } else { "" })])
    } else {
        Ok(content.len())
    }
}
