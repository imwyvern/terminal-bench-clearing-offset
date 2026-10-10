# Clearing Offset

One original Terminal-Bench task, `tasks/clearing-offset` (version 1.3.0). A payments engine is supposed to settle batches under a liquidity-saving rulebook (`environment/docs/rules.md`, revision 4). The checked-in engine only walks each priority queue and restarts after every payment, so floors, ceilings, partial lots, offsets with fees, and the round structure are all missing. The job is to make `python -m lumen.settle` match the rulebook for every valid batch, exactly, within 5 seconds per batch on one core and using only the Python standard library.

The layout is the Harbor task format used by [harbor-framework/terminal-bench](https://github.com/harbor-framework/terminal-bench) (the tree the contributing guide now documents). Run it with `harbor run -p tasks/clearing-offset ...`.

This repository is the take-home artifact. It is not a pull request to Terminal-Bench. License: MIT. Results of every check and trial, with job ids, are in [RESULTS.md](RESULTS.md).

## Author

The task author is `imwyvern`. `author_email` is `imwyvern@example.com` because the static check requires an email and the README Author line has to match `task.toml` exactly. Replace that address if you want a real one, and keep the two files in sync. `## Relevant experience` is one honest line and is marked for you to review.

## What the agent sees

`/app/docs/rules.md` is the normative procedure. Participants have a collateral, a reserve and a ceiling. Unilateral payments use a floor (half the reserve for priority 0, the full reserve otherwise) and respect the creditor's ceiling; priority 2 payments can also be paid in partial lots of 5, in a queue ordered by amount. When the unilateral scan is stuck, the best closed and funded bundle of payments is settled at once; every paying participant pays a 5 percent rounded-up fee that counts in the funded test; bundles are ranked by sum, then fewest participants, then most payments, then sorted ids. The procedure runs in rounds that restart at priority 0 after any action. Four fixtures under `/app/fixtures/` have checked reports. The starting `engine.py` passes only the plain chain.

## Verification

Grading does not read the fixture files and does not import the submitted package into the root test process. `tests/test.sh` runs pytest, which executes `python -m lumen.settle` as `nobody` with a fresh environment and a 5 second timeout per batch on 64 stored batches in `tests/cases/`. Reports must match on the set of settled ids, the set of unsettled ids, and integer balances. `/tests` is mode `0700`, so the unprivileged process cannot read the stored reports or the transcription in `tests/reference.py`. The only agent artifact uploaded is `/app/src/`. Reward is `1` only when pytest exits 0.

The stored reports come from `tools/ref_np.py`, an offline numpy brute force over all subsets that shares no search code with the oracle. `tools/build_cases.py` regenerates all cases and also writes, for each of eleven single wrong readings of one rule (`tools/mutants.py`, `tools/ref_tie.py`), the two smallest batches that the wrong reading gets wrong, so each such reading fails at least two stored cases. A separate three-way check (oracle branch and bound, pure-Python brute force, numpy brute force) agreed on tens of thousands of random batches while the task was built. An independent scipy MILP with lexicographic tie-breaking agreed with the earlier bundle-only rules.

## Design notes

The procedure is original. It is in the family of RTGS liquidity-saving mechanisms (unilateral funding, then a multilateral offset), but the floors, ceilings, lots, fee, tie chain, and round structure are specific to this rulebook so a memorized netting writeup does not settle the hidden batches. The offset step is an exact optimization (the best closed, funded subset of payments), not a heuristic gridlock algorithm.

### Iteration history (honest account)

The task was hardened four times because strong models passed earlier versions. Details and job ids are in RESULTS.md.

- `1.0.0`: the offset step was "best 2-cycle or 3-cycle". A smoke trial of codex `gpt-6.1-sol` (xhigh) and of terminus-2 `deepseek-flash` each scored reward 1 on their first trial. Too easy, so it was not submitted in that form.
- `1.1.0`: the offset step became "best closed and funded bundle" (exact subset optimization), with size and time limits. A deepseek trial scored 0 but only because its solution imported scipy and numpy, which it had installed in the agent container and which are missing from the separate verifier image. That is an infrastructure-style failure, not a rulebook failure, so it does not count. The codex trial of that job was stopped before it finished.
- `1.1.1`: the instruction and rulebook now say the grader has only the Python standard library. codex `gpt-6.1-sol` then passed its first trial (reward 1) with a 950-line exact branch-and-bound over a min-cost-flow relaxation. A strong exact solver was not enough, so scale was not the right lever.
- `1.2.0`: the rulebook was rewritten as revision 3 so that exactness on several interacting rules, not only a fast solver, decides the reward: priority-dependent floors, creditor ceilings, priority-2 partial lots and queue order, an offset fee that counts in the funded test, a participant-count tie-break before the payment-count tie-break, and a round loop that restarts at priority 0. The verifier cases were extended with mutation-checked batches. In its first batch of trials, one deepseek trial still passed by compiling a C solver and a static GLPK binary into `/app/src`, which the earlier wording technically allowed.
- `1.2.1`: the rulebook and the grader now require pure Python: no native files, `ctypes`, `subprocess`, extra processes or threads. In 1.2.1, terminus-2 deepseek-flash passed 2 of 2 finished trials with a pure-Python branch-and-bound engine of 571 and about 400 lines (the third trial was stopped), so rule exactness at that level was not enough for it.
- `1.3.0`: rulebook revision 4 adds two stateful rules that interact with everything else and that the worked examples only partly show: payment aging (a payment waiting behind more urgent work becomes more urgent after three acting rounds, which changes its floor, queue, partial-lot rights, and bundle membership) and strain (a debtor that has made a partial settlement loses the priority-0 half floor for the rest of the run). The verifier gained 5 aging/strain mutant-killer pairs, 8 larger aging cases, and 10 mined dense batches that are slow for naive branch-and-bound; every expected report was also checked against `tools/ref_milp.py`, a second independent reference that solves each bundle step as an exact lexicographic MILP. The trials of this version are in RESULTS.md.

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

`/cheat` is the same command with `-k 1` and `--extra-instruction-path` pointing at `docs/prompts/hack-trial-prompt.md` from `harbor-framework/terminal-bench`. `scripts/run-trials.sh` downloads that file. The file is the official `docs/prompts/hack-trial-prompt.md` from `harbor-framework/terminal-bench` main, used verbatim.

### Current CI defaults

`terminal-bench` `.github/harbor-run-defaults.yml` on main, as fetched on 2026-10-10, runs three trials of `claude-code` / `anthropic/claude-fable-5-1` at `reasoning_effort=max` (with `CLAUDE_CODE_MAX_OUTPUT_TOKENS=128000`) and `codex` / `openai/gpt-6-astra` at `reasoning_effort=xhigh`. A `/cheat` comment forces one attempt and prepends `docs/prompts/hack-trial-prompt.md`. The assignment text names `gpt-6.1-sol` for codex, which differs from the `gpt-6-astra` default in that file; the commands above follow the assignment text and the take-home substitution (gpt-6.1-sol plus DeepSeek V4.1 Flash) because there is no Claude subscription. Record the runs you actually execute.

## Layout

```
tasks/clearing-offset/
  instruction.md
  task.toml
  README.md
  environment/          # agent image: buggy engine, rulebook, four fixtures
  solution/             # oracle engine installed by solve.sh
  tests/                # separate verifier image, 64 stored cases, brute-force transcription
tools/                  # offline: case builder, numpy brute force, mutation switches
scripts/run-trials.sh
scripts/codex.config.toml
RESULTS.md
```
