# Rafiq — one-command entry points
.PHONY: run test data check

run:      ## start the app on http://localhost:8000
	uv run uvicorn app.main:app --port 8000

test:     ## run the test suite (39 tests)
	uv run pytest -q

data:     ## regenerate the synthetic pack (200 employees, sim day 5)
	uv run python scripts/make_synthetic_data.py --employees 200 --sim-day 5

check: test   ## everything a judge should run before the demo
