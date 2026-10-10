# Clearing Offset

One original Terminal-Bench task, `tasks/clearing-offset`. A payments engine is supposed to settle batches under a small liquidity-saving rulebook. The checked-in engine only walks each priority queue and restarts after every payment, so rings, reserve-backed offsets, and the scan rule are wrong. The job is to make `python -m lumen.settle` match `/app/docs/rules.md` for every valid batch.

The layout is the Harbor task format used by [harbor-framework/terminal-bench](https://github.com/harbor-framework/terminal-bench) (the tree the contributing guide now documents). Run it with `harbor run -p tasks/clearing-offset ...`.

This repository is the take-home artifact. It is not a pull request to Terminal-Bench. License: MIT.

## Author

The task author is `imwyvern`. `author_email` is `imwyvern@example.com` because the static check requires an email and the README Author line has to match `task.toml` exactly. Replace that address if you want a real one, and keep the two files in sync. `## Relevant experience` is one honest line and is marked for you to review.

## What the agent sees

`/app/docs/rules.md` is the normative procedure: unilateral payments respect a reserve and a full-queue scan, then at most one simultaneous 2-cycle or 3-cycle is settled, priorities 0 then 1 then 2. Four fixtures under `/app/fixtures/` have checked reports. The starting `engine.py` passes the plain chain and fails the ring, the reserve ring, and the scan-order fixture.

## Verification

Grading does not read the fixture files and does not import the submitted package into the root test process. `tests/test.sh` runs pytest, which executes `python -m lumen.settle` as `nobody` with a fresh environment and a 5 second timeout per batch. Reports must match on the set of settled ids, the set of unsettled ids, and integer balances.

Hand batches in `tests/cases/` cover the reserve, the scan, priority isolation, multi-edge selection, a unilateral payment that blocks an offset, an offset that frees a later payment, and the amount, length, and id tie-breaks. Twenty-four further batches are drawn from seed `20261010` inside the verifier image. Their expected reports are computed by `tests/reference.py`, a second transcription of the rulebook. `/tests` is mode `0700`, so the unprivileged process cannot read that transcription or the tests. The only agent artifact uploaded is `/app/src/`.

Reward is `1` only when pytest exits 0, otherwise `0`. Per-test results go to `/logs/verifier/ctrf.json`.

## Design notes

The procedure is original. It is in the family of RTGS liquidity-saving mechanisms (unilateral funding, then a bilateral or trilateral offset), but the scan rule, the reserve exception, and the tie-break are specific to this rulebook so a memorized netting writeup does not settle the hidden batches.

The first draft specified the procedure only as "settle feasible cycles." That has more than one reading, so the rulebook now fixes the order of operations and includes four worked batches. Array order in the report is defined as insignificant so a correct engine is not failed for sorting. The oracle and the verifier transcription were checked against those worked batches by hand before the expected JSON was frozen. The checked-in engine still fails nine of the thirteen hand batches, which is what the no-op trial grades.

A likely way a strong model fails, if it fails, is to implement a plausible neighbor of the rulebook: restart the scan after each settlement, refuse offsets that pierce the reserve, or pick the lexicographically first cycle before comparing amounts. Those all clear some fixtures and fail others. This is an estimate from the shape of the rules, not a trial result. No model subscriptions were available in the environment that built this repo, so no `/run` or `/cheat` reward is recorded here.

## Checks and trials

Harbor version pinned by Terminal-Bench main on 2026-10-10: `0.23.1.dev202609170426`.

```bash
uv tool install "harbor==0.23.1.dev202609170426"
```

Static checks, from a checkout of `harbor-framework/terminal-bench` (the scripts are not vendored here):

```bash
git clone --depth 1 https://github.com/harbor-framework/terminal-bench.git /tmp/terminal-bench
# check-image-digests.sh needs dockerfile-pin on PATH (CI uses v1.5.0)
for check in /tmp/terminal-bench/scripts/checks/check-*.sh; do
  bash "$check" tasks/clearing-offset || echo "FAILED $check"
done
```

`scripts/checks/check_ai_detection.py` is not in the static-check workflow. It calls GPTZero and skips itself when `GPTZERO_API_KEY` is unset. The implementation rubric is `harbor check`, which needs a model API key:

```bash
harbor check tasks/clearing-offset -r /tmp/terminal-bench/docs/prompts/task-implementation.toml
```

Oracle and no-op, from this repo:

```bash
scripts/run-trials.sh oracle
scripts/run-trials.sh nop
```

### Assignment trials

Dan has no Claude subscription, so the pair is Codex plus the allowed DeepSeek substitution. `scripts/run-trials.sh` wraps the commands. Keys stay in the environment.

```bash
export APIKEYCLAW_API_KEY='...'
export DEEPSEEK_API_KEY='...'

scripts/run-trials.sh codex-run      # 3 trials
scripts/run-trials.sh codex-cheat    # 1 trial, hack prompt prepended
scripts/run-trials.sh deepseek-run
scripts/run-trials.sh deepseek-cheat

# Flag parse and local dry-run. Does not call a model and does not need keys.
scripts/run-trials.sh parse
```

The take-home sample omits the trial count because CI puts it in the job config (`n_attempts`). On the Harbor CLI installed here, that flag is `-k` / `--n-attempts`. `-n` is concurrency, not the number of trials.

#### Codex

Put this in `~/.codex/config.toml`. The same file is checked in at `scripts/codex.config.toml`. It names the env var. It does not contain the key.

```toml
model = "gpt-6.1-sol"
model_provider = "apikeyclaw"

[model_providers.apikeyclaw]
name = "API Key Claw"
base_url = "https://sub2api.apikeyclaw.com/v1"
wire_api = "responses"
env_key = "APIKEYCLAW_API_KEY"
```

Harbor's Codex agent does not read `~/.codex/config.toml` by itself. `Codex._load_base_config` loads the path or inline object passed as the `config` kwarg (`--ak config=<path>`). It then builds an effective TOML. If `OPENAI_BASE_URL` is set, that value overwrites the top-level `openai_base_url` key, which is the built-in OpenAI provider and does not set `wire_api`. Leave `OPENAI_BASE_URL` unset so the `[model_providers.apikeyclaw]` block is what Codex uses. Harbor uploads the result to `$CODEX_HOME/config.toml` inside the agent container (`/tmp/codex-home/config.toml`) and runs `codex exec --model gpt-6.1-sol` (the `openai/` prefix is stripped). `model_reasoning_effort=xhigh` is added with `-c` from `--ak reasoning_effort=xhigh`.

Auth for this endpoint is `env_key`, not a ChatGPT login. Do not set `CODEX_FORCE_AUTH_JSON`. Harbor's default path still writes a container `auth.json` from `OPENAI_API_KEY`; leave that variable unset. Pass the real key only as `APIKEYCLAW_API_KEY`. `--ae` puts it in the container, and Harbor stores `${APIKEYCLAW_API_KEY}` in the job config when the value matches the host environment.

```bash
export APIKEYCLAW_API_KEY='...'
harbor run -p tasks/clearing-offset \
  --agent codex --model openai/gpt-6.1-sol \
  --env docker --yes \
  --ak config=scripts/codex.config.toml \
  --ak reasoning_effort=xhigh \
  --ae "APIKEYCLAW_API_KEY=${APIKEYCLAW_API_KEY}" \
  -k 3
```

#### DeepSeek

Harbor `0.23.1.dev202609170426` and current Harbor `main` have no agent named `deepseek`. The provider entry in `harbor/agents/model_connection.py` is:

- provider `deepseek`
- API key env `DEEPSEEK_API_KEY`
- default base URL `https://api.deepseek.com`
- optional override `DEEPSEEK_BASE_URL`

LiteLLM in that pin lists `deepseek/deepseek-flash`. DeepSeek's API docs for V4.1 Flash say to set the model to `deepseek-flash`. The compatibility id `deepseek-v4-flash` still routes to V4.1 Flash. The Harbor model string used here is `deepseek/deepseek-flash`.

`terminus-2` is the agent in this pin that calls that provider directly and accepts `reasoning_effort` values including `max`. It runs LiteLLM in the Harbor process, so `DEEPSEEK_API_KEY` has to be exported in the shell that launches `harbor`, not only inside the task container. This pin's LiteLLM maps any `reasoning_effort` other than `none` to DeepSeek `thinking` enabled or disabled. The string `max` is stored on the Harbor job. It is not sent as the effort level.

```bash
export DEEPSEEK_API_KEY='...'
harbor run -p tasks/clearing-offset \
  --agent terminus-2 --model deepseek/deepseek-flash \
  --env docker --yes \
  --ak reasoning_effort=max \
  --ae "DEEPSEEK_API_KEY=${DEEPSEEK_API_KEY}" \
  -k 3
```

`/cheat` is the same command with `-k 1` and `--extra-instruction-path` pointing at `docs/prompts/hack-trial-prompt.md` from `harbor-framework/terminal-bench`. `scripts/run-trials.sh` downloads that file.

### Current CI defaults

`terminal-bench` `.github/harbor-run-defaults.yml` on main, as fetched on 2026-10-10, runs three trials of `claude-code` / `anthropic/claude-fable-5-1` at `reasoning_effort=max` (with `CLAUDE_CODE_MAX_OUTPUT_TOKENS=128000`) and `codex` / `openai/gpt-6-astra` at `reasoning_effort=xhigh`. A `/cheat` comment forces one attempt and prepends `docs/prompts/hack-trial-prompt.md`. The commands above follow the take-home substitution (gpt-6.1-sol plus DeepSeek V4.1 Flash) because there is no Claude subscription. Record the runs you actually execute.

## Layout

```
tasks/clearing-offset/
  instruction.md
  task.toml
  README.md
  environment/          # agent image: buggy engine, rulebook, four fixtures
  solution/             # oracle engine installed by solve.sh
  tests/                # separate verifier image, cases, reference transcription
scripts/run-trials.sh
scripts/codex.config.toml
RESULTS.md
```
