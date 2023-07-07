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

use alua;
use clap::Parser;
use std::ffi::OsStr;
use std::fs;
use std::path::PathBuf;
use std::process;
use shellexpand;

#[derive(Parser)]
#[command(author, version, about, long_about = None)]
struct Cli {
    /// Input alua file
    file: PathBuf,
    /// Specify output file
    #[arg(short, long, value_name = "FILE")]
    output: Option<PathBuf>
}

fn main() {
    let mut cli = Cli::parse();
    cli.file = match shellexpand::path::full(&cli.file) {
        Ok(path) => path.into_owned(),
        Err(msg) => {
            eprintln!("\x1b[31;1m[alua]\x1b[0m Failed to expand the input file '\x1b[33m{}\x1b[0m':", cli.file.to_string_lossy());
            eprintln!("\x1b[31;1m[alua]\x1b[0m {}.", msg);
            process::exit(1);
        }
    };
    cli.output = match cli.output {
        Some(path) => {
            match shellexpand::path::full(&path) {
                Ok(expand) => Some(expand.into_owned()),
                Err(msg) => {
                    eprintln!("\x1b[31;1m[alua]\x1b[0m Failed to expand the input file '\x1b[33m{}\x1b[0m':", cli.file.to_string_lossy());
                    eprintln!("\x1b[31;1m[alua]\x1b[0m {}.", msg);
                    process::exit(1);
                }
            }
        },
        None => {
            let mut p = cli.file.clone();
            if let Some("lua") = p.extension().and_then(OsStr::to_str) {
                eprintln!("\x1b[31;1m[alua]\x1b[0m Input file has extension '\x1b[33m.lua\x1b[0m' but no output file is specified.");
                eprintln!("\x1b[32;1m[alua]\x1b[0m If you want alua to overwrite input file, you need to explicitly specify it with the '\x1b[32m--output\x1b[0m' option.");
                process::exit(1);
            }
            p.set_extension("lua");
            Some(p)
        }
    };

    let content = match fs::read_to_string(&cli.file) {
        Ok(content) => content,
        Err(msg) => {
            eprintln!("\x1b[31;1m[alua]\x1b[0m Failed to read from the input file '\x1b[33m{}\x1b[0m':", cli.file.to_string_lossy());
            eprintln!("\x1b[31;1m[alua]\x1b[0m {}.", msg);
            process::exit(1);
        }
    };

    let content = match alua::process(&content) {
        Ok(content) => content,
        Err(msgs) => {
            for msg in &msgs {
                eprintln!("\x1b[31;1m[alua]\x1b[0m {}", msg);
            }
            process::exit(1);
        }
    };

    if let Err(msg) = fs::write(&cli.output.as_ref().unwrap(), content) {
        eprintln!("\x1b[31;1m[alua]\x1b[0m Failed to write to the output file '\x1b[33m{}\x1b[0m':", cli.output.as_ref().unwrap().to_string_lossy());
        eprintln!("\x1b[31;1m[alua]\x1b[0m {}.", msg);
        process::exit(1);
    }
}
