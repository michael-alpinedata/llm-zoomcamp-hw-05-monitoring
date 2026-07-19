# LLM Zoomcamp — Homework Module 5: Monitoring

This repo contains my solution to the **Module 5: Monitoring** homework
from the [LLM Zoomcamp](https://github.com/DataTalksClub/llm-zoomcamp/).

The goal is to instrument a RAG system with
[OpenTelemetry](https://opentelemetry.io/) (OTel): create traces,
capture metrics (tokens, cost, duration) as span attributes, persist
those traces to SQLite, and query them to understand the system's
behavior.

Unlike the original starter (which uses OpenAI), this repo uses
**Gemini** (`gemini-3.1-flash-lite`) as the LLM, via the `google-genai`
SDK.

## Stack

- **RAG**: text search with [minsearch](https://github.com/alexeygrigorev/minsearch)
  over the 72 lesson pages from the LLM Zoomcamp, fetched via
  [gitsource](https://github.com/alexeygrigorev/gitsource)
- **LLM**: Gemini (`gemini-3.1-flash-lite`) via the `google-genai` SDK
- **Instrumentation**: OpenTelemetry (`opentelemetry-api`, `opentelemetry-sdk`)
- **Trace storage**: SQLite, via a custom OTel exporter
- **Project management**: [uv](https://docs.astral.sh/uv/)

## Repo structure

```
.
├── README.md
├── homework.md            # Original homework assignment
├── pyproject.toml
├── .env.example            # Template for the required env vars
├── rag_helper.py            # RAGBase, adapted for Gemini
├── starter.py                # Loads the index + Gemini client
├── run_q6.py                  # RAGTraced (instrumented rag/search/llm),
│                                #   toggles between console exporter
│                                #   (Q1-Q3) and SQLite exporter (Q4-Q6)
├── run_query_q4.py           # Lists distinct span names in traces.db
├── run_query_q5.py           # Total duration per span type (excl. "rag")
├── run_query_q6.py           # Input tokens per "llm" span (token stability)
├── traces.db                  # Generated SQLite database with the spans
├── q1.png ... q6.png          # Screenshots of the console/query output
│                                #   for each question
└── course-material/           # Course lessons and reference code for
                                 #   Module 5 (unmodified)
```

## Installation

```bash
uv sync
```

or, starting from scratch:

```bash
uv init
uv add gitsource minsearch python-dotenv google-genai
uv add opentelemetry-api opentelemetry-sdk
```

Copy `.env.example` to `.env` and fill in your Gemini API key:

```bash
cp .env.example .env
```

```
GEMINI_API_KEY=your_key_here
```

## Usage

### 1. Plain RAG, no instrumentation

```bash
uv run python starter.py
```

### 2. Traced RAG (Q1–Q6)

`run_q6.py` wraps `rag()`, `search()`, and `llm()` in OTel spans, and
attaches the `input_tokens` / `output_tokens` / `cost` attributes to the
`llm` span.

By default it uses the **SQLite exporter**, writing every span into
`traces.db`:

```bash
uv run python run_q6.py
```

To reproduce Q1–Q3 (console output only), edit `run_q6.py` and swap the
active `add_span_processor` call to use `ConsoleSpanExporter` instead
of `SQLiteSpanExporter` (both are already wired in the file, one is
commented out):

```python
provider.add_span_processor(SimpleSpanProcessor(ConsoleSpanExporter()))
# provider.add_span_processor(SimpleSpanProcessor(SQLiteSpanExporter("traces.db")))
```

For Q6, run `run_q6.py` **4 times** with the SQLite exporter enabled so
`traces.db` accumulates 4 runs of the same query.

### 3. Querying the traces (Q4, Q5, Q6)

```bash
uv run python run_query_q4.py   # distinct span names
uv run python run_query_q5.py   # total duration (ms) per span type
uv run python run_query_q6.py   # input tokens per "llm" span
```

## OpenTelemetry concepts used

- **Trace**: the end-to-end story of a single RAG call (one call = one trace)
- **Span**: a single operation within a trace (`rag`, `search`,
  `llm`), organized as a tree
- **Attributes**: key-value pairs attached to a span (e.g.
  `input_tokens`, `output_tokens`, `cost`)
- **Exporter**: determines where finished spans go — console
  (`ConsoleSpanExporter`) or a custom `SQLiteSpanExporter` that
  persists spans into `traces.db`

## Notes

- The Gemini model exposes usage information via
  `response.usage_metadata.prompt_token_count` and
  `response.usage_metadata.candidates_token_count`, unlike the OpenAI
  API (`response.usage.input_tokens` / `output_tokens`).
- Cost is computed using OpenAI's pricing (`$0.75` / 1M input tokens,
  `$4.50` / 1M output tokens) as a stand-in, since the homework's cost
  formula is modeled on OpenAI pricing rather than Gemini's actual
  rates. This is purely illustrative.
- Span timestamps (`start_time`, `end_time`) are expressed in
  **nanoseconds**; `run_query_q5.py` divides by `1_000_000` to report
  durations in milliseconds.
- Answers to the homework questions may vary slightly between runs
  (network latency, model variance) — this is expected and accounted
  for in the questions.

## Resources

- [Original homework](https://github.com/DataTalksClub/llm-zoomcamp/blob/main/cohorts/2026/05-monitoring/homework.md)
- [OpenTelemetry documentation](https://opentelemetry.io/)
- [LLM Zoomcamp](https://github.com/DataTalksClub/llm-zoomcamp/)
