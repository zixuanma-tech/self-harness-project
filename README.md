# Self-Harness Demo

This project is a **minimal runnable Self-Harness prototype with real LLM-backed candidate generation**.

It implements the core loop you asked for:

1. the agent generates a candidate modification through a real LLM call,
2. `AdmissionController` decides `accept` / `reject` / `quarantine`,
3. validators are executed with `pytest`,
4. failure signatures are logged,
5. the loop continues across rounds.

The goal of this repository is **not** to present a full research system yet, but to provide a small, executable prototype of the process-control logic under actual model calls.

## What this demo is

This repository is intended to be:

- runnable,
- readable,
- easy to explain,
- easy to extend into a larger benchmark-style prototype.

Compared with a purely heuristic toy loop, the current version already uses **real LLM invocation** for candidate generation, so the prototype now better matches the intended research direction.

## What the demo does

The system under test is a tiny order / inventory / payment / refund workflow with deliberately limited scope.

The loop is organized around three admission actions:

- **reject**: hard constraints or core regression obligations fail,
- **quarantine**: hard constraints pass but soft issues remain,
- **accept**: all required checks pass and the candidate is merged into mainline.

That gives a concrete minimal example of **process-time reliability control** through `reject / quarantine / accept`.

## Project structure

```text id="19462"
minimal_self_harness/
├── main.py
├── pyproject.toml
├── README.md
└── self_harness_demo/
    ├── __init__.py
    ├── admission.py
    ├── agent.py
    ├── env.py
    ├── llm_client.py
    ├── logger.py
    ├── loop.py
    ├── models.py
    ├── patches.py
    ├── pytest_runner.py
    ├── synth.py
    └── validator_materializer.py
````

## Quick start

### With `uv`

```bash id="10223"
uv sync
uv run python main.py --runtime-dir ./runtime --max-rounds 4
```

### With plain `pip`

```bash id="93054"
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e .
python main.py --runtime-dir ./runtime --max-rounds 4
```

## LLM configuration

Before running the LLM-backed version, make sure your model access is configured correctly.

The current client expects these environment variables:

```bash id="26443"
OPENAI_API_KEY=your_api_key
OPENAI_BASE_URL=your_base_url
OPENAI_MODEL=your_model_name
```

Examples:

* `OPENAI_API_KEY`: your provider token
* `OPENAI_BASE_URL`: API endpoint such as an OpenAI-compatible `/v1`
* `OPENAI_MODEL`: the model name you want to call

If `OPENAI_BASE_URL` or `OPENAI_MODEL` is omitted, the code may fall back to its internal defaults.

## What to inspect after running

### 1. Round logs

Open:

```text id="84297"
runtime/logs/rounds.jsonl
```

Each row may contain:

* round id,
* source workspace,
* candidate patch name,
* action (`baseline`, `accept`, `reject`, `quarantine`),
* hard failures,
* soft failures,
* generated validators,
* model-generated candidate summaries.

### 2. Workspaces

The runtime directory stores branch states and candidate workspaces, which makes it easier to inspect what happened in each round.

Typical examples include:

* a mainline workspace,
* one or more candidate workspaces,
* quarantined branches,
* later accepted mainline states.

## Where each paper concept lives in code

* **Harness state**: `models.HarnessState`
* **Failure signatures**: `models.FailureSignature`
* **Admission semantics**: `admission.AdmissionController`
* **Validator execution**: `pytest_runner.run_pytest_validation`
* **Failure-driven expansion**: `synth.ValidatorSynthesizer`
* **Round loop**: `loop.SelfHarnessLoop`
* **LLM-backed candidate generation**: `agent.LLMAgent`
* **LLM transport**: `llm_client.ask_llm`

## Current scope and limitations

This is still a **minimal prototype**, not the final research system.

Current limitations may include:

* small task scope,
* limited validator diversity,
* lightweight branch management,
* no full benchmark integration yet,
* no large-scale workload study yet.

So the repository should be read as a **research prototype for mechanism validation**, not as the final long-horizon system.

## How this can be extended

Natural next steps include:

1. replacing the current toy task with a richer toy repo or e-commerce prototype,
2. adding more validators and runtime monitors,
3. improving quarantine branch management,
4. connecting the loop to benchmark environments such as TerminalBench-style or SWE-Bench-style settings,
5. expanding workload evolution and failure-driven validator synthesis.

## Summary

This repository is a **minimal but real LLM-backed prototype** of the Self-Harness loop.

Its purpose is to demonstrate, in executable form, the central research idea:

> candidate generation alone is not enough for long-horizon system building;
> an internal process-time control layer is needed to decide what gets accepted, rejected, or quarantined.

