"""Integration tests run with temporary HOME; never modify real shell profiles."""
import json
import os
import shutil
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

    def fake_claude(self, extra=()):
        """A stand-in binary carrying an embedded verb table."""
        words = (['Baking', 'Cooking', 'Brewing', 'Smooshing', 'Razzle-dazzling',
                  'Tinkering'] + ['Filler%02d' % i for i in range(54)] + list(extra))
        stub = self.home/'fake-bin'/'claude'
        stub.parent.mkdir(exist_ok=True)
        # Same shape as the real bundle: a flat array next to the anchor word.
        stub.write_text('#!/bin/sh\nexec /bin/true\n/*' + json.dumps(words) + '*/\n')
        stub.chmod(0o755)
        return stub, words

    def test_spinner_install_keeps_other_settings_and_backs_up(self):
        settings = self.home/'.claude/settings.json'
        settings.parent.mkdir()
        settings.write_text(json.dumps({'model': 'some-model', 'theme': 'dark'}))
        stub, words = self.fake_claude()
        p = self.run_cmd([sys.executable, 'scripts/claude-spinner.py', '--claude', str(stub)])
        self.assertIn('native verbs read from', p.stdout)
        applied = json.loads(settings.read_text())
        self.assertEqual(applied['model'], 'some-model')
        self.assertEqual(applied['theme'], 'dark')
        self.assertEqual(applied['spinnerVerbs']['mode'], 'replace')
        verbs = applied['spinnerVerbs']['verbs']
        self.assertIn('🥐 Baking', verbs)
        self.assertIn('🫠 Smooshing', verbs)
        self.assertIn('🎩 Conjuring', verbs)  # our extra, not a native word
        self.assertEqual(len(verbs), len(words)+6)
        backups = list((self.home/'.config/starfield-terminal/backups').glob('spinner-*'))
        self.assertEqual(len(backups), 1)
        self.assertTrue((backups[0]/'claude-settings.json').is_file())

    def test_spinner_says_when_it_fell_back_to_the_snapshot(self):
        stub = self.home/'only-a-wrapper'/'claude'
        stub.parent.mkdir()
        # A shim with no verb table and no sibling binary to fall back to.
        stub.write_text('#!/bin/sh\nexec /bin/true\n')
        stub.chmod(0o755)
        p = self.run_cmd([sys.executable, 'scripts/claude-spinner.py', '--claude', str(stub)])
        self.assertIn('bundled snapshot', p.stdout)
        self.assertIn('could not be inspected', p.stdout)
        applied = json.loads((self.home/'.claude/settings.json').read_text())
        self.assertEqual(len(applied['spinnerVerbs']['verbs']), len(self.fallback_verbs())+6)

    def fallback_verbs(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            'claude_spinner', ROOT/'scripts/claude-spinner.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module.FALLBACK_VERBS

    def test_extracts_verbs_from_real_claude_when_installed(self):
        claude = shutil.which('claude')
        if not claude:
            self.skipTest('Claude Code is not installed')
        p = self.run_cmd([sys.executable, 'scripts/claude-spinner.py', '--dry-run',
                          '--claude', claude])
        data = json.loads(p.stdout)
        self.assertEqual(data['spinnerVerbs']['mode'], 'replace')
        self.assertGreater(len(data['spinnerVerbs']['verbs']), 100)

    def test_spinner_check_reports_new_native_verbs(self):
        stub, words = self.fake_claude()
        self.run_cmd([sys.executable, 'scripts/claude-spinner.py', '--claude', str(stub)])
        self.run_cmd([sys.executable, 'scripts/claude-spinner.py', '--claude', str(stub), '--check'])
        stub, words = self.fake_claude(extra=['Zigzagging'])
        p = self.run_cmd([sys.executable, 'scripts/claude-spinner.py', '--claude', str(stub), '--check'], expected=1)
        self.assertIn('Zigzagging', p.stdout)
        # Re-running picks the new word up without touching anything else.
        self.run_cmd([sys.executable, 'scripts/claude-spinner.py', '--claude', str(stub)])
        applied = json.loads((self.home/'.claude/settings.json').read_text())
        self.assertIn('🦓 Zigzagging', applied['spinnerVerbs']['verbs'])

    def test_spinner_remove_restores_previous_value(self):
        settings = self.home/'.claude/settings.json'
        settings.parent.mkdir()
        original = {'model': 'some-model',
                    'spinnerVerbs': {'mode': 'append', 'verbs': ['Mine']}}
        settings.write_text(json.dumps(original))
        stub, _ = self.fake_claude()
        self.run_cmd([sys.executable, 'scripts/claude-spinner.py', '--claude', str(stub)])
        self.run_cmd([sys.executable, 'scripts/claude-spinner.py', '--remove'])
        self.assertEqual(json.loads(settings.read_text()), original)
        self.assertFalse((self.home/'.config/starfield-terminal/spinner-install-state.json').exists())

    def test_installer_with_spinner_and_uninstall(self):
        stub, words = self.fake_claude()
        env = {'PATH': str(stub.parent)+os.pathsep+os.environ['PATH']}
        self.run_cmd(['bash', 'scripts/install.sh', '--with-spinner'], extra_env=env)
        applied = json.loads((self.home/'.claude/settings.json').read_text())
        self.assertEqual(applied['spinnerVerbs']['mode'], 'replace')
        self.assertEqual(len(applied['spinnerVerbs']['verbs']), len(words)+6)
        self.assertTrue((self.home/'.config/starfield-terminal/claude-spinner.py').is_file())
        self.run_cmd(['bash', 'scripts/uninstall.sh'])
        restored = json.loads((self.home/'.claude/settings.json').read_text())
        self.assertNotIn('spinnerVerbs', restored)

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
        # An empty stdin must fail safe: two content lines plus the spacer.
        lines=proc.stdout.splitlines()
        self.assertEqual(len(lines),3)
        self.assertEqual(lines[2],'⠀')
        status=subprocess.run([sys.executable,str(self.home/'.config/starfield-terminal/statusline.py')],
                 input=json.dumps(payload),text=True,env=self.env,capture_output=True,check=True)
        self.assertIn('~18%',status.stdout)
        self.run_cmd(['bash','scripts/uninstall.sh'])
        restored=json.loads(settings.read_text())
        self.assertEqual(restored,original)
        self.assertNotIn('# >>> STARFIELD', (self.home/'.zshrc').read_text())

    def test_name_flag_sets_status_label(self):
        self.run_cmd(['bash','scripts/install.sh','--name=NOVA / LAB'])
        cfg=json.loads((self.home/'.config/starfield-terminal/config.json').read_text())
        self.assertEqual(cfg['status_label'],'NOVA / LAB')
        self.assertEqual(cfg['label'],'STARFIELD / TERMINAL')

    def test_non_interactive_install_leaves_name_to_machine(self):
        self.run_cmd(['bash','scripts/install.sh'])
        cfg=json.loads((self.home/'.config/starfield-terminal/config.json').read_text())
        self.assertNotIn('status_label',cfg)

    def test_diagnose_explains_rendering(self):
        self.run_cmd(['bash','scripts/install.sh'])
        p=self.run_cmd([sys.executable,str(self.home/'.config/starfield-terminal/welcome.py'),'--diagnose'])
        self.assertIn('diagnosis',p.stdout)
        self.assertIn('width',p.stdout)
        self.assertIn('constellation images',p.stdout)
        self.assertIn('heading sprites',p.stdout)
        # Piped stdout is not a terminal: the report must say so, not crash.
        self.assertIn('stdout is a terminal',p.stdout)
        self.assertIn('[FAIL]',p.stdout)

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
