import os
from datetime import date
from unittest import TestCase

from .ansible import AnsibleHelper
from .git import GitHelper

role_path = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))


class TestRoleNoRemote(GitHelper, TestCase):

    def setUp(self):
        super(TestRoleNoRemote, self).setUp()
        self.ansible = AnsibleHelper(self.dir, self.repo)
        self.ansible.install_role(role_path, 'create_tag')

    def test_simple_with_defaults(self):
        self.make_repo_with_content(self.repo)
        self.ansible.run_playbook(yml="""
            - hosts: localhost
              vars:
                git_remote:
                git_tag: test_tag
              roles:
                - create_tag
        """)
        self.check_tags(expected={'test_tag': self.git_rev_parse('HEAD')})

    def test_tag_templated_from_environment(self):
        self.make_repo_with_content(self.repo)
        self.ansible.run_playbook(yml="""
            - hosts: localhost
              vars:
                env: test
                git_remote:
                git_tag: "{{env}}_{{ansible_date_time.date}}"
              roles:
                - create_tag
        """)

        self.check_tags(expected={
            'test_'+str(date.today()): self.git_rev_parse('HEAD')
        })


class TestFromOtherDirectory(GitHelper, TestCase):

    def setUp(self):
        super(TestFromOtherDirectory, self).setUp()
        self.ansible = AnsibleHelper(self.dir)
        self.ansible.install_role(role_path, 'create_tag')

    def test_specific_git_repo_location(self):
        self.make_repo_with_content(self.repo)
        self.ansible.run_playbook(yml="""
            - hosts: localhost
              vars:
                git_tag: test_tag
                git_remote:
                git_repo_location: ../local
              roles:
                - create_tag
        """)
        self.check_tags(expected={'test_tag': self.git_rev_parse('HEAD')})


class TestRoleWithRemote(GitHelper, TestCase):

    def setUp(self):
        super(TestRoleWithRemote, self).setUp()
        self.make_repo_with_content('upstream/')
        self.git('clone '+self.dir.getpath('upstream')+' local',
                 '.')
        self.ansible = AnsibleHelper(self.dir, self.repo)
        self.ansible.install_role(role_path, 'create_tag')

    def test_with_remote(self):
        self.ansible.run_playbook(yml="""
            - hosts: localhost
              vars:
                git_tag: test_tag
              roles:
                - create_tag
        """)
        rev = self.git_rev_parse('HEAD')
        self.check_tags(expected={'test_tag': rev})
        self.check_tags(expected={'test_tag': rev}, repo='upstream/')

    def test_duplicate_tag_create_same_rev(self):
        self.git('tag test_tag', 'upstream/')
        self.ansible.run_playbook(yml="""
            - hosts: localhost
              vars:
                git_tag: test_tag
              roles:
                - create_tag
        """)
        rev = self.git_rev_parse('HEAD')
        self.check_tags(expected={'test_tag': rev})
        self.check_tags(expected={'test_tag': rev}, repo='upstream/')

    def test_duplicate_tag_create_different_rev(self):
        self.git('tag test_tag', 'upstream/')
        upstream_rev = self.git_rev_parse('test_tag', 'upstream/')
        self.dir.write('local/c', 'changed')
        self.git('commit -m changed .')

        output = self.ansible.run_playbook(
            should_fail=True,
            yml="""
            - hosts: localhost
              vars:
                git_tag: test_tag
              roles:
                - create_tag
        """)
        self.assertTrue('Existing tag clashes' in output, output)
        self.assertTrue(
            'current head: {}, existing tag: {}'.format(
                self.git_rev_parse('HEAD'), upstream_rev
            ) in output, output)
        self.check_tags(expected={'test_tag': upstream_rev}, repo='upstream/')
        self.check_tags(expected={'test_tag': upstream_rev})

    def test_skip_when_tag_exists(self):
        self.git('tag test_1', 'upstream/')
        self.ansible.run_playbook(yml="""
            - hosts: localhost
              vars:
                git_tag: test_2
                skip_if_tag_matching: test_*
              roles:
                - create_tag
        """)
        rev = self.git_rev_parse('HEAD')
        self.check_tags(expected={'test_1': rev})
        self.check_tags(expected={'test_1': rev}, repo='upstream/')

    def test_skip_when_tag_on_old(self):
        self.git('tag test_1', 'upstream/')
        upstream_rev = self.git_rev_parse('test_1', 'upstream/')
        self.dir.write('local/c', 'changed')
        self.git('commit -m changed .')
        self.ansible.run_playbook(yml="""
            - hosts: localhost
              vars:
                git_tag: test_2
                skip_if_tag_matching: test_*
              roles:
                - create_tag
        """)
        rev = self.git_rev_parse('HEAD')
        self.check_tags(expected={'test_1': upstream_rev,
                                  'test_2': rev})
        self.check_tags(expected={'test_1': upstream_rev,
                                  'test_2': rev},
                        repo='upstream/')

    def test_only_push_specific_tag(self):
        rev = self.git_rev_parse('HEAD')
        self.git('tag other')
        self.ansible.run_playbook(yml="""
            - hosts: localhost
              vars:
                git_tag: test_tag
              roles:
                - create_tag
        """)
        self.check_tags(expected={'test_tag': rev, 'other': rev})
        self.check_tags(expected={'test_tag': rev}, repo='upstream/')
