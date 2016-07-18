import os
from subprocess import check_output, STDOUT, CalledProcessError

from testfixtures import TempDirectory, compare


class GitHelper(object):

    repo = 'local/'

    def setUp(self):
        self.dir = TempDirectory()
        self.addCleanup(self.dir.cleanup)

    def git(self, command, repo=None):
        repo_path = self.dir.getpath(repo or self.repo)
        try:
            return check_output(['git'] + command.split(), cwd=repo_path, stderr=STDOUT)
        except CalledProcessError as e:
            self.fail(e.output)

    def git_rev_parse(self, label, repo=None):
        return self.git('rev-parse --verify -q --short '+label, repo).strip()

    def check_tags(self, expected, repo=None):
        actual = {}
        for tag in self.git('tag', repo).split():
            actual[tag] = self.git_rev_parse(tag, repo)
        compare(expected, actual=actual)

    def make_repo_with_content(self, repo):
        if not os.path.exists(self.dir.getpath(repo)):
            self.dir.makedir(repo)
        self.git('init', repo)
        self.dir.write(repo + 'a', 'some content')
        self.dir.write(repo + 'b', 'other content')
        self.dir.write(repo + 'c', 'more content')
        self.git('add .', repo)
        self.git('commit -m initial', repo)
