use std::fs;
use std::io::{self, Read};
use std::path::PathBuf;

use clap::{Parser, Subcommand};
use watersheep_harness::{build_receipt, build_receipt_json, parse_request, WaterSheepClient};

#[derive(Debug, Parser)]
#[command(
    name = "watersheep-harness",
    version,
    about = "Evidence-only WaterSheep-compatible Rust harness"
)]
struct Cli {
    #[command(subcommand)]
    command: Command,
}

#[derive(Debug, Subcommand)]
enum Command {
    /// Call an inference endpoint and emit a deterministic evidence receipt.
    Ask {
        #[arg(
            long,
            default_value = "http://127.0.0.1:8766",
            env = "WATERSHEEP_BASE_URL"
        )]
        base_url: String,
        #[arg(long, default_value = "-")]
        request: String,
        #[arg(long)]
        out: Option<PathBuf>,
        /// Raw response is observation-only, and requires BOTH flags below.
        #[arg(long)]
        response_out: Option<PathBuf>,
        #[arg(long, help = "Enable local development read-only response export")]
        dev: bool,
        #[arg(long, help = "Approve exporting raw response for this invocation only")]
        approve_readonly_response_out: bool,
    },
    /// Project an already-captured pair offline without network access.
    Project {
        #[arg(long)]
        request: PathBuf,
        #[arg(long)]
        response: PathBuf,
        #[arg(long, default_value = "offline://watersheep/v1/systemone")]
        endpoint: String,
        #[arg(long)]
        out: Option<PathBuf>,
    },
    /// Validate a request without running inference.
    Validate {
        #[arg(long, default_value = "-")]
        request: String,
    },
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    match Cli::parse().command {
        Command::Ask {
            base_url,
            request,
            out,
            response_out,
            dev,
            approve_readonly_response_out,
        } => {
            // Validate gate before sending any inference request or writing files.
            if response_out.is_some() && !(dev && approve_readonly_response_out) {
                return Err(
                    "--response-out requires --dev AND --approve-readonly-response-out".into(),
                );
            }
            if approve_readonly_response_out && !dev {
                return Err("--approve-readonly-response-out requires --dev".into());
            }
            let request_text = read_input(&request)?;
            let request = parse_request(&request_text)?;
            let client = WaterSheepClient::new(base_url)?;
            let response = client.ask(&request).await?;
            let receipt = build_receipt(&request, &response, client.endpoint())?;
            if let Some(path) = response_out {
                fs::write(
                    path,
                    format!("{}\n", serde_json::to_string_pretty(&response)?),
                )?;
            }
            write_output(out, &serde_json::to_string_pretty(&receipt)?)?;
        }
        Command::Project {
            request,
            response,
            endpoint,
            out,
        } => {
            let request = fs::read_to_string(request)?;
            let response = fs::read_to_string(response)?;
            let receipt = build_receipt_json(&request, &response, endpoint)?;
            write_output(out, &receipt)?;
        }
        Command::Validate { request } => {
            let request = parse_request(&read_input(&request)?)?;
            println!("{{\"ok\":true,\"questions\":{}}}", request.questions.len());
        }
    }
    Ok(())
}

fn read_input(path: &str) -> io::Result<String> {
    if path == "-" {
        let mut input = String::new();
        io::stdin().read_to_string(&mut input)?;
        Ok(input)
    } else {
        fs::read_to_string(path)
    }
}
fn write_output(path: Option<PathBuf>, body: &str) -> io::Result<()> {
    match path {
        Some(path) => fs::write(path, format!("{body}\n")),
        None => {
            println!("{body}");
            Ok(())
        }
    }
}
