# Wearable agent operating protocol

Repository-wide workflow contract for Codex/OpenAI agents and Claude Code. The primary agent is the
**Manager**. Every delegated agent is a **Worker**. The Manager always owns integration, acceptance,
authoritative status updates, and the final answer to the user.

These are behavioral instructions, not filesystem guarantees. Enforce them with narrow tool access,
exclusive file ownership, diff review, and verification.

---

## 1. Context discipline — read this first

This project has repeatedly burned entire usage windows on agents re-reading and re-verifying work
that was already done. That is the failure mode this section exists to prevent.

**Read in this order, and stop as soon as you can act:**

1. `CLAUDE.md` (auto-loaded, deliberately small) and this file.
2. The verified log and current-work section of `pcb/README.md`.
3. Only the specific authority the task actually needs, per the authority map in `CLAUDE.md`.

**Do not:**

- Re-read `pcb/README.md` end to end when the verified log and next-actions answer the question.
- Re-check part stock, pricing, or availability that the log already records, unless the task is
  sourcing or the user asks.
- Re-read datasheets for parts whose pinouts the log records as verified.
- Re-run a check the log records as passing against the **current** file hash (see section 2).
- Survey the repo "for context" before starting. Read what the task needs, when it needs it.

Prefer `grep`/`sed -n` over reading whole files. A 460-line document read in full to answer one
question is a defect, not diligence.

If a question is genuinely settled but the record is thin, say so and ask — do not re-derive it.

---

## 2. The verified log and hash gating

`pcb/README.md` carries an **append-only verified log**. Every accepted check is one row:

```
| date | artifact hash (first 12) | check | result |
```

**The rule: if the current hash of an artifact matches the hash logged beside a check, that check's
logged result stands. Re-running it is a protocol violation, not diligence.** Report the logged
result and move on.

A hash change invalidates every logged check for that artifact. Those checks become open again and
must be rerun before their results may be cited.

Current hashes:

```bash
shasum -a 256 pcb/wearable_v2.kicad_sch pcb/wearable_v2.kicad_pcb
```

Exceptions, where a rerun is correct even on a matching hash:

- The user explicitly asks for a rerun.
- You are about to change the artifact and want a pre-change baseline.
- The logged result is ambiguous, or you have concrete evidence it is wrong. State the evidence.

---

## 3. Update the log as you work, not at the end

The Manager appends to the verified log **immediately after each accepted check or milestone**, not
in a wrap-up at the end of the session. An agent that is cut off mid-task must leave the log already
current.

Also keep the **Next actions** list in `pcb/README.md` ordered and truthful: strike what is done,
add what the work revealed. Record only durable facts — verification results, decisions, remaining
risks, next work. Never agent transcripts, ownership tables, or process narration.

Do not create dated handoff files. There is one living status document; a second one becomes a
second source of truth that the next agent has to reconcile.

A milestone is complete only when its deliverable exists, required verification passed, and the
Manager accepted the evidence. Attempts and Worker self-reports are not milestones.

---

## 4. Authority

- This file owns agent workflow and delegation policy.
- `CLAUDE.md` owns the authority map, hard rules, and locked constraints.
- `pcb/README.md` owns current PCB/schematic state, the verified log, constraints and next work.
- `parts/V2_BOM.md` owns part rationale and release/approval status.
- `pcb/bom_from_schematic.csv` owns reference designators and quantities.
- The KiCad schematic is frozen for layout. Raise a suspected circuit change; never implement one
  silently.
- Worker completion, clean checks, or completed layout never mean fabrication or ordering is
  approved. Release gates are separate.

---

## 5. When to delegate, and when not to

The orchestrator/Worker architecture stays available and should be used whenever it genuinely pays.
It is not the default for every task.

**Work locally when** the task is a short sequence of edits or checks, the steps depend on each
other, or the whole job is smaller than the cost of writing a contract and reviewing a report. Most
single-step layout, DRC and documentation work is local.

**Delegate when at least one is true:**

- Two or more genuinely independent tasks can run at once on disjoint files.
- The task needs a large read — datasheet sweeps, full-netlist audits, multi-part sourcing — whose
  bulk should stay out of the Manager's context. The Worker returns the conclusion, not the corpus.
- An independent check is wanted precisely because it does *not* share the Manager's assumptions.
- The work is exploratory and may be discarded.

**Do not delegate** to re-verify something the verified log already covers at the current hash, to
manufacture parallelism where none exists, or to avoid reading something small yourself.

Prefer read-only Workers. Grant write access only for an exact, exclusive file list.

### Manager loop

1. Establish the baseline: `pcb/README.md` verified log + next actions, `git status --short`,
   current artifact hashes, and any unresolved user decisions. Preserve unrelated changes.
2. Decide local vs delegated per the test above.
3. Spawn a fresh Worker per task. Codex: `fork_turns="none"`. Claude: a project subagent with a
   separate context. Pass only the task contract and the evidence it needs — never the transcript.
4. Keep an ownership table in working memory. One active writer per file. The Manager does not edit
   a Worker-owned file while that Worker is active.
5. Inspect returned evidence. Reproduce a claim only if it is high-risk, decision-bearing, and not
   already covered by the log. Reject unsupported conclusions or send a bounded correction.
6. Integrate, append to the verified log, and communicate the result.

Workers must not spawn Workers unless their contract explicitly allows it.

---

## 6. Required Worker task contract

Every delegation must name all six fields:

```text
Objective:
Authoritative documents:
Files it may edit:
Files it must not edit:
Required verification:
Concise return format:
```

Use exact paths or narrow globs. State `none (read-only)` when no edits are permitted. Include
unresolved user decisions and stop conditions. Name the checks the Worker must **not** rerun
because the verified log already covers them at the current hash.

A Worker stops and reports a blocker rather than broadening scope, deciding an unresolved option,
or editing a forbidden file.

---

## 7. Evidence required for acceptance

- repository claims: exact `file:line` or symbol references;
- external/API claims: authoritative link and access date where drift matters;
- changes: exact changed-file list and concise diff summary;
- verification: command, working directory, exit code, result counts, output paths;
- visual/hardware claims: screenshot or artifact reference plus explicit observations;
- incomplete checks: listed as not run — never implied to have passed.

Distinguish observed facts, inferences, recommendations, and unresolved risks. For hardware,
preserve the difference between feasibility, first-spin confidence, fabrication approval, and
guaranteed performance.

---

## 8. Write ownership and safety

- One active writer per file; parallel writers need disjoint lists.
- Workers never edit `AGENTS.md`, `CLAUDE.md`, or `pcb/README.md` unless their contract grants
  exclusive ownership of that exact file. **Workers never update project status.**
- Before accepting a write task, compare changed files against the assigned list and inspect the
  diff. Unexpected paths invalidate acceptance until explained.
- Never patch `pcb/wearable_v2.kicad_pcb` while PCB Editor is open.
- Never edit `pcb/wearable_v2.kicad_sch` during layout work.
- Do not rerun KiCad F8 unless the schematic genuinely changed; if it does, parity DRC must return
  to zero before layout continues.
- Do not silently decide anything listed as an open question in `CLAUDE.md` or `pcb/README.md`.

---

## 9. Platform worker definitions

- Claude project agents: `.claude/agents/` — `evidence-worker` (read-only) and `bounded-worker`
  (exclusive listed edits). `CLAUDE.md` imports this file, so the primary session is the Manager.
- Codex project agents: `.codex/agents/`; `.codex/config.toml` caps concurrent Workers.
