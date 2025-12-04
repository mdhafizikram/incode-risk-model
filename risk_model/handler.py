from __future__ import annotations

import base64
import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

import pandas as pd
import ujson
from catboost import CatBoostClassifier

_ROOT = Path(__file__).parent
MODEL_PATH = Path(os.environ.get("MODEL_PATH", _ROOT / "model.cbm"))
METADATA_PATH = Path(os.environ.get("METADATA_PATH", _ROOT / "model_metadata.json"))
DEFAULT_THRESHOLD_ENV = os.environ.get("DEFAULT_THRESHOLD")

_model: Optional[CatBoostClassifier] = None
_metadata: Optional[Dict[str, Any]] = None


def _load_model_once() -> None:
  global _model, _metadata
  if _model is not None:
    return

  model = CatBoostClassifier()
  model.load_model(str(MODEL_PATH))
  _model = model

  with METADATA_PATH.open("r", encoding="utf-8") as fh:
    _metadata = json.load(fh)


def _validated_frame(features: Dict[str, Any]) -> pd.DataFrame:
  assert _metadata is not None
  feature_order = _metadata["feature_order"]
  missing = [name for name in feature_order if name not in features]
  if missing:
    raise ValueError(f"Missing required feature(s): {', '.join(missing)}")
  row = {name: features.get(name) for name in feature_order}
  return pd.DataFrame([row], columns=feature_order)


def _classify(features: Dict[str, Any], threshold_override: Optional[float]) -> Dict[str, Any]:
  assert _model is not None and _metadata is not None

  frame = _validated_frame(features)
  baseline_threshold = float(_metadata.get("risk_threshold", 0.4))
  version = _metadata.get("version", "catboost-risk-v1")

  risk_score = float(_model.predict_proba(frame)[:, 1][0])

  if threshold_override is not None:
    threshold = threshold_override
  elif DEFAULT_THRESHOLD_ENV is not None:
    threshold = float(DEFAULT_THRESHOLD_ENV)
  else:
    threshold = baseline_threshold

  label = (
    "FRAUD"
    if risk_score >= float(_metadata.get("fraud_cutoff", 0.4))
    else "NON_FRAUD"
    if risk_score <= float(_metadata.get("non_fraud_cutoff", 0.09))
    else "REVIEW"
  )

  return {
    "risk_score": risk_score,
    "risk_label": label,
    "threshold": threshold,
    "version": version,
    "feature_order": _metadata["feature_order"],
  }


def handler(event, _context):
  try:
    _load_model_once()

    body_raw: str
    if isinstance(event, dict) and "body" in event:
      body_raw = event["body"] or "{}"
      if event.get("isBase64Encoded"):
        body_raw = base64.b64decode(body_raw).decode("utf-8")
    else:
      body_raw = json.dumps(event or {})

    body = ujson.loads(body_raw)
    features = body.get("features")
    if not isinstance(features, dict):
      return _response(400, {"message": "Missing or invalid 'features' object"})

    threshold_override = body.get("threshold_override")
    if threshold_override is not None:
      try:
        threshold_override = float(threshold_override)
      except (TypeError, ValueError):
        return _response(400, {"message": "'threshold_override' must be numeric"})

    return _response(200, _classify(features, threshold_override))
  except ValueError as validation_err:
    return _response(400, {"message": str(validation_err)})
  except Exception as exc:  # pragma: no cover - reported via CW logs
    print(f"CatBoost handler error: {exc}", flush=True)
    return _response(500, {"message": "Internal server error"})


def _response(status_code: int, payload: Dict[str, Any]) -> Dict[str, Any]:
  return {
    "statusCode": status_code,
    "headers": {"Content-Type": "application/json"},
    "body": ujson.dumps(payload),
  }
