from unittest.mock import MagicMock

import pytest
import requests

import prefect
from prefect.tasks.github import CreateGitHubPR
from prefect.utilities.configuration import set_temporary_config


class TestCreateGitHubPRInitialization:
    def test_initializes_with_nothing_and_sets_defaults(self):
        task = CreateGitHubPR()
        assert task.repo is None
        assert task.body is None
        assert task.title is None
        assert task.head is None
        assert task.base is None

    def test_additional_kwargs_passed_upstream(self):
        task = CreateGitHubPR(name="test-task", checkpoint=True, tags=["bob"])
        assert task.name == "test-task"
        assert task.checkpoint is True
        assert task.tags == {"bob"}

    @pytest.mark.parametrize("attr", ["repo", "body", "title", "head", "base"])
    def test_initializes_attr_from_kwargs(self, attr):
        task = CreateGitHubPR(**{attr: "my-value"})
        assert getattr(task, attr) == "my-value"

    def test_repo_is_required_eventually(self):
        task = CreateGitHubPR()
        with pytest.raises(ValueError, match="repo"):
            task.run()


class TestCredentialsandProjects:
    def test_creds_are_pulled_from_secret_at_runtime(self, monkeypatch):
        task = CreateGitHubPR(token_secret="GITHUB_ACCESS_TOKEN")

        req = MagicMock()
        monkeypatch.setattr(requests, "post", req)

        with prefect.context(secrets=dict(GITHUB_ACCESS_TOKEN={"key": 42})):
            task.run(repo="org/repo")

        assert req.call_args[1]["headers"]["AUTHORIZATION"] == "token {'key': 42}"
