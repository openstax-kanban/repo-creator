import json
import os
import sys
from datetime import datetime
from pathlib import Path

import github3.exceptions
from docopt import docopt
from github3 import GitHub


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


def cli():
    cli_docs = """Issue Importer: Import issues into a repository from a json file
Usage:
  imp <organization> <repository_name> [-hf FILE]

Options:
  -h --help  Show this screen
  -f FILE --file=FILE  The json data file with issues [default: ./issues.json]

Examples:
  imp openstax-kanban team1 
  imp openstax-kanban team2 --file issues_trello.json
    """
    username = os.environ.get('GITHUB_USER', None)
    password = os.environ.get('GITHUB_PASSWORD', None)
    github = None

    if username and password:
        github = GitHub(username=username, password=password)
    else:
        print('You need to set GITHUB_USER and GITHUB_PASSWORD environment variables')
        return sys.exit()

    arguments = docopt(cli_docs)

    organization = arguments['<organization>']
    repo_name = arguments['<repository_name>']
    issue_file = Path(arguments['--file'])

    if issue_file.is_file():
        print('Attempting to load the issue file ...')
        with open(issue_file, 'r') as json_data:
            issue_data = json.load(json_data)
        print('File loaded successfully')
    else:
        print("There was an error trying to read your file. "
              "Please make sure the path is correct")

    # Prepare issues
    issues = [{'title': i['name'], 'body': i['desc']}
              for i in issue_data['cards']]

    # Check if the repository exists, if not exit.
    try:
        repo = github.repository(owner=organization, repository=repo_name)
        print(repo)
    except github3.exceptions.NotFoundError:
        print("That repository was not found. You'll need to create it in GitHUB first")
        return sys.exit()

    # Import the issues
    for issue in issues:
        import_issue(repo, issue)


if __name__ == "__main__":
    cli()
