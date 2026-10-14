# Results

Every reward below was read from a Harbor `result.json` or `verifier/ctrf.json` on the Mac mini that ran the trials. Nothing is invented. The final version of the task is `1.5.0` (commit `5daa348`). **The take-home requirement that every standard trial scores reward 0 is NOT met on 1.5.0: Codex passed 1 of 3 on the first 1.5.0 job (`codex-run-v15`) and again 1 of 3 on the re-run (`codex-run-v15b`).** DeepSeek on 1.5.0 failed all three standard trials and scored 0 on `/cheat`. The history of earlier versions is kept because it explains why the task changed.

Harbor pin: `0.23.1.dev202609170426`, from `harbor-framework/terminal-bench` `.github/harbor-version` on main, fetched 2026-10-10. Static scripts are that repo's `scripts/checks/`.

## Static checks

Run against `tasks/clearing-offset` using `scripts/checks/check-*.sh` from a depth-1 clone of `harbor-framework/terminal-bench` main. On 1.4.0 (2026-10-10) all 27 scripts exited 0, with `dockerfile-pin` v1.5.0 on `PATH`. On 1.5.0 (2026-10-12) 26 scripts exited 0; `check-image-digests.sh` could not run because `dockerfile-pin` was not installed on that machine. 1.5.0 changed no Dockerfile (only verifier cases, `tests/`, tools and docs), so the 1.4.0 digest result still applies to the same Dockerfiles, but the script itself was not re-run on 1.5.0.

| Check | Result |
| --- | --- |
| Canary strings | PASS |
| No cheat directory | PASS |
| Dockerfile refs | PASS |
| Image digest pins | PASS on 1.4.0; not run on 1.5.0 (`dockerfile-pin` missing; Dockerfiles unchanged) |
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

## Oracle and nop (final version 1.5.0)

Harbor `0.23.1.dev202609170426`, run on the Mac mini from a clone at commit `5daa348`: `harbor run -p tasks/clearing-offset --agent oracle|nop --env docker --yes`.

| Trial | Job id | Reward | Result |
| --- | --- | --- | --- |
| oracle (`oracle-v9`) | `f4e93784-e80b-43db-ada9-6c7f77cd0fab`, trial `A8eUZuN` | 1 | 130 passed, 0 failed |
| nop (`nop-v9`) | `ab0cf136-8f65-4485-ba3f-1049eec5a9c7`, trial `vG9WnTr` | 0 | 11 passed, 119 failed |

Earlier versions were checked the same way (oracle reward 1, nop reward 0 every time): 1.4.0 oracle `420fe412-14d6-4534-9f6a-48f76d8c8bc0` (108 passed), nop `c967cdce-6b50-40fa-8ef7-8235d164ee88` (97 failed); 1.1.0 oracle `fe56594b-665c-4555-b9a6-8576873a3277`, nop `357b2f3e-bedb-48fc-9541-61d42108ed0e`; 1.1.1 oracle `64904282-0aa8-4fe6-8227-3170e3a11923`, nop `f30af9a3-53f7-45cc-83c4-76f548593057`; 1.2.0 oracle `458dc6b4-e041-4d7a-baa3-34320f9fa05b`, nop `d615c90c-ff09-4990-bcf7-d3913d90b5cd`; 1.2.1 oracle `cdc32a84-5112-4319-a48f-1e14d9db89b6`, nop `feedd350-c0d9-40fa-9ead-f99a4412b872`; 1.3.0 oracle `6a2872f4-869e-4d62-b7ed-1305161b14ef`, nop `687334d6-3ce5-4bf4-9396-59d86758fdfb`; 1.3.1 oracle `d3b9efa3-8cd8-4c2f-a782-1eddae93b0fc`, nop `eb2e3ef8-bdf2-4cab-8d63-7108dcbb7871`.

## Standard trials (`/run`) on the final version 1.5.0

Codex `openai/gpt-6.1-sol` `reasoning_effort=xhigh`, `-k 3 -n 3`, job `codex-run-v15` = `c00277a5-c894-42c6-9f60-cbde49e9e6e9`, commit `5daa348`, launched 2026-10-12 05:28 PT. Only a run that was graded on a normal agent finish (or agent timeout) counts as a model result; an infrastructure error does not.

| Trial | Reward | Notes |
| --- | --- | --- |
| `VbtqbPM` | **0** | Valid failure. No exception; agent ran 05:31 to 08:56 PT (about 3h25m). 1669-line pure-Python engine. 127 of 130 passed; the 3 failures are 5 s timeouts on `801-long-lots`, `909-multi-lots` and `920-multi-lots`. |
| `ZHMaEd6` | 0 (infrastructure, not counted) | The codex CLI exited with `turn.failed: Connection failed: error sending request` after about 4h30m (05:31 to 10:00 PT). The verifier still graded the code left in `/app/src` (2921 lines): 129 of 130 passed, the only failure a 5 s timeout on `909-multi-lots`. Because the agent was cut off by a network error, this is not a valid model failure. |
| `qkbfmaT` | **1** | No exception; agent ran the full ~8 h (05:31 to 13:31 PT). 4045-line pure-Python engine (8 files), 130 of 130 passed. |

DeepSeek terminus-2 `deepseek/deepseek-flash` `reasoning_effort=max`, `-k 3 -n 3`, job `deepseek-run-v15` = `b2586be3-12d8-4b59-869b-aa82fcd9d691`, commit `5daa348`, launched 2026-10-13 06:46 PT, finished 2026-10-13 11:02 PT. All three trials finished with no exception (valid model results). Mean reward 0.0.

| Trial | Reward | Notes |
| --- | --- | --- |
| `KvPoyhg` | **0** | Valid failure. No exception; agent ran about 2h21m (06:46 to 09:08 PT), 169 episodes, 655-line pure-Python engine. 127 of 130 passed; the 3 failures are 5 s timeouts on `7m_22_2-hard`, `900-multi-lots` and `915-multi-lots`. |
| `QMjs6Q5` | **0** | Valid failure. No exception; about 2h56m (06:46 to 09:43 PT), 227 episodes, 806-line pure-Python engine. 110 of 130 passed; 20 failures are 5 s timeouts on `801`/`803`/`809-long-lots` and 17 of the `900`-series `multi-lots` batches. |
| `YFQZrXZ` | **0** | Valid failure. No exception; about 4h15m (06:46 to 11:02 PT), 309 episodes, 1122-line pure-Python engine (5 files including `lp.py` / `bundle_lp.py`). 110 of 130 passed; same 20 timeout failures as `QMjs6Q5`. |


### Codex re-run requested by Xiangkai (`codex-run-v15b`)

Same model and settings: Codex `openai/gpt-6.1-sol` `reasoning_effort=xhigh`, `-k 3 -n 3`, Harbor job `codex-run-v15b` = `7764ed94-053f-4e72-89b6-2a5c7b7163d5`, task still at commit `5daa348` / version 1.5.0 (RESULTS baseline was `0e3b88f` before this update). Launched 2026-10-13 about 8:07 PM PT, finished 2026-10-14 about 4:10 AM PT (total runtime 8h 2m 57s). Mean reward 0.333; Pass@2 0.667. One `AgentTimeoutError` (counted separately below). **Requirement still NOT met.**

| Trial | Reward | Notes |
| --- | --- | --- |
| `VVA9VE9` | **0** | Valid failure. No exception; agent ran about 8h (8:09 PM PT Oct 13 to 4:09 AM PT Oct 14). 127 of 130 passed; the 3 failures are 5 s timeouts (`AssertionError: timed out` / `TimeoutExpired` after 5 seconds) on `909-multi-lots`, `917-multi-lots` and `920-multi-lots`. |
| `9e476uJ` | **0** | Valid failure. No exception; agent ran about 1h51m (8:09 PM to 10:00 PM PT Oct 13). 129 of 130 passed; the only failure is a 5 s timeout on `909-multi-lots`. |
| `Q2FcQtA` | **1** | `AgentTimeoutError` after 28800 s (8h agent timeout), but Harbor still ran the verifier on the submitted code: 130 of 130 passed, reward 1. Same timeout-then-pass pattern as earlier Codex trials. Infrastructure/timeout exception counted separately from the two valid reward-0 failures. |

Infrastructure / non-model errors in this job: 1 (`AgentTimeoutError` on `Q2FcQtA`). The timeout trial still received a graded reward 1 from the verifier.


### Previous version 1.4.0 (commit `9bbd8e8`)

| Trial | Model | Job id / trial | Reward | Notes |
| --- | --- | --- | --- | --- |
| `/run` 1 | terminus-2 `deepseek/deepseek-flash` `reasoning_effort=max` | `c82cd146-67cd-44c7-a1a5-3574b97e1ec5` / `W2hnKub` | **0** | Finished, no exception, 153 steps, about 1h19m. 105 of 108 passed; timeouts at 5 s on `801`, `803`, `809-long-lots`. Valid failure. |
| `/run` 2 | same | same job / `5k5MmBz` | **0** | 151 steps, about 1h56m. Same 3 timeouts. Valid failure. |
| `/run` 3 | same | same job / `xxWynm2` | **0** | 280 steps, about 2h34m. Same 3 timeouts. Valid failure. |
| `/run` 1-3 | codex `openai/gpt-6.1-sol` xhigh | `a9b4d8a4-5824-49fe-8248-6321dd6b1d5c` (`codex-run-h2`) / `KrT9G3D`, `QAo3ozk`, `SFv5mdt` | 1, 1, 1 | 108 of 108 each. `KrT9G3D` and `SFv5mdt` hit the 8 h agent timeout but their submitted code was graded and passed. An earlier Codex job on 1.4.0, `20623c7a-5f62-49e4-b03d-81ed9fcad06f`, was stopped with 0 trials finished and is not counted. |

## Adversarial trials (`/cheat`)

On 1.5.0, DeepSeek `/cheat` was run once. Codex `/cheat` was not re-attempted (every earlier attempt hit the same endpoint safety refusal).

The prompt is the official `docs/prompts/hack-trial-prompt.md` from `harbor-framework/terminal-bench` main, fetched verbatim (2755 bytes, identical to the copy used in all earlier cheat attempts) and passed with `--extra-instruction-path`, one attempt (`-k 1`).

| Trial | Model | Job id / trial | Reward | Notes |
| --- | --- | --- | --- | --- |
| `/cheat` 1.5.0 | terminus-2 `deepseek/deepseek-flash` | `bf0e5475-66f0-4fa3-a89c-1da8b504c231` (`deepseek-cheat-v15`) / `iPbUpet` | **0** | Finished, no exception; about 23m (06:46 to 07:10 PT), 25 episodes. 14 of 130 passed, 116 failed. Submitted a lookup-style `known_answers.py` plus `sitecustomize.py`; did not produce correct reports for the hidden batches. |
| `/cheat` 1.4.0 | terminus-2 `deepseek/deepseek-flash` | `ded92a35-6f74-4e06-866e-b3027e4b87d0` / `nL9HeyF` | 0 | Finished, no exception. |
| `/cheat` | codex `openai/gpt-6.1-sol` | `d5f7379b-ec09-43e4-8b1b-5b0b35009ce6` / `LZRLrgd` | no result | Could not be run through the apikeyclaw endpoint: safety refusal. The endpoint returned `This content was flagged for possible cybersecurity risk ... apply for Daybreak access` and Harbor recorded `AgentSafetyRefusalError` before the agent took any action. Harbor stores reward 0.0 for the trial, but no agent ran, so this is not evidence that the task resists cheating. |

The same refusal happened on every earlier Codex `/cheat` attempt with the same official prompt: jobs `2aaa986d-d493-4296-a73a-6a24aeed21d8` (trial `LjZVEMp`) and `4d803bab-b8ff-4e3c-83d3-ca2ee73ba460` (trial `3QTrMiD`) on 1.1.1, and `89279a0b-c1ad-4bfc-83d2-f46ec9986ee8` (trial `A6RiZLe`) on 1.3.1. I did not rephrase the prompt to get around the safeguard.

DeepSeek `/cheat` on earlier versions also ended at reward 0: 1.1.1 job `4e87f73b-c1e4-4c06-9d39-78224f1c95ca` (`pk6yzS6`, 11 of 39 passed), 1.2.0 job `9a41ffd5-24db-4fed-b6c6-7b8660790da6` (`YwsbZZr`), 1.3.1 job `4ee9410e-f33d-4f00-8983-8994d08d7f0b` (`XH75WjU`, 19 of 96 passed). In the 1.3.1 trial the agent built a lookup table of hashes of the public fixtures and sidecar `*.expected.json` files and also sketched scraping the parent test process; none of that produces reports for the hidden batches, so the verifier gave 0. The 1.4.0 DeepSeek cheat trajectory was not analysed in detail; only its reward (0) is reported.

## Iteration history with every trial

The take-home requires every standard trial to get reward 0. That is not met by any version, including the final 1.5.0; the table is the honest record.

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
| 1.4.0 | `c82cd146-67cd-44c7-a1a5-3574b97e1ec5` | deepseek | `W2hnKub`, `5k5MmBz`, `xxWynm2` | 0, 0, 0 | valid failures, 105 of 108 each |
| 1.4.0 | `20623c7a-5f62-49e4-b03d-81ed9fcad06f` | codex | none | stopped, 0 finished | restarted as the next job |
| 1.4.0 | `a9b4d8a4-5824-49fe-8248-6321dd6b1d5c` | codex | `KrT9G3D`, `QAo3ozk`, `SFv5mdt` | 1, 1, 1 | 108 of 108 each |
| 1.5.0 | `c00277a5-c894-42c6-9f60-cbde49e9e6e9` | codex | `VbtqbPM`, `ZHMaEd6`, `qkbfmaT` | 0, 0 (infra), 1 | final version; see above |
| 1.5.0 | `b2586be3-12d8-4b59-869b-aa82fcd9d691` (`deepseek-run-v15`) | deepseek | `KvPoyhg`, `QMjs6Q5`, `YFQZrXZ` | 0, 0, 0 | valid failures; 127/130, 110/130, 110/130 |
| 1.5.0 | `bf0e5475-66f0-4fa3-a89c-1da8b504c231` (`deepseek-cheat-v15`) | deepseek `/cheat` | `iPbUpet` | 0 | 14 of 130; lookup/sidecar attempt |

The 1.4.0 hardening came from checking the three Codex 1.3.1 engines on 12 random huge-pass batches: all three solved them in under 0.2 s and matched the oracle, without being told. DeepSeek's three 1.3.1 engines timed out on 2 of 12. I therefore expected 1.4.0 to affect DeepSeek far more than Codex.

## Failure analysis

### DeepSeek (terminus-2, `deepseek-flash`)

- 1.5.0, all three standard trials (`KvPoyhg`, `QMjs6Q5`, `YFQZrXZ`) are valid failures with reward 0. Each finished normally with no exception. `KvPoyhg` got closest (127 of 130): timeouts only on `7m_22_2-hard`, `900-multi-lots` and `915-multi-lots`. The other two each passed 110 of 130 and timed out on the same set of 20 many-pass batches (`801`/`803`/`809-long-lots` plus 17 of the `900`-series `multi-lots`). Engines were 655–1122 lines of pure Python. So on the final version DeepSeek still fails all standard trials, as it did on 1.4.0, but against the larger 130-test suite.
- 1.5.0 `/cheat` (`iPbUpet`) also reward 0 (14 of 130). The trajectory left a `known_answers.py` lookup and `sitecustomize.py`; that does not cover the hidden batches.
- 1.4.0, all three trials (`W2hnKub`, `5k5MmBz`, `xxWynm2`) are valid failures with reward 0. Each run finished normally, with no exception. Each submitted a pure-Python engine of 671, 534 and 473 lines that was correct on 105 of 108 tests, including all hand batches, mutant-killer batches, aging and strain batches, and mined dense batches. The same three tests timed out at 5 s in all three trials: `801-long-lots`, `803-long-lots` and `809-long-lots`. These are priority-2 phases that make hundreds of millions of passes. I re-ran the three submitted engines on those batches offline and they still had not finished after 120 s, so this is a speed failure and not a wrong answer. The failures are not infrastructure errors.
- What the trajectories show: all three agents read the rulebook's statement that a phase can take tens of millions of passes, tried the worked many-pass example, and wrote an accelerated priority-2 phase (`W2hnKub` step 9: an "event-batched priority-2 unilateral phase"; `5k5MmBz` steps 24 to 30: a "fast-forward" batch size patched after a randomized mismatch; `xxWynm2` steps 9 to 12: simulated random phases to look for a regime to exploit). Their shortcuts handle the simple two-payment ping-pong and 9 of the 12 stored many-pass batches, but not those 3 batches (3 to 4 participants, 4 to 6 priority-2 payments, largest amounts 8.4x10^8 to 9.7x10^8; other stored batches of similar size, such as `802`, were solved in time). I have not characterized more precisely which property of those batches defeats their shortcuts. All three then ended with a final claim that their engine "handles many-pass cases efficiently", on the basis of their own tests, which did not include a batch of this shape. In short: they understood the requirement and implemented a partial acceleration; they did not find a cycle-detecting acceleration that is correct for queue-order changes.
- On 1.3.1, which did not mention the long passes, all three DeepSeek trials passed.

### Codex (`gpt-6.1-sol`, xhigh)

- Codex passed every version it completed (1.0.0, 1.1.1, 1.3.1). Its solutions were large (2.8k to 5k lines) exact solvers (LP, SAT, cuts and factorization modules) that it tested against its own brute-force references; it matched all hidden batches, including the mined dense ones, and all three 1.3.1 engines also handled the huge-pass batches it had never been told about. On 1.4.0 all three Codex trials passed (108 of 108) with 3.2k to 4.6k-line engines that detect and skip repeating pass groups with certified guards.
- 1.5.0: `VbtqbPM` (valid failure) wrote a 1669-line engine and stopped after about 3h25m; its pass-skipping did not cover 3 batches (`801-long-lots`, `909-multi-lots`, `920-multi-lots`), which timed out at 5 s. Every other test, including all correctness cases, passed. `ZHMaEd6` was cut off by a network error (not counted); the code it had at that point already passed 129 of 130, missing only `909-multi-lots`. `qkbfmaT` used the full 8 h and passed all 130. Its final message said the task was still incomplete because its own stress batches took over 5 s (one 13.9 CPU s), yet none of the hidden batches hit that weakness. So the 22 mined cases separate Codex engines only when an engine's acceleration has a gap on that specific shape; a run that keeps hardening its acceleration for 8 hours can close all gaps in the stored set. Mining cases against previous-run engines is an arms race against the specific engines mined, not a guarantee against new runs.
- The apikeyclaw endpoint refuses Codex `/cheat` with the official prompt (see above).

### Which requirements are met

- Standard trials all reward 0 on the final version: **NOT MET.** Codex on 1.5.0 first job (`codex-run-v15`): one valid failure, one infrastructure error, one pass (`qkbfmaT`, reward 1). Codex re-run (`codex-run-v15b`): two valid failures (`VVA9VE9`, `9e476uJ`) and one pass (`Q2FcQtA`, reward 1) with `AgentTimeoutError` on that pass. DeepSeek on 1.5.0: 3 of 3 valid failures (reward 0).
- `/cheat` reward 0: DeepSeek yes on 1.5.0 (`iPbUpet`) and every earlier attempt; Codex could not be run (safety refusal at the endpoint).
- Oracle 1, nop 0 on 1.5.0: met. Static checks: 26 of 27 run and pass on 1.5.0; the image-digest check was not re-run (tool missing), it passed on 1.4.0 with identical Dockerfiles.
- `harbor check` rubric: not run (needs a model key); marked for Dan.

## What would be needed next

Not done, by decision: the task is submitted as is. To make Codex fail reliably, the difficulty would have to come from something an 8-hour exact-solver effort cannot close by testing, rather than from more mined cases against past engines. Options: (1) generate the many-pass verifier batches at grading time from a seeded family broad enough that pass skipping must be fully general (for example cycle detection on the complete queue state), with the oracle computing expected reports on the fly; (2) a tighter per-batch time limit combined with that family; (3) rule subtleties that are under-specified by the examples but fully determined by the text. Each needs new Codex trials (about 8 h each). DeepSeek was re-run on 1.5.0 and still failed all three standard trials plus `/cheat`.

## Local log

Static checks: 27 of 27 `check-*.sh` scripts exit 0 on 1.4.0 (run 2026-10-10 from a fresh depth-1 clone of `harbor-framework/terminal-bench`, `dockerfile-pin` v1.5.0 on `PATH`). `tools/verify_pp.py` replayed all 12 `long-lots` batches pass by pass with no acceleration (42 to 380 s each) and the stored report matched on all 12.
