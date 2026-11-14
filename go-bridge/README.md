# Standalone WaterSheep-compatible Go supervisor

Owns optional local child process startup and observation-only status. Does
not perform inference and does not authorize actions from model output.

```bash
go test ./...
go test -race ./...
go run ./cmd/watersheep-supervisor serve
```

Default supervisor address: 127.0.0.1:8777 (loopback enforced).
Default inference upstream: 127.0.0.1:8766.

`GET /v1/status`: observation-only lifecycle, child PID, readiness method.
`POST /v1/systemone`: normal raw inference forwarding (no debug consent needed).
`POST /v1/debug/direct`: requires `--dev` plus per-call direct-output consent.
`GET /v1/debug/logs`: requires `--dev` plus separately scoped logs consent.
Debug consent is not authentication and never grants execution authority.

Use `python3 ../tools/smoke.py --smoke --dev` for offline tests without a
model download. For stronger readiness validation, pass
`--readiness-request /path/to/request.json`, understanding that the POST may
trigger actual inference. Default TCP-only readiness is deliberately labeled
as such and must not be mistaken for full application health.
