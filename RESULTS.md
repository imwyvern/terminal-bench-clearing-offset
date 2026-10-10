# Results

Only rows with a command and an observed result were filled in. Everything else is marked `TO BE FILLED BY DAN`. No trial reward below was invented.

Harbor pin: `0.23.1.dev202609170426`, from `harbor-framework/terminal-bench` `.github/harbor-version` on main, fetched 2026-10-10. Static scripts are that repo's `scripts/checks/`.

## Static checks

Run from `/workspace` on 2026-10-10 against `tasks/clearing-offset`, using `scripts/checks/check-*.sh` from a depth-1 clone of `harbor-framework/terminal-bench` main. `dockerfile-pin` v1.5.0 was on `PATH` for the digest check. Every script exited 0.

| Check | Result |
| --- | --- |
| Canary strings | PASS |
| No cheat directory | PASS |
| Dockerfile refs | PASS |
| Image digest pins | PASS |
| Dockerfile sanity | PASS |
| Dockerfile platform | PASS |
| Absolute paths | PASS |
| Test refs | PASS |
| test.sh sanity | PASS |
| Task fields | PASS |
| Task fix changelog | PASS |
| Task timeout cap | PASS |
| Instruction suffix | PASS |
| Instruction headings | PASS |
| GPU types | PASS |
| Resource sizes | PASS |
| Allow internet | PASS |
| No internet opt-in | PASS |
| Task slug length | PASS |
| Task package name | PASS |
| Separate verifier | PASS |
| Verifier tooling baked | PASS |
| Trial network fetch | PASS |
| Pip pinning | PASS |
| Pytest version pin | PASS |
| Nproc usage | PASS |
| Compose host binds | PASS |
| AI detection (`check_ai_detection.py`) | not run; `GPTZERO_API_KEY` unset, and this script is not in `.github/workflows/static-checks.yml` |

## Implementation rubric

| Check | Result |
| --- | --- |
| `harbor check tasks/clearing-offset -r docs/prompts/task-implementation.toml` | TO BE FILLED BY DAN |

Not run here. `harbor check` needs a model API key. The rubric file is `docs/prompts/task-implementation.toml` in `harbor-framework/terminal-bench`.

## Docker build

Harbor builds both images as part of `harbor run`. The successful oracle job below built `environment/Dockerfile` and `tests/Dockerfile` (the verifier image installs `pytest==9.1.1` and `pytest-json-ctrf==0.5.2` at build time). Base image: `python:3.12-slim-bookworm@sha256:34386ef0cb081344d7ec1c103ba398e6e9f64e9ab3a1509accc92a4e24a07258`.

The first `harbor run` on this machine failed before any image build: Docker 29 had no Compose plugin, and the default containerd overlay snapshotter cannot nest overlay mounts here. After `docker-compose-v2` was installed and dockerd was restarted with the `vfs` storage driver, the builds succeeded. That was a local daemon limitation, not a task failure.

| Image | Result |
| --- | --- |
| `tasks/clearing-offset/environment` | built during the oracle job on 2026-10-10 (job `jobs/oracle/2026-10-10__03-12-15`) |
| `tasks/clearing-offset/tests` | built during the same job; verifier then ran |

## Oracle and nop

Harbor `0.23.1.dev202609170426`. Commands were `harbor run -p tasks/clearing-offset --agent oracle --env docker --yes` and the same with `--agent nop`.

| Trial | Reward | Result |
| --- | --- | --- |
| oracle, job `2026-10-10__03-12-15`, trial `clearing-offset__vzuuxvH` | 1 | 38 passed in 4.30s, no exceptions. Mean reward 1.000. |
| nop, job `2026-10-10__03-12-52`, trial `clearing-offset__nHHxBUX` | 0 | 13 failed, 25 passed in 4.45s, no exceptions. Mean reward 0.000. |

Nop failures were the hand batches `02-ring`, `03-reserve-ring`, `04-scan-order`, `06-priority`, `07-multi-edge`, `09-lex-tie`, `10-amount-tie`, `11-length-tie`, `12-after-cycle`, and seeded batches `seed-2`, `seed-12`, `seed-14`, `seed-15`. The reference self-check passed. The starting engine still passes `01-chain`, `05-greedy-blocks`, `08-second-pass`, and `13-id-tie`.

## Standard trials (`/run`)

Take-home pair after the allowed substitution: Codex, plus DeepSeek V4.1 Flash in place of Claude. Three trials each. A pass, a crash, a rate limit, or a timeout does not count as the model failing the verifier. These rows stay empty until a real trial finishes.

| Trial | Model | Reward | Notes |
| --- | --- | --- | --- |
| `/run` 1 | codex `openai/gpt-6.1-sol` `reasoning_effort=xhigh` | TO BE FILLED BY DAN | |
| `/run` 2 | codex `openai/gpt-6.1-sol` `reasoning_effort=xhigh` | TO BE FILLED BY DAN | |
| `/run` 3 | codex `openai/gpt-6.1-sol` `reasoning_effort=xhigh` | TO BE FILLED BY DAN | |
| `/run` 1 | terminus-2 `deepseek/deepseek-flash` `reasoning_effort=max` | TO BE FILLED BY DAN | |
| `/run` 2 | terminus-2 `deepseek/deepseek-flash` `reasoning_effort=max` | TO BE FILLED BY DAN | |
| `/run` 3 | terminus-2 `deepseek/deepseek-flash` `reasoning_effort=max` | TO BE FILLED BY DAN | |

## Adversarial trials (`/cheat`)

CI forces one attempt and prepends `docs/prompts/hack-trial-prompt.md`. Any reward other than 0 fails this requirement.

| Trial | Model | Reward | Notes |
| --- | --- | --- | --- |
| `/cheat` | codex `openai/gpt-6.1-sol` `reasoning_effort=xhigh` | TO BE FILLED BY DAN | |
| `/cheat` | terminus-2 `deepseek/deepseek-flash` `reasoning_effort=max` | TO BE FILLED BY DAN | |

## Failure analysis

TO BE FILLED BY DAN after the trials. For each failing trial, note whether the run finished and the verifier returned 0, or the run died on infrastructure (crash, auth, rate limit, timeout, container). Only verifier failures count. Then:

- Which rule the submitted engine got wrong (scan restart, reserve applied to offsets, priority order, cycle tie-break, multi-edge selection, or something else).
- Whether the four fixtures passed while hidden batches failed.
- Whether `/cheat` found a real bypass or stopped at reward 0.

### Pre-assessment (estimate, not a result)

No subscriptions were available while this repo was built, so this is not a trial outcome. The rulebook is fully specified and the oracle is short, so a careful implementation should pass. The plausible misses are the ones the starting engine already makes, plus inverting the amount / length / tuple order. Fixtures catch the ring, the reserve ring, and the scan. They do not catch priority, multi-edge selection, or the tie-breaks. A model that patches until the four fixtures pass, and does not build its own cases from the rulebook, should score 0. A model that transcribes the rulebook and tests the worked examples can score 1. I would not claim a 0/3 fail rate without the runs.

## Local log

Static checks: 27/27 `check-*.sh` scripts exited 0 on 2026-10-10. Re-run after the CTRF test-id cleanup, still 27/27. `check-task-fields.sh` was run again after the author fields were set to `imwyvern` and passed.

`scripts/run-trials.sh parse` on 2026-10-10, with `APIKEYCLAW_API_KEY` and `DEEPSEEK_API_KEY` unset: `--print-config` accepted both agents, and `--dry-run` reported `Dry run OK` for Codex x3, DeepSeek x3, and one `/cheat` each. That is a flag parse, not a trial. Rewards above stay empty.

Oracle stdout (abridged): `Trials 1`, `Exceptions 0`, `Mean 1.000`, reward count `1.0: 1`, runtime 33s, results in `jobs/oracle/2026-10-10__03-12-15`. `reward.txt` contains `1`.

Nop stdout (abridged): `Trials 1`, `Exceptions 0`, `Mean 0.000`, reward count `0.0: 1`, runtime 31s, results in `jobs/nop/2026-10-10__03-12-52`. `reward.txt` contains `0`. Pytest summary: `13 failed, 25 passed in 4.45s`.
