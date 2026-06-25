#!/usr/bin/env bash
set -euo pipefail

python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

# Optional: rerun live model evaluation if API keys are available.
# export GROQ_API_KEY="..."
# export GEMINI_API_KEY="..."
# python pipeline.py --models groq gemini --num-questions 300

# Recreate all research-quality artifacts from saved outputs.
python research_quality_analysis.py
