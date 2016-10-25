createtag
=========

A role to create a git tag in a repo and push it to any remotes.

Requirements
------------

Git must be installed on any host that will run this role.

Role Variables
--------------

    repo_location: the path to the git repo, defaults to '.'
    git_tag: the tag to apply, use templating to make it sensible!

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

License
-------

MIT

Author Information
------------------

Chris Withers <chris@withers.org>
