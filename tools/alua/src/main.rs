use clap::Parser;
use std::path::PathBuf;

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
    let cli = Cli::parse();
    println!("file: {:?}", cli.file);
    println!("output: {:?}", cli.output);
}
