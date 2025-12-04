# Incode Risk Model

A CatBoost-based fraud risk scoring model deployed on AWS Lambda using [SST v3](https://sst.dev/).

## Overview

This service provides a REST API endpoint that evaluates fraud risk based on identity verification features. It uses a pre-trained CatBoost classifier to return a risk score, risk label, and threshold information.

## Architecture

- **Runtime**: Python 3.11 on AWS Lambda (container-based)
- **Infrastructure**: SST v3 with Pulumi
- **ML Framework**: CatBoost 1.2.5
- **Memory**: 1024 MB
- **Architecture**: x86_64

## API

### Endpoint

```
POST /
```

### Request Body

```json
{
  "features": {
    "nameRiskLevel": "medium",
    "phoneLevel": "low",
    "addressRiskLevel": "low",
    "phoneEmailMatch": "exact",
    "phoneDobMatch": "fuzzy",
    "phoneCityMatch": "exact",
    "phoneZipcodeMatch": "exact",
    "phoneStateMatch": "exact",
    "phoneNameMatch": "exact",
    "phoneAddressMatch": "fuzzy",
    "overallLevel": "medium",
    "campus": "tempe"
  },
  "threshold_override": 0.5
}
```

#### Features (all required)

| Feature             | Description                       | Example Values           |
| ------------------- | --------------------------------- | ------------------------ |
| `nameRiskLevel`     | Risk level from name verification | `low`, `medium`, `high`  |
| `phoneLevel`        | Phone verification level          | `low`, `medium`, `high`  |
| `addressRiskLevel`  | Address verification risk level   | `low`, `medium`, `high`  |
| `phoneEmailMatch`   | Phone-email match quality         | `exact`, `fuzzy`, `none` |
| `phoneDobMatch`     | Phone-DOB match quality           | `exact`, `fuzzy`, `none` |
| `phoneCityMatch`    | Phone-city match quality          | `exact`, `fuzzy`, `none` |
| `phoneZipcodeMatch` | Phone-zipcode match quality       | `exact`, `fuzzy`, `none` |
| `phoneStateMatch`   | Phone-state match quality         | `exact`, `fuzzy`, `none` |
| `phoneNameMatch`    | Phone-name match quality          | `exact`, `fuzzy`, `none` |
| `phoneAddressMatch` | Phone-address match quality       | `exact`, `fuzzy`, `none` |
| `overallLevel`      | Overall verification level        | `low`, `medium`, `high`  |
| `campus`            | Campus identifier                 | `tempe`, `phoenix`, etc. |

#### Optional Parameters

| Parameter            | Type    | Description                                   |
| -------------------- | ------- | --------------------------------------------- |
| `threshold_override` | `float` | Override the default risk threshold (0.0-1.0) |

### Response

```json
{
  "risk_score": 0.23,
  "risk_label": "REVIEW",
  "threshold": 0.4,
  "version": "catboost-risk-v1",
  "feature_order": ["nameRiskLevel", "phoneLevel", ...]
}
```

#### Risk Labels

| Label       | Condition                 |
| ----------- | ------------------------- |
| `FRAUD`     | `risk_score >= 0.4`       |
| `NON_FRAUD` | `risk_score <= 0.09`      |
| `REVIEW`    | `0.09 < risk_score < 0.4` |

## Development

### Prerequisites

- [Node.js](https://nodejs.org/) 18+
- [pnpm](https://pnpm.io/)
- [uv](https://docs.astral.sh/uv/) (Python package manager)
- AWS credentials configured

### Setup

```bash
# Install Node dependencies
pnpm install

# Install Python dependencies
cd risk_model && uv sync && cd ..
```

### Deploy

```bash
# Deploy to development stage
pnpm run deploy

# Deploy to specific stage
pnpm run deploy --stage prod
```

### Local Testing

```bash
curl -X POST <LAMBDA_URL> \
  -H "Content-Type: application/json" \
  -d '{
    "features": {
      "nameRiskLevel": "medium",
      "phoneLevel": "low",
      "addressRiskLevel": "low",
      "phoneEmailMatch": "exact",
      "phoneDobMatch": "fuzzy",
      "phoneCityMatch": "exact",
      "phoneZipcodeMatch": "exact",
      "phoneStateMatch": "exact",
      "phoneNameMatch": "exact",
      "phoneAddressMatch": "fuzzy",
      "overallLevel": "medium",
      "campus": "tempe"
    }
  }'
```

## Project Structure

```
incode-risk-model/
├── sst.config.ts          # SST infrastructure config
├── pyproject.toml         # Root Python workspace config
├── package.json           # Node.js dependencies
└── risk_model/
    ├── Dockerfile         # Custom Lambda container
    ├── pyproject.toml     # Python package config
    ├── handler.py         # Lambda handler
    ├── model.cbm          # CatBoost model file
    └── model_metadata.json # Model configuration
```

## Environment Variables

| Variable            | Description                 | Default                 |
| ------------------- | --------------------------- | ----------------------- |
| `MODEL_PATH`        | Path to CatBoost model file | `./model.cbm`           |
| `METADATA_PATH`     | Path to model metadata JSON | `./model_metadata.json` |
| `DEFAULT_THRESHOLD` | Default risk threshold      | `0.4`                   |

## License

Proprietary
