from __future__ import print_function

import os
from subprocess import check_call, CalledProcessError
from tempfile import TemporaryFile

test_dir = os.path.dirname(__file__)


class AnsibleHelper(object):

    def __init__(self, dir, workspace='workspace'):
        self.dir = dir
        self.workspace = workspace
        self.workspace_path = self.dir.getpath(self.workspace)
        self.write_config()

    def _write(self, name, content):
        self.dir.write([self.workspace, name], content)

    def write_config(self):
        self._write(
            'ansible.cfg',
            '\n'.join((
                '[defaults]',
                'roles_path='+self.workspace_path,
            ))+'\n'
        )

    def install_role(self, path, name):
        os.symlink(path, self.dir.getpath([self.workspace, name]))

    def run_playbook(self, yml, should_fail=False):
        playbook_path = self.dir.write('playbook.yml', yml)
        inventory_path = os.path.join(test_dir, 'inventory')
        output = TemporaryFile()
        try:
            check_call(
                ['ansible-playbook', '-vv', '-i', inventory_path, playbook_path],
                cwd=self.workspace_path,
                stdout=output
            )
        except CalledProcessError:
            output.seek(0)
            if should_fail:
                return output.read()
            else:
                print('cwd:', self.workspace_path)
                print(output.read())
                raise
