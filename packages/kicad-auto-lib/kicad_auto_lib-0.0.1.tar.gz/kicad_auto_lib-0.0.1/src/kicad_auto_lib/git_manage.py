"""Git Automation Utilities

This module provides utility functions for automating Git operations, including
checking if a folder is a Git repository (`git_check_if_repo`) and performing
commit and push operations (`git_commit_and_push`).

Functions
---------
git_check_if_repo(folder_path: str) -> bool
    Check if the given folder is a Git repository.

git_commit_and_push(folder_path: str, commit_message: str) -> Union[bool, str]
    Commit and push changes in the given Git repository, ensuring the local
    repository is up to date with retries and interrupt handling.

Examples
--------
To check if a folder is a Git repository:
>>> git_check_if_repo("/path/to/repo")
True

To commit and push changes:
>>> result = git_commit_and_push("/path/to/repo", "Update README")
>>> print(result)
True

Notes
-----
- This module requires the `os`, `subprocess`, `time`, and `typing` Python standard libraries.
- The `git_commit_and_push` function handles interrupt signals (Ctrl+C) gracefully,
  allowing users to abort retries without terminating the entire program.
"""

import os
import subprocess
import time
from contextlib import contextmanager


def git_check_if_repo(folder_path: str) -> bool:
    """
    Check if the given folder is a Git repository.

    Parameters
    ----------
    folder_path : str
        The path to the folder to check.

    Returns
    -------
    bool
        True if the folder is a Git repository, False otherwise.
    """
    # Check if the .git directory exists in the given folder
    git_dir = os.path.join(folder_path, '.git')
    return os.path.isdir(git_dir)


@contextmanager
def change_directory(path: str):
    """
    Context manager for temporarily changing the working directory.

    Parameters
    ----------
    path : str
        The directory to change to.
    """
    old_dir = os.getcwd()
    try:
        os.chdir(path)
        yield
    finally:
        os.chdir(old_dir)

def git_commit_and_push(folder_path: str, commit_message: str) -> bool:
    """
    Commit and push changes in the given Git repository, ensuring the local repository is up to date.
    Retries every 5 seconds for up to 4 times if any Git operation fails.

    Parameters
    ----------
    folder_path : str
        The path to the Git repository.
    commit_message : str
        The commit message to use.

    Returns
    -------
    bool
        True if the commit and push were successful, False otherwise.
    """
    max_retries = 4
    retry_delay = 5  # in seconds

    def execute_git_commands() -> bool:
        """Execute the sequence of Git commands."""
        subprocess.run(['git', 'pull', '--no-rebase'], check=True)
        subprocess.run(['git', 'add', '.'], check=True)
        subprocess.run(['git', 'commit', '-m', commit_message], check=True)
        subprocess.run(['git', 'push'], check=True)
        return True

    with change_directory(folder_path):
        for attempt in range(max_retries):
            try:
                return execute_git_commands()

            except (subprocess.CalledProcessError, Exception) as e:
                print(f"Attempt {attempt + 1} / {max_retries} failed: {e}")
                if attempt < max_retries - 1:
                    print(f"Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
    print("Failed to commit or push on Git")
    return False

# Example usage (commented out for library usage)
# if __name__ == "__main__":
#     repo_path = "/path/to/your/repo"
#     commit_msg = "Your commit message here"
#
#     if git_check_if_repo(repo_path):
#         result = git_commit_and_push(repo_path, commit_msg)
#         print(result)
#     else:
#         print("The specified folder is not a Git repository.")