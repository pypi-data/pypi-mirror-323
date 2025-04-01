from datetime import datetime
from typing import Any, Dict, Generator, List, Optional, Union

from gitlab.base import RESTObject
from gitlab.v4.objects import Project, ProjectBranch, ProjectCommit
from gitlab.v4.objects import User as GitlabUser

from jf_ingest.config import GitConfig
from jf_ingest.jf_git.adapters import GitAdapter
from jf_ingest.jf_git.clients.gitlab import GitlabClient
from jf_ingest.jf_git.standardized_models import (
    StandardizedBranch,
    StandardizedCommit,
    StandardizedOrganization,
    StandardizedPullRequest,
    StandardizedPullRequestMetadata,
    StandardizedRepository,
    StandardizedTeam,
    StandardizedUser,
)
from jf_ingest.utils import parse_gitlab_date


class GitlabAdapter(GitAdapter):

    def __init__(self, config: GitConfig):
        self.config = config
        self.client = GitlabClient(auth_config=config.git_auth_config)
        self.group_id_to_full_path: Dict[str, str] = {}

    def get_api_scopes(self) -> str:
        """Return the list of API Scopes. This is useful for Validation

        Returns:
            str: A string of API scopes we have, given the adapters credentials
        """
        raise NotImplementedError()

    @staticmethod
    def _get_group_id_from_gid(gitlab_gid: str) -> str:
        """Helper function.
        The Gitlab GQL returns Group (Organization) IDs with this weird GID format.
        All we care about is the number trailing at the end.
        Gitlab Format: gid://gitlab/Group/{ID_NUMBER}
        """
        return gitlab_gid.split('gid://gitlab/Group/')[1]

    @staticmethod
    def _get_project_id_from_gid(gitlab_gid: str) -> str:
        """Helper function.
        The Gitlab GQL returns Project (Organization) IDs with this weird GID format.
        All we care about is the number trailing at the end.
        Gitlab Format: gid://gitlab/Project/{ID_NUMBER}
        """
        return gitlab_gid.split('gid://gitlab/Project/')[1]

    @staticmethod
    def _standardize_commit_author(api_user: dict) -> StandardizedUser:
        id = api_user.get('id') or api_user.get('email')  # Commit users may not have ids
        name = api_user.get('name')
        login = api_user.get('login') or api_user.get('email')
        email = api_user.get('email')

        return StandardizedUser(
            id=str(id),
            login=str(login),
            name=str(name),
            email=str(email),
        )

    @staticmethod
    def _standardize_gitlab_commit(
        gitlab_commit: ProjectCommit | RESTObject,
        standardized_repo: StandardizedRepository,
        branch_name: str,
        strip_text_content: bool,
        redact_names_and_urls: bool,
    ) -> StandardizedCommit:
        """
        Converts a ProjectCommit from the gitlab client to a standardized jf commit.
        """
        commit_url = gitlab_commit.web_url if not redact_names_and_urls else None
        author = GitlabAdapter._standardize_commit_author(
            {
                'name': gitlab_commit.author_name,
                'email': gitlab_commit.author_email,
            }
        )
        return StandardizedCommit(
            hash=gitlab_commit.id,
            author=author,
            url=commit_url,
            commit_date=parse_gitlab_date(gitlab_commit.committed_date),
            author_date=parse_gitlab_date(gitlab_commit.authored_date),
            message=GitAdapter.sanitize_text(gitlab_commit.message, strip_text_content),
            is_merge=len(gitlab_commit.parent_ids) > 1,
            repo=standardized_repo.short(),  # use short form of repo
            branch_name=(
                branch_name
                if not redact_names_and_urls
                else GitAdapter.branch_redactor.redact_name(branch_name)
            ),
        )

    @staticmethod
    def _standardize_gitlab_project(
        gitlab_repo: Project | RESTObject, standardized_organization: StandardizedOrganization
    ) -> StandardizedRepository:
        """
        Converts a Project from the gitlab client to a standardized jf project.
        """
        return StandardizedRepository(
            id=str(gitlab_repo.id),
            name=gitlab_repo.name,
            full_name=gitlab_repo.name,
            url=gitlab_repo.web_url,
            default_branch_sha='',
            default_branch_name=gitlab_repo.default_branch,
            organization=standardized_organization,
            is_fork=getattr(gitlab_repo, 'forked_from_project', False),
        )

    @staticmethod
    def _standardize_gitlab_branch(
        gitlab_branch: ProjectBranch | RESTObject, standardized_repository: StandardizedRepository
    ) -> StandardizedBranch:
        """
        Converts a Branch (ProjectBranch) from the gitlab client to a standardized jf branch.
        """
        return StandardizedBranch(
            name=gitlab_branch.name,
            sha=gitlab_branch.commit['id'],
            repo_id=standardized_repository.id,
            is_default=gitlab_branch.default,
        )

    @staticmethod
    def _standardize_user(api_user: Union[RESTObject, GitlabUser]) -> StandardizedUser:
        return StandardizedUser(
            id=api_user.id,
            name=api_user.name,
            login=api_user.username,
            email=None,
            url=api_user.web_url,
        )

    def get_group_full_path_from_id(self, group_id: str) -> str:
        if group_id not in self.group_id_to_full_path:
            _, full_path, _ = self.client.get_organization_name_full_path_and_url(login=group_id)
            self.group_id_to_full_path[group_id] = full_path

        return self.group_id_to_full_path[group_id]

    def get_group_full_path_from_organization(self, org: StandardizedOrganization) -> str:
        return self.get_group_full_path_from_id(org.login)

    def get_organizations(self) -> List[StandardizedOrganization]:
        """Get the list of organizations the adapter has access to

        Returns:
            List[StandardizedOrganization]: A list of standardized organizations within this Git Instance
        """
        orgs: List[StandardizedOrganization] = []
        if not self.config.discover_organizations:
            for group_id in self.config.git_organizations:
                name, full_path, url = self.client.get_organization_name_full_path_and_url(
                    login=group_id
                )
                self.group_id_to_full_path[group_id] = full_path
                orgs.append(
                    StandardizedOrganization(id=group_id, name=name, login=group_id, url=url)
                )
        else:
            # Discover Orgs
            for api_org in self.client.get_organizations_gql():
                group_id = self._get_group_id_from_gid(api_org['groupIdStr'])
                full_path = api_org['fullPath']
                self.group_id_to_full_path[group_id] = full_path
                orgs.append(
                    StandardizedOrganization(
                        id=group_id, name=api_org['name'], login=group_id, url=api_org['webUrl']
                    )
                )

        return orgs

    def get_users(
        self, standardized_organization: StandardizedOrganization, limit: Optional[int] = None
    ) -> Generator[StandardizedUser, None, None]:
        """
        Get all users in a given Git Organization

        Args:
            standardized_organization (StandardizedOrganization): A standardized Git Organization Object
            limit (int, optional): When provided, only returns this many users. Defaults to None.

        Returns:
            Generator[StandardizedUser, None, None]: A generator of StandardizedUser objects
        """
        for idx, user in enumerate(self.client.get_users(group_id=standardized_organization.login)):
            if limit and idx >= limit:
                return

            yield self._standardize_user(user)

    def get_teams(
        self, standardized_organization: StandardizedOrganization, limit: Optional[int] = None
    ) -> Generator[StandardizedTeam, None, None]:
        """
        This function is to align with what the parent adapter class expects.
        GitLab does not have a concept of teams past groups, which we use as organizations.
        This will return an empty list, regardless of arguments.
        """
        teams: List[StandardizedTeam] = []
        yield from teams

    def get_repos(
        self, standardized_organization: StandardizedOrganization, use_gql: Optional[bool] = False
    ) -> Generator[StandardizedRepository, None, None]:
        """Get a list of standardized repositories within a given organization

        Args:
            standardized_organization (StandardizedOrganization): A standardized organization
            use_gql (bool, optional): Whether to use GQL queries. Defaults to False.

        Returns:
            Generator[StandardizedRepository]: An iterable of standardized Repositories
        """
        if use_gql:
            full_path = self.get_group_full_path_from_organization(standardized_organization)
            for repo in self.client.get_repos_gql(full_path):
                yield StandardizedRepository(
                    id=self._get_project_id_from_gid(repo['id']),
                    name=repo['name'],
                    full_name=repo['name'],
                    url=repo['webUrl'],
                    default_branch_sha='',
                    default_branch_name=repo['repository']['defaultBranchName'],
                    organization=standardized_organization,
                    is_fork=repo['isForked'],
                )
        else:
            for client_repo in self.client.get_repos(standardized_organization):
                yield self._standardize_gitlab_project(client_repo, standardized_organization)

    def get_commits_for_default_branch(
        self,
        standardized_repo: StandardizedRepository,
        limit: Optional[int] = None,
        pull_since: Optional[datetime] = None,
        pull_until: Optional[datetime] = None,
    ) -> Generator[StandardizedCommit, None, None]:
        """For a given repo, get all the commits that are on the Default Branch.

        Args:
            standardized_repo (StandardizedRepository): A standard Repository object
            limit (int): limit the number of commit objects we will yield
            pull_since (datetime): filter commits to be newer than this date
            pull_until (datetime): filter commits to be older than this date

        Returns:
            Generator[StandardizedCommit]: An iterable of standardized commits
        """
        default_branch_name: Optional[str] = standardized_repo.default_branch_name
        if default_branch_name:
            for j, api_commit in enumerate(
                self.client.get_commits(
                    standardized_repo,
                    since=pull_since,
                    branch_name=default_branch_name,
                ),
                start=1,
            ):
                yield self._standardize_gitlab_commit(
                    api_commit,
                    standardized_repo,
                    default_branch_name,
                    self.config.git_strip_text_content,
                    self.config.git_redact_names_and_urls,
                )
                if limit and j >= limit:
                    return

    def get_branches_for_repo(
        self,
        standardized_repo: StandardizedRepository,
        pull_branches: Optional[bool] = False,
    ) -> Generator[StandardizedBranch, None, None]:
        """Function for pulling branches for a repository. By default, pull_branches will run as False,
        so we will only process the default branch. If pull_branches is true, than we will pull all
        branches in this repository

        Args:
            standardized_repo (StandardizedRepository): A standardized repo, which hold info about the default branch.
            pull_branches (bool): A boolean flag. If True, pull all branches available on Repo. If false, only process the default branch. Defaults to False.

        Yields:
            StandardizedBranch: A Standardized Branch Object
        """
        search_term: Optional[str] = None
        if not pull_branches:
            search_term = f'^{standardized_repo.default_branch_name}$'

        for api_branch in self.client.get_branches_for_repo(
            standardized_repo, search_term=search_term
        ):
            yield self._standardize_gitlab_branch(api_branch, standardized_repo)

    def get_commits_for_branches(
        self,
        standardized_repo: StandardizedRepository,
        branches: List[StandardizedBranch],
        pull_since: Optional[datetime] = None,
        pull_until: Optional[datetime] = None,
    ) -> Generator[StandardizedCommit, None, None]:
        """For a given repo, get all the commits that are on the included branches.
        Included branches are found by crawling across the branches pulled/available
        from get_filtered_branches

        Args:
            standardized_repo (StandardizedRepository): A standard Repository object
            pull_since (datetime): A date to pull from
            pull_until (datetime): A date to pull up to

        Returns:
            List[StandardizedCommit]: A list of standardized commits
        """
        raise NotImplementedError()

    def get_pr_metadata(
        self,
        standardized_repo: StandardizedRepository,
        limit: Optional[int] = None,
        pr_pull_from_date: Optional[datetime] = None,
    ) -> Generator[StandardizedPullRequestMetadata, None, None]:
        """Get all PRs, but only included the bare necesaties

        Args:
            standardized_repo (StandardizedRepository): A standardized repository
            limit (int, optional): When provided, the number of items returned is limited.
                Useful for the validation use case, where we want to just verify we can pull PRs.
                Defaults to None.
            pr_pull_from_date: This is currently only used by the GithubAdapter. Probably won't be useful for this adapter

        Returns:
            List[StandardizedPullRequest]: A list of standardized PRs
        """
        raise NotImplementedError()

    def git_provider_pr_endpoint_supports_date_filtering(self) -> bool:
        """Returns a boolean on if this PR supports time window filtering.
        So far, Github DOES NOT support this (it's adapter will return False)
        but ADO does support this (it's adapter will return True)

        Returns:
            bool: A boolean on if the adapter supports time filtering when searching for PRs
        """
        return True

    def get_prs(
        self,
        standardized_repo: StandardizedRepository,
        pull_files_for_pr: bool = False,
        hash_files_for_prs: bool = False,
        limit: Optional[int] = None,
        start_cursor: Optional[Any] = None,
        start_window: Optional[datetime] = None,
        end_window: Optional[datetime] = None,
    ) -> Generator[StandardizedPullRequest, None, None]:
        """Get the list of standardized Pull Requests for a Standardized Repository.

        Args:
            standardized_repo (StandardizedRepository): A standardized repository
            pull_files_for_pr (bool): When provided, we will pull file metadata for all PRs
            hash_files_for_prs (bool): When provided, all file metadata will be hashed for PRs
            limit (int, optional): When provided, the number of items returned is limited.
                Useful for the validation use case, where we want to just verify we can pull PRs.
                Defaults to None.

        Returns:
            List[StandardizedPullRequest]: A list of standardized PRs
        """
        raise NotImplementedError()
