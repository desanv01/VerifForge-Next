"""One offline fake-filesystem contract check; never invokes Node or a browser."""
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

MODULE = Path(__file__).resolve().parents[1]/'scripts/browser_preflight.py'
spec = importlib.util.spec_from_file_location('browser_preflight', MODULE)
preflight = importlib.util.module_from_spec(spec)
spec.loader.exec_module(preflight)


class OfflineLaunchContract(unittest.TestCase):
    def test_strict_identity_ports_and_clean_environment(self):
        with tempfile.TemporaryDirectory(prefix='fake-', dir=MODULE.parents[2]) as temp:
            root = Path(temp)/'web'; root.mkdir()
            deps = root/'node_modules'; (deps/'vite/bin').mkdir(parents=True)
            node = Path(temp)/'node.exe'; node.write_bytes(b'FAKE never executable')
            vite = deps/'vite/bin/vite.js'; vite.write_bytes(b'FAKE never evaluated')
            pins = {}
            for name in preflight.SOURCE_FILES:
                path=root/name; path.parent.mkdir(parents=True, exist_ok=True)
                raw = json.dumps({'name':'@veriforge/web','scripts':{'dev':'vite --host 127.0.0.1'}}).encode() if name=='package.json' else b'fake source'
                path.write_bytes(raw); pins[name]=hashlib.sha256(raw).hexdigest()
            config = dict(baseline_commit=preflight.BASELINE,frontend_root=str(root),dependency_root=str(deps),
                          node_exe=str(node),node_sha256=hashlib.sha256(node.read_bytes()).hexdigest(),
                          vite_sha256=hashlib.sha256(vite.read_bytes()).hexdigest(),source_sha256=pins,
                          ui_port=15142,api_port=18642)
            plan=preflight.launch_plan(config, {'NODE_OPTIONS':'--inspect','MODEL_API_KEY':'FAKE','PATH':'FAKE'})
            self.assertFalse(plan['execution_authorized'])
            self.assertEqual(plan['argv'], [str(node), str(vite), '--config', str(root/'vite.config.ts'),
                                           '--host', '127.0.0.1', '--port', '15142', '--strictPort'])
            self.assertEqual(plan['dependency_root'], str(deps))
            self.assertEqual(plan['tool_sha256'], {'node_exe': config['node_sha256'],
                                                   'vite_entrypoint': config['vite_sha256']})
            self.assertEqual(plan['source_sha256'], pins)
            self.assertIsNot(plan['source_sha256'], pins)
            self.assertEqual(plan['environment'], {'VERIFORGE_API_PROXY':'http://127.0.0.1:18642','NO_COLOR':'1'})
            self.assertEqual(plan['api_probe_url'], 'http://127.0.0.1:15142/api/health')
            for changed in ({**config,'api_port':15142},{**config,'ui_port':True},
                            {**config,'baseline_commit':'0'*40},{**config,'node_sha256':'0'*64},
                            {**config,'vite_sha256':'0'*64},
                            {**config,'source_sha256':{**pins,'package.json':'0'*64}}):
                with self.assertRaises(ValueError): preflight.launch_plan(changed,{})
            (root/'.env.local').write_bytes(b'FAKE not read')
            with self.assertRaisesRegex(ValueError,'dotenv_present'): preflight.launch_plan(config,{})
            (root/'.env.local').unlink()
            for package in ([], {'name':'@veriforge/web','scripts':[]}):
                raw=json.dumps(package).encode()
                (root/'package.json').write_bytes(raw)
                malformed={**config,'source_sha256':{**pins,'package.json':hashlib.sha256(raw).hexdigest()}}
                with self.assertRaisesRegex(ValueError,'unsupported_frontend'):
                    preflight.launch_plan(malformed,{})


if __name__ == '__main__': unittest.main()
