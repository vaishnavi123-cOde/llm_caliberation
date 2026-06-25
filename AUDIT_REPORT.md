# Audit Report: Mock / Simulated Code Analysis

## Search Summary

Scanned all `.py` files for: `_mock_query`, `mock`, `simulated`, `synthetic`, `fake`, `MODEL_ACCURACY`, `CONFIDENCE_MEAN`, `random` confidence generation, `fallback` responses, `set_mock_data`.

---

## Files Containing Mock Code (NOW REMOVED)

### 1. `models/gemini.py` (cleaned)

| Line | Code | Can Generate Fake? |
|------|------|--------------------|
| 9-10 | `MODEL_ACCURACY = 0.60` / `CONFIDENCE_MEAN = 0.72` | Yes — hardcoded accuracy/confidence targets |
| 16-17 | `if not self.api_key: return self._mock_query(prompt)` | Yes — silent fallback when API key missing |
| 33-34 | `except Exception: return self._mock_query(prompt)` | Yes — silent fallback on any API error |
| 36-50 | `def _mock_query(...)` generates rng-based answer + confidence | Yes — generates fully fake results |
| **Status** | **All removed.** Raises `RuntimeError` on missing key. Propagates API exceptions. |

### 2. `models/groq.py` (cleaned)

| Line | Code | Can Generate Fake? |
|------|------|--------------------|
| 9-10 | `MODEL_ACCURACY = 0.56` / `CONFIDENCE_MEAN = 0.73` | Yes — hardcoded accuracy/confidence targets |
| 16-17 | `if not self.api_key: return self._mock_query(prompt)` | Yes — silent fallback when API key missing |
| 37-38 | `except Exception: return self._mock_query(prompt)` | Yes — silent fallback on any API error |
| 40-54 | `def _mock_query(...)` generates rng-based answer + confidence | Yes — generates fully fake results |
| **Status** | **All removed.** Raises `RuntimeError` on missing key. Propagates API exceptions. |

### 3. `models/qwen.py` (DELETED)

| Line | Code | Can Generate Fake? |
|------|------|--------------------|
| 9-10 | `MODEL_ACCURACY = 0.50` / `CONFIDENCE_MEAN = 0.65` | Yes |
| 16-17 | `if not self.api_key: return self._mock_query(prompt)` | Yes |
| 36-37 | `except Exception: return self._mock_query(prompt)` | Yes |
| 39-53 | `def _mock_query(...)` | Yes — fully simulated |
| **Status** | **File deleted** (unused model). |

### 4. `models/base.py` (cleaned)

| Line | Code | Can Generate Fake? |
|------|------|--------------------|
| 10 | `self._mock_data = None` | Yes — stores mock context |
| 12-21 | `def set_mock_data(...)` stores correct answer index | Yes — provides correct answer to mock |
| **Status** | **All removed.** `_mock_data` and `set_mock_data` deleted. |

### 5. `pipeline.py` (cleaned)

| Line | Code | Can Generate Fake? |
|------|------|--------------------|
| 10 | `from models import QwenClient` | Yes — imports mock-capable client |
| 19-26 | `if model_name == "qwen": return QwenClient(...)` | Yes — routes to mock-capable client |
| 45 | `client.set_mock_data(...)` | Yes — feeds correct answer to mock |
| **Status** | **All removed.** Only `GeminiClient` and `GroqClient` remain. No `set_mock_data` call. |

---

## Clean Files (No Mock Code)

- `config.py` — Only model config and env var lookup
- `data/dataset.py` — Question bank and deterministic shuffling (legitimate)
- `metrics/calibration.py` — Statistical metrics and temperature scaling
- `visualization/plots.py` — Plotting functions
- `generate_report.py` — Report generation from CSV data only

---

## Result File Verification

| File | Generated From | Evidence |
|------|---------------|----------|
| `outputs/results_groq.csv` | **Real API calls** | 84 entries at conf=1.0 (mock max was 0.96); accuracy=0.6733 ≠ mock target 0.56 |
| `outputs/results_gemini.csv` | **Real API calls** | No conf=1.0 values; accuracy=0.5767 ≠ mock target 0.60; 208 unique confidence values |
| `outputs/metrics_summary.csv` | Computed from real CSVs | Derived from above files |

**Definitive proof Groq data is real:**
- Mock code used `min(rng.gauss(...), 0.96)` → maximum possible mock confidence = **0.96**
- Actual data has **84 values at exactly 1.0** → **impossible for mock code to produce**

---

## Mock Removal Summary

| Action | File | Status |
|--------|------|--------|
| Remove `_mock_query` method | `models/gemini.py` | ✅ Done |
| Remove `MODEL_ACCURACY`/`CONFIDENCE_MEAN` | `models/gemini.py` | ✅ Done |
| Remove silent fallback on missing API key | `models/gemini.py` → now raises `RuntimeError` | ✅ Done |
| Remove silent fallback on API error | `models/gemini.py` → now propagates exception | ✅ Done |
| Remove `_mock_query` method | `models/groq.py` | ✅ Done |
| Remove `MODEL_ACCURACY`/`CONFIDENCE_MEAN` | `models/groq.py` | ✅ Done |
| Remove silent fallback on missing API key | `models/groq.py` → now raises `RuntimeError` | ✅ Done |
| Remove silent fallback on API error | `models/groq.py` → now propagates exception | ✅ Done |
| Delete entire file | `models/qwen.py` | ✅ Done |
| Remove `_mock_data` and `set_mock_data` | `models/base.py` | ✅ Done |
| Remove `set_mock_data` call | `pipeline.py` | ✅ Done |
| Remove `QwenClient` import/instantiation | `pipeline.py`, `models/__init__.py`, `config.py` | ✅ Done |

**Result:** Zero mock code remains. All API calls now fail loudly when keys are missing or APIs error.
