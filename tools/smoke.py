#!/usr/bin/env python3
"""Deterministic offline WaterSheep-compatible Go supervisor and Rust receipt smoke.

Uses a subprocess fake HTTP inference server on 127.0.0.1; no weights or credentials.
--skip-rust is a diagnostic-only mode and does not satisfy release acceptance.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.error import HTTPError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
REQUEST = ROOT / "fixtures/v1/request.json"
RESPONSE = ROOT / "fixtures/v1/response.json"
DIRECT = "I-APPROVE-READONLY-DIRECT-OUTPUT"
LOGS = "I-APPROVE-READONLY-LOGS"
HEADER = "X-WaterSheep-Debug-Approval"


def run(args: list[str], cwd: Path | None = None, capture: bool = False) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, cwd=cwd, check=True, text=True, capture_output=capture)


def free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def json_http(method: str, url: str, data: dict | None = None, header: str | None = None):
    raw = None if data is None else json.dumps(data).encode()
    headers = {"Accept": "application/json"}
    if raw is not None:
        headers["Content-Type"] = "application/json"
    if header:
        headers[HEADER] = header
    req = Request(url, data=raw, headers=headers, method=method)
    with urlopen(req, timeout=4) as response:
        return response.status, json.loads(response.read().decode())


def refused(method: str, url: str, body=None, header=None) -> bool:
    try:
        json_http(method, url, body, header)
    except HTTPError as exc:
        return exc.code == 403
    return False


class FakeBackend(BaseHTTPRequestHandler):
    def log_message(self, *args):
        return

    def do_POST(self):
        if self.path != "/v1/systemone":
            self.send_error(404)
            return
        size = int(self.headers.get("Content-Length", "0"))
        request = json.loads(self.rfile.read(size))
        default_response = json.loads(RESPONSE.read_text(encoding="utf8"))
        if set(request["questions"]) == set(default_response["answers"]):
            response = default_response
        else:
            response = {
                "model": "synthetic-fixture-v1", "usage": {"input_tokens": 0, "output_tokens": 0},
                "answers": {name: {"type": "noul", "noul": 0.5} for name in request["questions"]},
            }
        payload = json.dumps(response, separators=(",", ":"), sort_keys=True).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)


def fake_server(port: int) -> None:
    ThreadingHTTPServer(("127.0.0.1", port), FakeBackend).serve_forever()


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true", help="run smoke (default)")
    parser.add_argument("--dev", action="store_true")
    parser.add_argument("--skip-rust", action="store_true", help="diagnostic-only partial mode")
    parser.add_argument("--_fake-server", type=int, help=argparse.SUPPRESS)
    args = parser.parse_args(argv)
    if args._fake_server:
        fake_server(args._fake_server)
        return 0

    bin_path = ROOT / ".dev/bin/watersheep-supervisor"
    bin_path.parent.mkdir(parents=True, exist_ok=True)
    run(["go", "test", "./..."], ROOT / "go-bridge")
    run(["go", "build", "-o", str(bin_path), "./cmd/watersheep-supervisor"], ROOT / "go-bridge")
    upstream = free_port()
    listen = free_port()
    base = f"http://127.0.0.1:{listen}"
    env = dict(os.environ, WATERSHEEP_SMOKE="1")
    child = [sys.executable, str(Path(__file__).resolve()), "--_fake-server", str(upstream)]
    cmd = [str(bin_path), "serve", "--listen", f"127.0.0.1:{listen}",
           "--upstream", f"http://127.0.0.1:{upstream}", "--startup-timeout", "12s",
           "--child-command-json", json.dumps(child), "--readiness-request", str(REQUEST)]
    if args.dev:
        cmd.append("--dev")
    proc = subprocess.Popen(cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    try:
        for _ in range(120):
            if proc.poll() is not None:
                raise RuntimeError(f"supervisor exited: {proc.stderr.read()}")
            try:
                _, status = json_http("GET", base + "/v1/status")
                if status["state"] == "ready":
                    break
            except Exception:
                pass
            time.sleep(0.1)
        else:
            raise TimeoutError("supervisor not ready")

        assert status["authority"] == "observation-only"
        assert status["owner"] == "go-bridge"
        assert status["go_module"] == "github.com/es-3581100/watersheep-rust-wasm-harness/go-bridge"
        assert status["readiness_method"] == "json-probe"
        req = json.loads(REQUEST.read_text(encoding="utf8"))
        _, response = json_http("POST", base + "/v1/systemone", req)
        assert response == json.loads(RESPONSE.read_text(encoding="utf8"))
        assert refused("POST", base + "/v1/debug/direct", req)
        assert refused("POST", base + "/v1/debug/direct", req, "wrong")
        assert refused("POST", base + "/v1/debug/direct", req, LOGS)
        assert refused("GET", base + "/v1/debug/logs")
        assert refused("GET", base + "/v1/debug/logs", header=DIRECT)
        if args.dev:
            _, direct = json_http("POST", base + "/v1/debug/direct", req, DIRECT)
            assert direct == response
            _, logs = json_http("GET", base + "/v1/debug/logs", header=LOGS)
            assert logs["authority"] == "observation-only" and logs["readonly"] is True
        else:
            assert refused("POST", base + "/v1/debug/direct", req, DIRECT)
            assert refused("GET", base + "/v1/debug/logs", header=LOGS)

        receipt = None
        if not args.skip_rust:
            with tempfile.TemporaryDirectory() as td:
                out = Path(td) / "receipt.json"
                rust = ["cargo", "run", "--quiet", "--manifest-path", str(ROOT / "rust-harness/Cargo.toml"), "--"]
                run(rust + ["ask", "--base-url", base, "--request", str(REQUEST), "--out", str(out)])
                receipt = json.loads(out.read_text())
                expected = json.loads((ROOT / "fixtures/v1/receipt.golden.json").read_text())
                # Endpoint differs from offline golden; hashes and decisions must not.
                receipt["endpoint"] = expected["endpoint"]
                assert receipt == expected
                assert receipt["authority"] == "evidence-only"
                # Raw response export must fail before inference or file writes
                # unless both invocation-scoped flags are present.
                raw = Path(td) / "raw.json"
                gated = rust + ["ask", "--base-url", base, "--request", str(REQUEST),
                                "--out", str(out), "--response-out", str(raw)]
                out.unlink()
                for flags in ([], ["--dev"], ["--approve-readonly-response-out"]):
                    result = subprocess.run(gated + flags, text=True, capture_output=True)
                    assert result.returncode != 0 and not raw.exists() and not out.exists()
                run(gated + ["--dev", "--approve-readonly-response-out"])
                assert json.loads(raw.read_text()) == response
                assert json.loads(out.read_text())["authority"] == "evidence-only"
                # Repeated identical requests yield identical complete receipts.
                run(rust + ["project", "--request", str(REQUEST), "--response", str(RESPONSE),
                            "--endpoint", "offline://watersheep/v1/systemone", "--out", str(out)])
                first = out.read_bytes()
                run(rust + ["project", "--request", str(REQUEST), "--response", str(RESPONSE),
                            "--endpoint", "offline://watersheep/v1/systemone", "--out", str(out)])
                assert first == out.read_bytes()
        print(json.dumps({"status": "PASS", "dev": args.dev, "rust_included": not args.skip_rust,
                          "normal_forward": True, "debug_gates": "PASS", "readiness": status["readiness_method"],
                          "receipt": receipt is not None}, sort_keys=True))
        return 0
    finally:
        proc.terminate()
        try:
            proc.communicate(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.communicate(timeout=2)


if __name__ == "__main__":
    raise SystemExit(main())
