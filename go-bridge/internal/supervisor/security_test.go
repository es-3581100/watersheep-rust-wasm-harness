package supervisor

import (
	"context"
	"net/http"
	"net/http/httptest"
	"testing"
)

func TestLoopbackRequired(t *testing.T) {
	for _, bad := range []string{"0.0.0.0:8777", "[::]:8777", ":8777", "192.0.2.10:8777", "example.com:8777"} {
		if _, err := New(Config{ListenAddr: bad, ChildCommand: []string{"true"}}); err == nil {
			t.Errorf("accepted unsafe listen address %q", bad)
		}
	}
	for _, good := range []string{"127.0.0.1:8777", "[::1]:8777", "localhost:8777"} {
		if _, err := New(Config{ListenAddr: good, ChildCommand: []string{"true"}}); err != nil {
			t.Errorf("rejected %q: %v", good, err)
		}
	}
}
func TestDebugApprovalOperationScoped(t *testing.T) {
	s, _ := New(Config{ChildCommand: []string{"true"}, DevMode: true})
	prod, _ := New(Config{ChildCommand: []string{"true"}, DevMode: false})
	for _, op := range []struct{ method, path, phrase string }{
		{"GET", "/v1/debug/logs", DebugLogsApprovalPhrase},
		{"POST", "/v1/debug/direct", DebugApprovalPhrase},
	} {
		r := httptest.NewRequest(op.method, op.path, nil)
		if s.debugApproved(r) {
			t.Fatalf("missing approval allowed for %s", op.path)
		}
		r.Header.Set(DebugApprovalHeader, "WRONG")
		if s.debugApproved(r) {
			t.Fatalf("invalid approval allowed for %s", op.path)
		}
		other := DebugApprovalPhrase
		if other == op.phrase {
			other = DebugLogsApprovalPhrase
		}
		r.Header.Set(DebugApprovalHeader, other)
		if s.debugApproved(r) {
			t.Fatalf("wrong-operation approval allowed for %s", op.path)
		}
		r.Header.Set(DebugApprovalHeader, op.phrase)
		if !s.debugApproved(r) {
			t.Fatalf("correct approval denied for %s", op.path)
		}
		if prod.debugApproved(r) {
			t.Fatalf("production debug allowed for %s", op.path)
		}
	}
}
func TestDebugEndpointsFailClosed(t *testing.T) {
	s, _ := New(Config{ChildCommand: []string{"true"}, DevMode: true})
	paths := []struct{ method, path string }{{"GET", "/v1/debug/logs"}, {"POST", "/v1/debug/direct"}}
	for _, p := range paths {
		r := httptest.NewRequest(p.method, p.path, nil)
		w := httptest.NewRecorder()
		s.Handler().ServeHTTP(w, r)
		if w.Code != http.StatusForbidden {
			t.Errorf("%s should be 403, got %d", p.path, w.Code)
		}
	}
}
func TestRequestBodyBounded(t *testing.T) {
	s, _ := New(Config{ChildCommand: []string{"true"}})
	if s.Snapshot().Authority != "observation-only" {
		t.Fatal("authority violation")
	}
}

func TestReadinessJSONProbeValidatesShape(t *testing.T) {
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if r.Method != "POST" || r.URL.Path != "/v1/systemone" {
			t.Errorf("wrong request: %v", r)
			return
		}
		w.Header().Set("Content-Type", "application/json")
		_, _ = w.Write([]byte(`{"model":"fixture","answers":{"ready":{"type":"noul","noul":0.5}}}`))
	}))
	defer server.Close()
	s, err := New(Config{ChildCommand: []string{"true"}, UpstreamBase: server.URL, ReadinessRequest: []byte(`{"questions":{"ready":{"type":"noul","instructions":"ready?"}}}`)})
	if err != nil {
		t.Fatal(err)
	}
	if s.Snapshot().ReadinessMethod != "json-probe" {
		t.Fatalf("incorrect method: %s", s.Snapshot().ReadinessMethod)
	}
	if err := s.probeJSON(context.Background()); err != nil {
		t.Fatal(err)
	}
}

func TestReadinessJSONProbeRejectsMalformedResponse(t *testing.T) {
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		_, _ = w.Write([]byte(`{"unexpected":true}`))
	}))
	defer server.Close()
	s, err := New(Config{ChildCommand: []string{"true"}, UpstreamBase: server.URL, ReadinessRequest: []byte(`{}`)})
	if err != nil {
		t.Fatal(err)
	}
	if err := s.probeJSON(context.Background()); err == nil {
		t.Fatal("accepted malformed readiness response")
	}
}
