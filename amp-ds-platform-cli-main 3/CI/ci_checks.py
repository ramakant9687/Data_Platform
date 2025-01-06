import subprocess
import os
import sys

GIT_COMMIT_ID = os.environ.get("GIT_PR_COMMIT", "False")
GIT_BRANCH_NAME = os.environ.get("GIT_PR_SOURCE_BRANCH", "False")

if GIT_COMMIT_ID == "False" or GIT_BRANCH_NAME == "False":
    print(
        "Failed to get env variables for Git Commit SHA or Git Branch name. These are retrieved using the environment "
        "variables: `GIT_PR_COMMIT` and `GIT_PR_SOURCE_BRANCH` in RIO builds."
    )
    sys.exit(1)


def is_valid_branch_name() -> bool:
    """
    Checks branch name starts with feature, bugfix or release.
    :return: bool
    """
    if not GIT_BRANCH_NAME.startswith(("feature/", "bugfix/", "release/", "develop")):
        print(
            f"Branch name must adhere to agreed upon convention of feature/radar_id or release/x.y.z or "
            f"bugfix/x.y.z/radar_id. Please refer to the Quip document (https://quip-apple.com/qPKhAbtbFwte) "
            f"for details"
        )
        return False
    return True


def main():
    if not is_valid_branch_name():
        sys.exit(1)


if __name__ == "__main__":
    main()
