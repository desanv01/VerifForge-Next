# Isolated workbench browser preflight

This file-only helper prepares the documented [local React/Vite workbench](UI.md)
for a separately authorized browser observation. It does not launch or install
anything, make HTTP requests, inspect running processes, or authorize execution.
It addresses a specific setup ambiguity: `npm run dev` specifies loopback but
does not require the documented port to remain fixed. A launch must stop on a
port conflict rather than redirect an observer to a fallback or unrelated server.

Run the existing Python interpreter from the repository root:

```text
python -I -S -B scripts/browser_preflight.py C:/owned/staging/browser-config.json
```

The config is supplied by the operation owner, has exactly these fields, and
contains no credentials. Substitute actual reviewed paths, ports and tool
SHA-256s. The six source hashes below are exact public blob bytes at the reviewed
baseline; the tool hash placeholders still require operator input.

```json
{
  "baseline_commit": "46dbc3e7e5c5d4493a5a2e7909c47569bc3edfe0",
  "frontend_root": "C:/owned/staging/apps/web",
  "dependency_root": "C:/owned/staging/apps/web/node_modules",
  "node_exe": "C:/reviewed/runtime/node.exe",
  "node_sha256": "<reviewed Node executable SHA-256>",
  "vite_sha256": "<reviewed node_modules/vite/bin/vite.js SHA-256>",
  "source_sha256": {
    "package.json": "7d61d455b213419e4dfd85afab2cc89c3979e10c1a4943f218eef151fdb574e1",
    "package-lock.json": "23d1da57285f768ddca1f4ac4bfaba59147105621da4f18500793e8a29a524bd",
    "vite.config.ts": "d7c847ba6aa18f5c3b57bd3ab2a45d8442460c2a3459f52af50c359479e1294c",
    "index.html": "27b540862cffb83c3f52cd4eeca1f32e636f15651de4c2a9736c2ed768a7d58a",
    "src/App.tsx": "d81e4e9f3d34e0a09b9411948e81800a4f50eb5acb15bf43a915e63f5a50c2eb",
    "src/api.ts": "493bf59a0569eddc38b7fbecfc4bedf938c025e8731383b62d9c636f84138773"
  },
  "ui_port": 15142,
  "api_port": 18642
}
```

`baseline_commit` names the reviewed source baseline, not a Git HEAD check. The
owner must independently verify the actual tree, full app/dependency closure,
and any later revision before admission. The helper neither generates nor
updates expected hashes. Its six source pins are immediate bootstrap assumptions,
not a complete dependency or source attestation. Pin Node, Vite, all resolved
config imports and native bundler dependencies in the full owner closure.
Use the exact reviewed bytes when staging: checkout newline conversion changes
hashes. Resolve any mismatch against the approved Git blobs before admission;
do not automatically refresh the expected pins from a mismatching staging tree.

The frontend root must be a new isolated staging copy, with its matching existing
`node_modules` tree and no `.env*` entries. The helper checks names only and does
not read dotenv content. Do not copy credential files into staging. Node must
satisfy the engines of the reviewed locked Vite version: the reviewed baseline
locks Vite 7.3.7 with Node `^20.19.0 || >=22.12.0`. Executable versions and installed
dependency availability remain separate admission checks.
Use the reviewed `package.json` and `package-lock.json` together for a separately
authorized clean dependency installation. Existing unrelated `node_modules`
cannot qualify merely by copying the Vite entrypoint: the pinned config imports
`vitest/config` and `@vitejs/plugin-react`, and Vite needs its installed package
and native bundler closure. Never substitute globally installed Vite or `npx`.

Output is a `browser.launch-plan.v1` JSON record with
`execution_authorized: false`, the exact cwd, explicit Node/Vite argv, pinned
`--config`, loopback host, selected `--port` and `--strictPort`, selected UI URL
and same-origin `/api/health` probe URL. Its environment contains only selected
Windows system variables, `NO_COLOR`, and the exact loopback
`VERIFORGE_API_PROXY`; it does not inherit `NODE_OPTIONS`, `PATH` or provider keys.
The owner must supply its reviewed scratch/cache containment separately.
The record also preserves the verified Node executable and Vite entrypoint
SHA-256s, matching dependency root and source pins. These two tool hashes do
not attest the entire installed dependency tree or establish executable versions.
After separate admission, the process owner consumes `argv` as an argument list
with the recorded `cwd` and a replacement `environment`; merging inherited
environment variables or launching through a shell changes the reviewed plan.

The current app requests `/api/...` from its frontend origin. The existing
`vite.config.ts` proxies that prefix to `VERIFORGE_API_PROXY`, whose ordinary
development default is `http://127.0.0.1:18000`. For the example above, the
authorized isolated API must instead own `127.0.0.1:18642` before the frontend
owns `127.0.0.1:15142`. These are examples, not reserved ports. No current API,
database, readiness or listener is established by generating a launch plan.

Before any launch, main owns the fresh operation grant, exact source/runtime
identities, isolated API/data target, resource admission, vacant owned ports,
process containment and bounded startup/cleanup. The existing dependency
installation/build route in UI.md is a separate authorized operation; this
helper never runs it. Historical private browser grants or resource samples are
not reusable successor authority.

A later authorized Terra browser check must record its selected browser/tab and
exact planned URL, confirm the listeners belong to the new owned processes,
observe the root and same-origin `/api/health`, and retain bounded responses and
screenshots of the approved light/dark interface and actual errors. Health
capabilities, including fresh `investigation_api: "1"` for recorded investigations,
are protocol markers, not simulator/model or design acceptance. Scope native or
provider mutations separately. Preserve actual process exit, owned cleanup and
listener settlement; unresolved effects prohibit a replacement operation.

Focused offline check:

```text
python -I -S -B tests/test_browser_preflight.py -v
```

Its files/executables are fake and never launched. Passing this check establishes
only the file-only plan/refusal behavior, not browser or native qualification.

Official references: [Vite CLI](https://v7.vite.dev/guide/cli),
[Vite server proxy and strict port](https://v7.vite.dev/config/server-options),
and [Vite dotenv loading](https://v7.vite.dev/guide/env-and-mode).
