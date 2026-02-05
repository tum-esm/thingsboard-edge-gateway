"""Git repository access utilities for the Edge Gateway controller.

This module provides the :class:`GatewayGitClient`, a lightweight wrapper around
the local Git repository of the Edge Gateway controller.

It is primarily used during controller software updates (e.g. OTA updates) to
resolve version identifiers, fetch updates from the remote repository, and reset
the working tree to a specific Git tag or commit hash.

Responsibilities
----------------
- Resolve Git tags to commit hashes.
- Verify the existence of commit hashes or tags.
- Query the currently checked-out commit.
- Fetch updates from the remote repository.
- Reset the controller repository to a specific commit in a reproducible way.

Notes
-----
- All Git commands are executed via subprocess calls.
- The client operates on the controller repository path defined by
  ``CONTROLLER_GIT_PATH``.
- The class is implemented as a singleton to avoid repeated initialization.
"""

import subprocess
from modules.logging import debug, error
from os.path import dirname
from typing import Optional, Any

from utils.paths import CONTROLLER_GIT_PATH

singleton_instance: Optional["GatewayGitClient"] = None

class GatewayGitClient:
    """Access and manage the local controller Git repository.

    This class encapsulates all Git interactions required by the Edge Gateway to
    manage controller versions during updates. It provides helper methods to resolve
    tags, validate commit hashes, and safely reset the repository state.

    The class follows a singleton pattern to ensure that Git operations are
    coordinated across the gateway process.
    """
    def __init__(self):
        global singleton_instance
        if singleton_instance is None:
            debug("[GIT-CLIENT] Initializing GatewayGitClient")
            super().__init__()
            singleton_instance = self

    # Singleton pattern
    def __new__(cls: Any) -> "GatewayGitClient":
        global singleton_instance
        if singleton_instance is not None:
            return singleton_instance
        return super(GatewayGitClient, cls).__new__(cls)

    def get_commit_from_hash_or_tag(self, hash_or_tag: str) -> Optional[str]:
        """Resolve a Git tag or commit hash to a commit hash.

        Args:
          hash_or_tag: Git tag name or commit hash.

        Returns:
          Commit hash if resolvable, otherwise ``None``.
        """
        commit_for_tag = self.get_commit_for_tag(hash_or_tag)
        if commit_for_tag is not None:
            return commit_for_tag
        elif self.verify_commit_hash_or_tag_exists(hash_or_tag):
            return hash_or_tag
        else:
            return None

    def get_current_commit(self) -> Optional[str]:
        """Return the currently checked-out Git commit.

        Returns:
          Commit hash string, or ``None`` if it cannot be determined.
        """
        try:
            return subprocess.check_output(["git", "rev-parse", "HEAD"], encoding='utf-8', cwd=dirname(CONTROLLER_GIT_PATH)).strip()
        except subprocess.CalledProcessError as e:
            error(f"[GIT-CLIENT] Unable to determine current commit hash: : {e} {e.stderr} {e.stdout}")
            return None

    def get_commit_for_tag(self, tag) -> Optional[str]:
        """Return the commit hash associated with a Git tag.

        Args:
          tag: Git tag name.

        Returns:
          Commit hash for the tag, or ``None`` if the tag does not exist.
        """
        try:
            return subprocess.check_output(["git", "rev-list", "-n 1", "tags/" + tag], encoding='utf-8', cwd=dirname(CONTROLLER_GIT_PATH)).strip()
        except subprocess.CalledProcessError as e:
            error(f"[GIT-CLIENT] Unable to find commit hash for tag '{tag}': {e} {e.stderr} {e.stdout}")
            return None

    def verify_commit_hash_or_tag_exists(self, commit_hash: str) -> bool:
        """Verify that a commit hash or tag exists in the repository.

        Args:
          commit_hash: Commit hash or tag to verify.

        Returns:
          ``True`` if the reference exists and points to a commit, otherwise ``False``.
        """
        try:
            return (subprocess.check_output(["git", "cat-file", "-t", commit_hash], cwd=dirname(CONTROLLER_GIT_PATH))
                    .strip() == b'commit')
        except subprocess.CalledProcessError as e:
            error(f"[GIT-CLIENT] Unable to verify commit hash: {e} {e.stderr} {e.stdout}")
            return False

    def execute_reset_to_commit(self, commit_hash: str) -> bool:
        """Reset the controller repository to a specific commit.

        This performs a forced checkout, hard reset, and clean to ensure a reproducible
        repository state.

        Args:
          commit_hash: Commit hash to reset to.

        Returns:
          ``True`` if the reset succeeded, otherwise ``False``.
        """
        try:
            if subprocess.run(["git", "checkout", "-f", commit_hash], cwd=dirname(CONTROLLER_GIT_PATH)).returncode == 0\
                and subprocess.run(["git", "reset", "HEAD", "--hard"], cwd=dirname(CONTROLLER_GIT_PATH)).returncode == 0\
                and subprocess.run(["git", "clean", "-f", "-d"], cwd=dirname(CONTROLLER_GIT_PATH)).returncode == 0:
                return True
        except subprocess.CalledProcessError as e:
            error(f"[GIT-CLIENT] Unable to reset to commit hash: {e} {e.stderr} {e.stdout}")
        return False

    def execute_fetch(self) -> bool:
        """Fetch updates from the remote Git repository.

        Returns:
          ``True`` if the fetch operation succeeded, otherwise ``False``.
        """
        try:
            if subprocess.run(["git", "fetch"], cwd=dirname(CONTROLLER_GIT_PATH)).returncode == 0:
                return True
        except subprocess.CalledProcessError as e:
            error(f"[GIT-CLIENT] Unable to fetch from remote: {e} {e.stderr} {e.stdout}")
        return False
