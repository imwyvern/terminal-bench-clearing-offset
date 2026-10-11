# Results

Every reward below was read from a Harbor `result.json` or `verifier/ctrf.json` on the Mac mini that ran the trials. Nothing is invented. Rows marked PENDING are trials that had not finished when this file was last written. The final version of the task is `1.4.0`; the history of earlier versions is kept because it explains why the task changed.

Harbor pin: `0.23.1.dev202609170426`, from `harbor-framework/terminal-bench` `.github/harbor-version` on main, fetched 2026-10-10. Static scripts are that repo's `scripts/checks/`.

## Static checks

Run from `/workspace` on 2026-10-10 against `tasks/clearing-offset` (re-run on version 1.4.0, all 27 scripts exit 0), using `scripts/checks/check-*.sh` from a depth-1 clone of `harbor-framework/terminal-bench` main. `dockerfile-pin` v1.5.0 was on `PATH` for the digest check. Every script exited 0.

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

## Oracle and nop (final version 1.4.0)

Harbor `0.23.1.dev202609170426`, run on the Mac mini from a clone at commit `9bbd8e8`: `harbor run -p tasks/clearing-offset --agent oracle|nop --env docker --yes`.

| Trial | Job id | Reward | Result |
| --- | --- | --- | --- |
| oracle (`oracle-v8`) | `420fe412-14d6-4534-9f6a-48f76d8c8bc0`, trial `PhM7CTv` | 1 | 108 passed, 0 failed |
| nop (`nop-v8`) | `c967cdce-6b50-40fa-8ef7-8235d164ee88`, trial `Drcs6mQ` | 0 | 11 passed, 97 failed |

Earlier versions were checked the same way (oracle reward 1, nop reward 0 every time): 1.1.0 oracle `fe56594b-665c-4555-b9a6-8576873a3277`, nop `357b2f3e-bedb-48fc-9541-61d42108ed0e`; 1.1.1 oracle `64904282-0aa8-4fe6-8227-3170e3a11923`, nop `f30af9a3-53f7-45cc-83c4-76f548593057`; 1.2.0 oracle `458dc6b4-e041-4d7a-baa3-34320f9fa05b`, nop `d615c90c-ff09-4990-bcf7-d3913d90b5cd`; 1.2.1 oracle `cdc32a84-5112-4319-a48f-1e14d9db89b6`, nop `feedd350-c0d9-40fa-9ead-f99a4412b872`; 1.3.0 oracle `6a2872f4-869e-4d62-b7ed-1305161b14ef`, nop `687334d6-3ce5-4bf4-9396-59d86758fdfb`; 1.3.1 oracle `d3b9efa3-8cd8-4c2f-a782-1eddae93b0fc`, nop `eb2e3ef8-bdf2-4cab-8d63-7108dcbb7871`.

## Standard trials (`/run`) on the final version 1.4.0

Take-home pair after the allowed substitution: Codex plus DeepSeek V4.1 Flash in place of Claude. Three trials each, `-k 3 -n 3`, launched together. Only a run that finished and was graded by the verifier counts; infrastructure errors do not. Commit `9bbd8e8`, job directories in `~/tb3-v121/jobs` on the Mac.

| Trial | Model | Job id / trial | Reward | Notes |
| --- | --- | --- | --- | --- |
| `/run` 1 | terminus-2 `deepseek/deepseek-flash` `reasoning_effort=max` | `c82cd146-67cd-44c7-a1a5-3574b97e1ec5` / `W2hnKub` | **0** | Finished, no exception, 153 steps, about 1h19m. 105 of 108 tests passed. The 3 failures are timeouts at 5 s on `801-long-lots`, `803-long-lots` and `809-long-lots`. Valid failure: the verifier ran and returned 0. |
| `/run` 2 | terminus-2 `deepseek/deepseek-flash` | same job / `5k5MmBz` | **0** | Finished, no exception, 151 steps, about 1h56m. 105 of 108 passed; the 3 failures are the same timeouts at 5 s on `801`, `803`, `809-long-lots`. Valid failure. |
| `/run` 3 | terminus-2 `deepseek/deepseek-flash` | same job / `xxWynm2` | **0** | Finished, no exception, 280 steps, about 2h34m. 105 of 108 passed; the same 3 timeouts. Valid failure. |
| `/run` 1 | codex `openai/gpt-6.1-sol` `reasoning_effort=xhigh` | `20623c7a-5f62-49e4-b03d-81ed9fcad06f` | PENDING | running since 2026-10-10 about 20:06 PT. Codex trials of the previous version took about 8 hours each. |
| `/run` 2 | codex `openai/gpt-6.1-sol` | same job | PENDING | |
| `/run` 3 | codex `openai/gpt-6.1-sol` | same job | PENDING | |

## Adversarial trials (`/cheat`) on the final version 1.4.0

The prompt is the official `docs/prompts/hack-trial-prompt.md` from `harbor-framework/terminal-bench` main, fetched verbatim (2755 bytes, identical to the copy used in all earlier cheat attempts) and passed with `--extra-instruction-path`, one attempt (`-k 1`).

| Trial | Model | Job id / trial | Reward | Notes |
| --- | --- | --- | --- | --- |
| `/cheat` | terminus-2 `deepseek/deepseek-flash` | `ded92a35-6f74-4e06-866e-b3027e4b87d0` / `nL9HeyF` | 0 | Finished, no exception. |
| `/cheat` | codex `openai/gpt-6.1-sol` | `d5f7379b-ec09-43e4-8b1b-5b0b35009ce6` / `LZRLrgd` | no result | Could not be run through the apikeyclaw endpoint: safety refusal. The endpoint returned `This content was flagged for possible cybersecurity risk ... apply for Daybreak access` and Harbor recorded `AgentSafetyRefusalError` before the agent took any action. Harbor stores reward 0.0 for the trial, but no agent ran, so this is not evidence that the task resists cheating. |

The same refusal happened on every earlier Codex `/cheat` attempt with the same official prompt: jobs `2aaa986d-d493-4296-a73a-6a24aeed21d8` (trial `LjZVEMp`) and `4d803bab-b8ff-4e3c-83d3-ca2ee73ba460` (trial `3QTrMiD`) on 1.1.1, and `89279a0b-c1ad-4bfc-83d2-f46ec9986ee8` (trial `A6RiZLe`) on 1.3.1. I did not rephrase the prompt to get around the safeguard.

DeepSeek `/cheat` on earlier versions also ended at reward 0: 1.1.1 job `4e87f73b-c1e4-4c06-9d39-78224f1c95ca` (`pk6yzS6`, 11 of 39 passed), 1.2.0 job `9a41ffd5-24db-4fed-b6c6-7b8660790da6` (`YwsbZZr`), 1.3.1 job `4ee9410e-f33d-4f00-8983-8994d08d7f0b` (`XH75WjU`, 19 of 96 passed). In the 1.3.1 trial the agent built a lookup table of hashes of the public fixtures and sidecar `*.expected.json` files and also sketched scraping the parent test process; none of that produces reports for the hidden batches, so the verifier gave 0. The 1.4.0 trajectory has not been read yet (PENDING).

## Iteration history with every trial

The take-home requires every standard trial to get reward 0. That is not met by any version so far; the table is the honest record.

| Version | Job (id) | Model | Trial | Reward | Notes |
| --- | --- | --- | --- | --- | --- |
| 1.0.0 | `6a19643e-0258-47c4-bae4-51eb5351d834` | codex | `bDsLBf8` | 1 | smoke trial, offset step was best 2- or 3-cycle |
| 1.0.0 | `84ec04b6-442c-4820-bb07-bcfc098d7da4` | deepseek | `eyU9YmN` | 1 | smoke trial |
| 1.1.0 | `ea2ad955-868c-4ebf-a57d-af3f583a5e79` | deepseek | `uy5ajzS` | 0 (invalid) | failed because its solution imported scipy/numpy, installed only in the agent container, missing from the separate verifier image. Spec gap, not a model failure; fixed in 1.1.1 by stating that the grader has only the standard library. |
| 1.1.0 | `24d8f00e-3866-4159-a49a-9953870e6902` | codex | none | stopped unfinished | |
| 1.1.1 | `c3fcb159-c26e-4fdf-a677-38c00285d1a4` | codex | `6X75Wdc` | 1 | 39 of 39, about 1h09m, 950-line exact branch and bound |
| 1.1.1 | `c19aa428-40ec-423d-92db-816ef74e8a1e` | deepseek | none | stopped unfinished | |
| 1.2.0 | `5853eb80-2df4-4ad0-90da-97b6f068b7c3` | deepseek | `WEcwadv` | 1 | passed by compiling C and a static GLPK binary into `/app/src` (a loophole), so 1.2.1 requires pure Python. Other trials stopped. |
| 1.2.0 | `bc478286-df3e-41fd-a745-936b88380a67` | codex | none | stopped after about 4 h with 0 of 3 finished | the version was obsolete |
| 1.2.1 | `deepseek-run-e` | deepseek | `j2QjLEM`, `88uzCwD` | 1, 1 | pure-Python engines; third trial stopped |
| 1.3.0 | `50c9312c-0979-4127-b798-a8a96d69cca3` | codex | `GUScTxN` | 0 (invalid) | passed 95 of 96 tests; the only failure was my purity check flagging a method named `fork` in its own pure-Python LP class, a false positive fixed in 1.3.1. With the fix the trial would have passed. Not counted. |
| 1.3.0 | `cb59e635-1c82-4280-a4a9-8e13418e224b` | deepseek | `Yqv4LS8` | 1 | 96 of 96, 542-line pure Python, about 1h36m |
| 1.3.1 | `d732bfa4-ec74-483d-aae5-34885430999b` | deepseek | `dg8onbT`, `MTDpdGD`, `j627cEx` | 1, 1, 1 | 96 of 96 each; 601, 1140 and 729 lines |
| 1.3.1 | `e46bba92-c812-4acb-b0e7-87650884e1c0` | codex | `Y9tFDJe`, `g3HHPyp`, `qcTh47T` | 1, 1, 1 | 96 of 96 each; 5083, 2792 and 4084 lines of pure Python; each ran about 8 hours and `qcTh47T` hit the 8 h agent timeout (`AgentTimeoutError`) but its submitted code was graded and passed |
| 1.4.0 | see above | | | | final version |

The 1.4.0 hardening came from checking the three Codex 1.3.1 engines on 12 random huge-pass batches: all three solved them in under 0.2 s and matched the oracle, without being told. DeepSeek's three 1.3.1 engines timed out on 2 of 12. I therefore expected 1.4.0 to affect DeepSeek far more than Codex.

## Failure analysis

### DeepSeek (terminus-2, `deepseek-flash`)

- 1.4.0, all three trials (`W2hnKub`, `5k5MmBz`, `xxWynm2`) are valid failures with reward 0. Each run finished normally, with no exception. Each submitted a pure-Python engine of 671, 534 and 473 lines that was correct on 105 of 108 tests, including all hand batches, mutant-killer batches, aging and strain batches, and mined dense batches. The same three tests timed out at 5 s in all three trials: `801-long-lots`, `803-long-lots` and `809-long-lots`. These are priority-2 phases that make hundreds of millions of passes. I re-ran the three submitted engines on those batches offline and they still had not finished after 120 s, so this is a speed failure and not a wrong answer. The failures are not infrastructure errors.
- What the trajectories show: all three agents read the rulebook's statement that a phase can take tens of millions of passes, tried the worked many-pass example, and wrote an accelerated priority-2 phase (`W2hnKub` step 9: an "event-batched priority-2 unilateral phase"; `5k5MmBz` steps 24 to 30: a "fast-forward" batch size patched after a randomized mismatch; `xxWynm2` steps 9 to 12: simulated random phases to look for a regime to exploit). Their shortcuts handle the simple two-payment ping-pong and 9 of the 12 stored many-pass batches, but not those 3 batches (3 to 4 participants, 4 to 6 priority-2 payments, largest amounts 8.4x10^8 to 9.7x10^8; other stored batches of similar size, such as `802`, were solved in time). I have not characterized more precisely which property of those batches defeats their shortcuts. All three then ended with a final claim that their engine "handles many-pass cases efficiently", on the basis of their own tests, which did not include a batch of this shape. In short: they understood the requirement and implemented a partial acceleration; they did not find a cycle-detecting acceleration that is correct for queue-order changes.
- On 1.3.1, which did not mention the long passes, all three DeepSeek trials passed.

### Codex (`gpt-6.1-sol`, xhigh)

- Codex passed every version it completed (1.0.0, 1.1.1, 1.3.1). Its solutions were large (2.8k to 5k lines) exact solvers (LP, SAT, cuts and factorization modules) that it tested against its own brute-force references; it matched all hidden batches, including the mined dense ones, and all three 1.3.1 engines also handled the huge-pass batches it had never been told about. The 1.4.0 Codex trials are PENDING.
- The apikeyclaw endpoint refuses Codex `/cheat` with the official prompt (see above).

### Which requirements are met

- Standard trials all reward 0 on the final version: NOT YET MET. DeepSeek: 3 of 3 valid failures. Codex: PENDING.
- `/cheat` reward 0: DeepSeek yes (every attempt); Codex could not be run (safety refusal at the endpoint).
- Oracle 1, nop 0, 27 of 27 static checks: met.
- `harbor check` rubric: not run (needs a model key); marked for Dan.

## Local log

Static checks: 27 of 27 `check-*.sh` scripts exit 0 on 1.4.0 (run 2026-10-10 from a fresh depth-1 clone of `harbor-framework/terminal-bench`, `dockerfile-pin` v1.5.0 on `PATH`). `tools/verify_pp.py` replayed all 12 `long-lots` batches pass by pass with no acceleration (42 to 380 s each) and the stored report matched on all 12.
