"""Offline browser-launch plan. Never starts a process or contacts a service.

Main must authorize execution separately and preserve ownership/resource guards.
Source pins are supplied by the integrator, never refreshed by this helper.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path

BASELINE = '46dbc3e7e5c5d4493a5a2e7909c47569bc3edfe0'
SOURCE_FILES = ('package.json', 'package-lock.json', 'vite.config.ts', 'index.html',
                'src/App.tsx', 'src/api.ts')


def require(condition, code):
    if not condition:
        raise ValueError(code)


def plain(path, directory=False):
    path = Path(path)
    require(path.is_absolute(), 'absolute_path_required')
    for part in (path, *path.parents):
        info = part.lstat()
        require(not part.is_symlink() and not getattr(info, 'st_file_attributes', 0) & 0x400,
                'linked_path_refused')
    require(path.is_dir() if directory else path.is_file(), 'path_kind')
    if not directory:
        require(path.stat().st_nlink == 1, 'hardlink_refused')
    return path


def pinned(path, expected, limit):
    require(isinstance(expected, str) and len(expected) == 64 and
            all(c in '0123456789abcdef' for c in expected), 'sha256_required')
    path = plain(path)
    require(path.stat().st_size <= limit, 'file_bound')
    raw = path.read_bytes()
    require(len(raw) <= limit and hashlib.sha256(raw).hexdigest() == expected, 'pin_changed')
    return raw


def launch_plan(config, environ=None):
    fields = {'baseline_commit', 'frontend_root', 'dependency_root', 'node_exe',
              'node_sha256', 'vite_sha256', 'source_sha256', 'ui_port', 'api_port'}
    require(type(config) is dict and set(config) == fields, 'config_shape')
    require(config['baseline_commit'] == BASELINE, 'baseline_changed')
    root = plain(config['frontend_root'], directory=True)
    deps = plain(config['dependency_root'], directory=True)
    require(deps == root/'node_modules', 'dependencies_must_match_frontend_root')
    require(type(config['source_sha256']) is dict and
            set(config['source_sha256']) == set(SOURCE_FILES), 'source_pin_set')
    # Vite auto-loads dotenv files. Require a clean, isolated frontend staging
    # root instead of reading or copying any credential-bearing file.
    require(not any(root.glob('.env*')), 'dotenv_present_stage_clean_root')
    package_raw = None
    for name in SOURCE_FILES:
        raw = pinned(root/name, config['source_sha256'][name], 4*1024*1024)
        if name == 'package.json':
            package_raw = raw
    package = json.loads(package_raw)
    require(type(package) is dict and package.get('name') == '@veriforge/web' and
            type(package.get('scripts')) is dict and
            package['scripts'].get('dev') == 'vite --host 127.0.0.1', 'unsupported_frontend')
    node = plain(config['node_exe'])
    vite = deps/'vite/bin/vite.js'
    pinned(node, config['node_sha256'], 256*1024*1024)
    pinned(vite, config['vite_sha256'], 1024*1024)
    for port in (config['ui_port'], config['api_port']):
        require(type(port) is int and 1024 <= port <= 65535, 'port_invalid')
    require(config['ui_port'] != config['api_port'], 'port_collision')
    environ = os.environ if environ is None else environ
    env = {k: environ[k] for k in ('SystemRoot', 'WINDIR', 'COMSPEC', 'PATHEXT', 'SYSTEMDRIVE') if k in environ}
    env.update(VERIFORGE_API_PROXY=f"http://127.0.0.1:{config['api_port']}", NO_COLOR='1')
    return {'schema': 'browser.launch-plan.v1', 'execution_authorized': False,
            'baseline_commit_assertion': BASELINE, 'source_sha256': dict(config['source_sha256']),
            'dependency_root': str(deps),
            'tool_sha256': {'node_exe': config['node_sha256'], 'vite_entrypoint': config['vite_sha256']},
            'cwd': str(root), 'argv': [str(node), str(vite), '--config', str(root/'vite.config.ts'), '--host', '127.0.0.1',
                '--port', str(config['ui_port']), '--strictPort'],
            'environment': env, 'url': f"http://127.0.0.1:{config['ui_port']}",
            'api_probe_url': f"http://127.0.0.1:{config['ui_port']}/api/health",
            'required_before_execution': ['main_owned_fresh_grant', 'full_source_dependency_closure',
                'owned_process_containment', 'resource_admission', 'empty_owned_ports',
                'explicit_node_browser_identity', 'isolated_backend_and_data', 'preserved_cleanup_receipt']}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('config', type=Path)
    args = parser.parse_args()
    try:
        require(args.config.stat().st_size <= 16384, 'config_bound')
        print(json.dumps(launch_plan(json.loads(args.config.read_bytes())), indent=2))
    except (ValueError, OSError, KeyError, TypeError):
        print(json.dumps({'status': 'preflight_refused', 'execution_authorized': False}))
        raise SystemExit(1)
