package main

import "testing"

func TestChildOverrideBlockedWithoutExplicitDevOrTestMode(t *testing.T) {
	_, err := childCommand("python3", "model", "http://127.0.0.1:8766", `["/bin/echo","hello"]`, false)
	if err == nil {
		t.Fatal("child override accepted in normal configuration")
	}
	child, err := childCommand("python3", "model", "http://127.0.0.1:8766", `["/bin/echo","hello"]`, true)
	if err != nil || len(child) != 2 {
		t.Fatalf("dev/test override incorrectly denied: %v, %v", child, err)
	}
}
func TestUpstreamPortValidation(t *testing.T) {
	for _, p := range []string{"http://127.0.0.1:8766", "http://localhost:8766/v1"} {
		got, err := upstreamPort(p)
		if err != nil || got != 8766 {
			t.Fatalf("%q = %d, %v", p, got, err)
		}
	}
	for _, p := range []string{"bad", "http://127.0.0.1", "http://127.0.0.1:0"} {
		if _, err := upstreamPort(p); err == nil {
			t.Fatalf("accepted %q", p)
		}
	}
}
func TestDebugCliRequiresScopedFlag(t *testing.T) {
	if err := debugLogs([]string{"--base-url", "http://127.0.0.1:1"}); err == nil {
		t.Fatal("logs request skipped approval")
	}
	if err := debugAsk([]string{"--base-url", "http://127.0.0.1:1"}); err == nil {
		t.Fatal("raw output request skipped approval")
	}
}
