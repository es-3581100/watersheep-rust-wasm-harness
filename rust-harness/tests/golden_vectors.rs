use std::fs;
use std::path::PathBuf;

use watersheep_harness::{build_receipt_json, parse_request, parse_response};

fn fixture(name: &str) -> String {
    let path = PathBuf::from(env!("CARGO_MANIFEST_DIR"))
        .join("../fixtures/v1")
        .join(name);
    fs::read_to_string(path).unwrap()
}

#[test]
fn golden_receipt_exact_and_repeatable() {
    let request = fixture("request.json");
    let response = fixture("response.json");
    let expected = fixture("receipt.golden.json");
    let endpoint = "offline://watersheep/v1/systemone";
    let first = build_receipt_json(&request, &response, endpoint).unwrap();
    let want: serde_json::Value = serde_json::from_str(&expected).unwrap();
    let got: serde_json::Value = serde_json::from_str(&first).unwrap();
    assert_eq!(got, want, "receipt or hash changed from checked-in vector");
    assert_eq!(
        first,
        build_receipt_json(&request, &response, endpoint).unwrap()
    );
    assert_eq!(got["authority"], "evidence-only");
    assert_eq!(got["schema"], "watersheep.harness.receipt/v1");
}

#[test]
fn object_key_order_invariance() {
    let request: serde_json::Value = serde_json::from_str(&fixture("request.json")).unwrap();
    let response: serde_json::Value = serde_json::from_str(&fixture("response.json")).unwrap();
    let original =
        build_receipt_json(&request.to_string(), &response.to_string(), "offline").unwrap();
    // BTreeMap sorting also handles nested object key order.
    let req: serde_json::Value = serde_json::from_str(&request.to_string()).unwrap();
    let resp: serde_json::Value = serde_json::from_str(&response.to_string()).unwrap();
    let next = build_receipt_json(&req.to_string(), &resp.to_string(), "offline").unwrap();
    assert_eq!(original, next);
}

#[test]
fn stale_answer_names_and_invalid_probabilities_rejected() {
    let request = fixture("request.json");
    let mut response: serde_json::Value = serde_json::from_str(&fixture("response.json")).unwrap();
    response["answers"]
        .as_object_mut()
        .unwrap()
        .remove("binary");
    let result = build_receipt_json(&request, &response.to_string(), "offline");
    assert!(result.is_err());
    let mut response: serde_json::Value = serde_json::from_str(&fixture("response.json")).unwrap();
    response["answers"]["choice"]["confidence"] = serde_json::json!(1.25);
    assert!(parse_response(&response.to_string()).is_err());
    let mut request: serde_json::Value = serde_json::from_str(&request).unwrap();
    request["questions"]["choice"]["threshold"] = serde_json::json!(0.4);
    assert!(parse_request(&request.to_string()).is_err());
}

#[test]
fn mutations_change_semantic_digest() {
    let base: serde_json::Value = serde_json::from_str(
        &build_receipt_json(
            &fixture("request.json"),
            &fixture("response.json"),
            "offline",
        )
        .unwrap(),
    )
    .unwrap();
    let mut request: serde_json::Value = serde_json::from_str(&fixture("request.json")).unwrap();
    request["state"]["attempt"] = serde_json::json!(4);
    let changed: serde_json::Value = serde_json::from_str(
        &build_receipt_json(&request.to_string(), &fixture("response.json"), "offline").unwrap(),
    )
    .unwrap();
    assert_ne!(base["request_sha256"], changed["request_sha256"]);
    assert_eq!(base["response_sha256"], changed["response_sha256"]);
}
