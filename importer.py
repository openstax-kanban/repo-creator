import json
import os
import sys
from datetime import datetime
from pathlib import Path

import github3.exceptions
from docopt import docopt
from github3 import GitHub


def load_json_data(filepath):
    if filepath.is_file():
        print('Attempting to load the issue file ...')
        with open(filepath, 'r') as json_data:
            data = json.load(json_data)
        print('File loaded successfully')
    else:
        print("There was an error trying to read your file. "
              "Please make sure the path is correct")
        sys.exit()
    return data


def import_issues(repo, issue_file, is_dry=False):
    issue_data = load_json_data(issue_file)

    # Prepare issues
    issues = [{'title': i['name'], 'body': i['desc']}
              for i in issue_data['cards']]

    # Import the issues
    for issue in issues:
        print(issue)
        if is_dry:
            print(issue)
        else:
            import_issue(repo, issue)


def import_issue(repo, issue, created_at=None):
    if created_at:
        issue['created_at'] = created_at
    else:
        issue['created_at'] = datetime.utcnow()

    if not issue['body']:
        issue['body'] = issue['title']

    try:
        repo.import_issue(**issue)
    except github3.exceptions.NotFoundError:
        print('There was an error trying to import that issue, maybe permissions?')
    return


def import_labels(repo, labels_file, is_dry=False):
    label_data = load_json_data(labels_file)

    # Prepare labels
    labels = [{'name': i['name'], 'color': i['hex']}
              for i in label_data['labels']]

    for label in labels:
        if is_dry:
            print(label)
        else:
            repo.create_label(**label)


def import_members(from_organization, to_organization, is_dry=False):
    print(from_organization)
    print(to_organization)

    members = [member.login for member in from_organization.members()]

    for member in members[49:]:
        if is_dry:
            print(member)
        else:
            print('You will only be able to import 50 members in a 24 hour period')
            try:
                m = to_organization.add_or_update_membership(member)
            except github3.exceptions.ForbiddenError:
                print('You may have hit the 50 invites per day restriction.')


def cli():
    cli_docs = """Issue Importer: Import issues into a repository from a json file
Usage:
  imp issues <organization> <repository_name> [-hi FILE] [--dry]
  imp labels <organization> <repository_name> [-hL FILE] [--dry]
  imp members <from_organization> <to_organization> [-h] [--dry]

Options:
  -h --help  Show this screen
  -i FILE --issues_file=FILE  The json data file with issues [default: ./issues.json]
  -L FILE --labels_file=FILE  The json data file with labels [default: ./labels.json]
  -d --dry  Do a dry run without importing issues to GitHub

Examples:
  imp issues openstax-kanban team1 
  imp issues openstax-kanban team2 --issues_file trello.json
  imp labels openstax-kanban team3
  imp labels openstax-kanban team4 --labels_file labels.json

Notes:
  You will need to set GITHUB_USER and GITHUB_PASSWORD environment variables
  in order to being using this command line application.
    """
    github = None

    # Create arguments object which contains passed in arguments and options
    arguments = docopt(cli_docs)

    username = os.environ.get('GITHUB_USER', None)
    password = os.environ.get('GITHUB_PASSWORD', None)

    # Ensure we have some important ENV VARS set
    if username and password:
        github = GitHub(username=username, password=password)
    else:
        print('You need to set GITHUB_USER and GITHUB_PASSWORD environment variables')
        return sys.exit()

    # Set necessary variables created from the command line
    organization = arguments['<organization>']
    repo_name = arguments['<repository_name>']
    from_organization = arguments['<from_organization>']
    to_organization = arguments['<to_organization>']
    issue_file = Path(arguments['--issues_file'])
    labels_file = Path(arguments['--labels_file'])
    issues = arguments['issues']
    labels = arguments['labels']
    members = arguments['members']
    is_dry = arguments['--dry']

    # Check if the repository exists, if not exit.
    try:
        repo = github.repository(owner=organization, repository=repo_name)
        print('The {} repository is available'.format(repo))
    except github3.exceptions.NotFoundError:
        print("That repository was not found. You'll need to create it in GitHUB first")
        return sys.exit()

    if issues:
        print('Importing issues ...')
        import_issues(repo, issue_file, is_dry)

    if labels:
        print('Importing labels ...')
        import_labels(repo, labels_file, is_dry)

    if members:
        print('Importing members ...')
        from_organization = github.organization(from_organization)
        to_organization = github.organization(to_organization)
        import_members(from_organization, to_organization, is_dry)


if __name__ == "__main__":
    cli()
