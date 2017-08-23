createtag
=========

A role to create a git tag in a repo and push it to the specified remote.

Requirements
------------

Git must be installed on any host that will run this role.

Role Variables
--------------

    git_repo_location: the path to the git repo, defaults to '.'
    git_remote: remote to push to, defaults to 'origin', set to null to not push.
    git_tag: the tag to apply, use templating to make it sensible!
    skip_if_tag_matching: see 'Conditional Tagging' below.

Dependencies
------------

None.

Example Playbook
----------------

This will create a tag something like `qa-2016-06-19`, assuming `env` is 
defined somewhere, such as in your inventory file:

    - hosts: localhost
      vars:
        git_tag: "{{env}}-{{ansible_date_time.date}}"
      roles:
        - cjw296.createtag

Conditional Tagging
-------------------

If you have a daily release process that pushes the `HEAD` of a branch to
a testing environment, you may find that this role creates a lot of tags
on a commit that ends up being `HEAD` for a number of weeks.

To prevent that, you can set `skip_if_tag_matching` to a glob such that
each commit will only be tagged the first time it is released to a particular
environment.

Modifying the above example, this gives:


    - hosts: localhost
      vars:
        git_tag: "{{env}}-{{ansible_date_time.date}}"
        skip_if_tag_matching: "{{env}}*"
      roles:
        - cjw296.createtag

License
-------

MIT

Author Information
------------------

Chris Withers <chris@withers.org>
