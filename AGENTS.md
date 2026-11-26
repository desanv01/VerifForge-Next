# VerifForge Next implementation

VerifForge Next continues the work published in VerifForge at `5453a5759af8d3529f2226ca9880f46eac618c18`. Use this repository and its new assignments for implementation and integration. The [upgrade roadmap](docs/project/UPGRADE_ROADMAP.md) tracks current work. Read the relevant project documentation and assigned scope before editing.

Use persistent implementation workers within their assigned scopes and focused GPT-6.2 Sol High review or tests where needed. Computer use belongs to a GPT-6.1 Terra High subagent when available. The main coordinator owns integration, operational acceptance and GitHub. Current successor controls govern runtime and request admission.

## Coordination
- Main owns integration, root configuration, shared dependency locks, project controls and progress tracking unless explicitly delegated.
- Workers edit only assigned paths. Do not switch branches, commit other workers' files, create workers, deploy, publish, or create schedules.
- Report changed paths, focused validation, remaining gates and any operation settlement through the assigned team channel and work receipt.
- Read the current successor assignment and applicable pause controls before starting a new operation. Stop at your task boundary; do not start another phase without assignment.
- Shared checkout: do not overwrite others' edits. Request shared-interface changes from main.
- Record actual commands, outcomes, limitations, and changed paths. Never mark mock execution as real simulator/model/Vivado evidence.

## Product constraints
- One engineering investigation engine. The primary roadmap covers sequences 1–6: RTL, real RISC-V, firmware/MMIO, live Vivado, KiCad and independent cross-domain checks. Sequence 7 is stretch scope. Sequence 8 covers later software adapters.
- Model proposes typed experiments; independent immutable checker determines verdict. Execution status and design verdict are separate.
- Preserve exact stimulus, source/checker/contract identity, tool versions, evidence, and failure signature.
- A timeout is not automatically a design defect. A successful build is not functional correctness.
- Existing RTL targets: FIFO, arithmetic pipeline, bounded AXI-Lite. Expanded adapters need explicit supported configurations and independent acceptance. Track Import / Execute / Repair separately.
- Curated trusted fixtures first; no arbitrary shell commands or uploaded Python execution. Credentials stay out of simulator jobs and reports.
- Initial implementation is local. Public deployment/release needs separate authorization.
- Use official current documentation for evolving dependencies. Read required relevant skills, especially 12ui before substantial UI creation.

## Layout and ownership baseline
Python src layout: src/veriforge/{contracts,core,rtl,api,planner,evidence,vivado}; React in apps/web; HDL in targets/{fifo,arithmetic,axi_lite}; tests mirror component names. Dependency changes require explicit ownership.
