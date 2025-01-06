from git import GitCommandError, Repo


class GitCLIOperator:

    def __init__(self, repo_path: str | None = None):
        """Initialize GitOperator with repository path.

        Args:
            repo_path: Path to git repository. Uses current directory if None.
        """
        try:
            self.repo = Repo(repo_path or ".")
        except Exception as e:
            raise RuntimeError(f"Failed to initialize repository: {str(e)}")

    def checkout_branch(self, branch_name: str, new_branch: bool = False) -> None:
        """Checks out repository to specified branch name.

        Args:
            branch_name: Name of the branch to checkout
            new_branch: Whether to create a new branch
        """
        git = self.repo.git
        try:
            if new_branch:
                git.checkout("-b", branch_name)
            else:
                git.checkout(branch_name)
        except GitCommandError as e:
            raise RuntimeError(f"Failed to checkout branch {branch_name}: {str(e)}")
        else:
            print(f"Checked out branch: {branch_name}")

    def pull(self, branch_name: str) -> None:
        """Pulls from specified origin branch.

        Args:
            branch_name: Name of the branch to pull from
        """
        try:
            origin = self.repo.remotes.origin
            origin.pull(branch_name)
        except GitCommandError as e:
            raise RuntimeError(f"Failed to pull changes: {str(e)}")
        else:
            print("Pulled changes successfully.")

    def commit(self, commit_message: str) -> None:
        """Commits all changes in current repository.

        Args:
            commit_message: Commit message
        """
        try:
            self.repo.git.add(A=True)
            self.repo.index.commit(commit_message)
        except GitCommandError as e:
            raise RuntimeError(f"Failed to commit changes: {str(e)}")
        else:
            print("Committed changes with message:", commit_message)

    def push(self, branch_name: str) -> None:
        """Pushes changes to specified branch.

        Args:
            branch_name: Name of the branch to push to
        """
        try:
            origin = self.repo.remotes.origin
            origin.push(branch_name)
        except GitCommandError as e:
            raise RuntimeError(f"Failed to push changes: {str(e)}")
        else:
            print("Pushed changes successfully.")
