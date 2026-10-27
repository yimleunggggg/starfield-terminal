"""Integration tests run with temporary HOME; never modify real shell profiles."""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class InstallTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='starfield-test-')
        self.addCleanup(self.temp.cleanup)
        self.home = Path(self.temp.name)
        self.env = os.environ.copy()
        self.env['HOME'] = str(self.home)
        self.env['SHELL'] = '/bin/zsh'
        self.env['PYTHONIOENCODING'] = 'utf-8'

    def run_cmd(self, cmd, expected=0, extra_env=None):
        env = dict(self.env)
        if extra_env: env.update(extra_env)
        p = subprocess.run(cmd, cwd=ROOT, env=env, text=True,
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE, input='')
        self.assertEqual(p.returncode, expected, p.stdout + '\n' + p.stderr)
        return p

    def test_default_install_and_reinstall_one_hook(self):
        self.run_cmd(['bash', 'scripts/install.sh'])
        self.run_cmd(['bash', 'scripts/install.sh'])
        s = (self.home/'.zshrc').read_text()
        self.assertEqual(s.count('# >>> STARFIELD TERMINAL >>>'), 1)
        self.assertEqual(s.count('starfield-terminal/welcome.py'), 1)
        self.assertFalse((self.home/'.claude/settings.json').exists())
        self.assertEqual(len(list((self.home/'.config/starfield-terminal/constellations').glob('*.png'))), 6)
        self.assertEqual(len(list((self.home/'.config/starfield-terminal/titles').glob('*.png'))), 12)
        p=self.run_cmd([sys.executable, str(self.home/'.config/starfield-terminal/welcome.py'), '--no-image', '--seed', '7'])
        self.assertIn('STARFIELD / TERMINAL',p.stdout)
        self.assertNotIn('\x1b_G',p.stdout)
        self.assertGreater(len(p.stdout.strip()),30)
        backups=list((self.home/'.config/starfield-terminal/backups').iterdir())
        self.assertEqual(len(backups),2)

    def test_statusline_opt_in_and_uninstall_restore(self):
        settings=self.home/'.claude/settings.json'
        settings.parent.mkdir()
        original={'model':'some-model','theme':'dark','statusLine':{'type':'command','command':'printf original'}}
        settings.write_text(json.dumps(original))
        self.run_cmd(['bash','scripts/install.sh','--with-claude'])
        self.run_cmd(['bash','scripts/install.sh','--with-claude'])
        applied=json.loads(settings.read_text())
        self.assertEqual(applied['model'],'some-model')
        self.assertIn('starfield-terminal/statusline.py',applied['statusLine']['command'])
        payload={'session_id':'abc','workspace':{'current_dir':str(self.home)},
                 'model':{'id':'ccs-openrouter','display_name':'poolside/laguna-s-2.1:free（OpenRouter）'},
                 'context_window':{'used_percentage':18}}
        proc=self.run_cmd([sys.executable,str(self.home/'.config/starfield-terminal/statusline.py')],expected=0)
        # An empty stdin must fail safe as well, still two lines.
        self.assertEqual(len(proc.stdout.strip().splitlines()),2)
        status=subprocess.run([sys.executable,str(self.home/'.config/starfield-terminal/statusline.py')],
                 input=json.dumps(payload),text=True,env=self.env,capture_output=True,check=True)
        self.assertIn('~18%',status.stdout)
        self.run_cmd(['bash','scripts/uninstall.sh'])
        restored=json.loads(settings.read_text())
        self.assertEqual(restored,original)
        self.assertNotIn('# >>> STARFIELD', (self.home/'.zshrc').read_text())

    def test_statusline_label_comes_from_config(self):
        self.run_cmd(['bash','scripts/install.sh','--with-claude'])
        cfg=self.home/'.config/starfield-terminal/config.json'
        cfg.write_text(json.dumps({'label':'X / Y','status_label':'MY / LAB'}))
        payload={'session_id':'abc','workspace':{'current_dir':str(self.home)},
                 'model':{'id':'m','display_name':'M'},'context_window':{'used_percentage':5}}
        out=subprocess.run([sys.executable,str(self.home/'.config/starfield-terminal/statusline.py')],
                 input=json.dumps(payload),text=True,env=self.env,capture_output=True,check=True).stdout
        self.assertIn('MY / LAB',out)

    def test_statusline_default_label_is_machine_name(self):
        self.run_cmd(['bash','scripts/install.sh','--with-claude'])
        payload={'session_id':'abc','workspace':{'current_dir':str(self.home)},
                 'model':{'id':'m','display_name':'M'},'context_window':{'used_percentage':5}}
        out=subprocess.run([sys.executable,str(self.home/'.config/starfield-terminal/statusline.py')],
                 input=json.dumps(payload),text=True,env=self.env,capture_output=True,check=True).stdout
        first=out.strip().splitlines()[0]
        self.assertIn('PROJECT',first)
        # The label must never be empty, whatever the host reports.
        self.assertGreater(len(first.strip()),2)

    def test_config_customization_and_gallery(self):
        self.run_cmd(['bash','scripts/install.sh'])
        cfg=self.home/'.config/starfield-terminal/config.json'
        cfg.write_text(json.dumps({'label':'MY / CONSTELLATIONS','status_label':'MY / LAB'}))
        self.run_cmd(['bash','scripts/install.sh'])
        self.assertEqual(json.loads(cfg.read_text())['label'],'MY / CONSTELLATIONS')
        p=self.run_cmd([sys.executable,str(self.home/'.config/starfield-terminal/welcome.py'),'--no-image','--gallery','--seed','3'])
        self.assertEqual(p.stdout.count('MY / CONSTELLATIONS'),6)

    def test_starship_opt_in_backup(self):
        stub = self.home/'fake-bin'
        stub.mkdir()
        executable = stub/'starship'
        executable.write_text('#!/bin/sh\n# fake Starship preset command for tests\n[ "$1" = "preset" ] || exit 1\nprintf "preset = %s\\n" "$2" > "$4"\n')
        executable.chmod(0o755)
        cfg=self.home/'.config/starship.toml'
        cfg.parent.mkdir(exist_ok=True)
        cfg.write_text('previous custom config')
        self.run_cmd(['bash','scripts/starship-presets.sh','--apply','pastel-powerline'],
                     extra_env={'PATH':str(stub)+os.pathsep+os.environ['PATH']})
        self.assertIn('pastel-powerline',cfg.read_text())
        backups=list(cfg.parent.glob('starship.toml.backup-*'))
        self.assertEqual(len(backups),1)
        self.assertEqual(backups[0].read_text(),'previous custom config')

if __name__=='__main__': unittest.main()
