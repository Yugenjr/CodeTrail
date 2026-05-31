import pytest

from utils.repo_utils import IssueExplorer


class DummyClient:
    def __init__(self, issues):
        self._issues = issues

    def get_issues(self, owner, repo, params=None):
        return list(self._issues)


def test_issue_explorer_search_filters():
    issues = [
        {"number": 1, "title": "Fix bug in parser", "body": "This is a bug"},
        {"number": 2, "title": "Add feature", "body": "Feature request"},
        {"number": 3, "title": "Search crash", "body": "bug when searching"},
    ]
    client = DummyClient(issues)
    explorer = IssueExplorer(client=client)

    results = explorer.search("owner", "repo", "bug")
    numbers = [r["number"] for r in results]
    assert 1 in numbers
    assert 3 in numbers
    assert 2 not in numbers
