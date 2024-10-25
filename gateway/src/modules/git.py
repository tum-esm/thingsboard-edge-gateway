import subprocess


class GatewayGitClient:
    def __init__(self):
        self.git_repo_path = "./.git"

    def get_current_commit(self):
        try:
            return subprocess.check_output("git --git-dir='" + self.git_repo_path + "' rev-parse HEAD", shell=True)
        except subprocess.CalledProcessError as e:
            print("[GIT-CLIENT] Unable to determine current commit hash: ", e)
            return None

    def get_commit_for_tag(self, tag):
        try:
            return subprocess.check_output("git --git-dir='" + self.git_repo_path + "' rev-list -n 1 tags/" + tag,
                                           shell=True)
        except subprocess.CalledProcessError as e:
            print("[GIT-CLIENT] Unable to find commit hash for tag '" + tag + "': ", e)
            return None

    def verify_commit_hash(self, commit_hash):
        try:
            return (subprocess.check_output("git --git-dir='" + self.git_repo_path + "' cat-file -t " + commit_hash, shell=True)
                    .strip() == b'commit')
        except subprocess.CalledProcessError as e:
            print("[GIT-CLIENT] Unable to verify commit hash: ", e)
            return None

    def execute_reset_to_commit(self, commit_hash):
        try:
            if subprocess.run("git --git-dir='" + self.git_repo_path + "' reset --hard " + commit_hash).returncode == 0:
                return True
        except subprocess.CalledProcessError as e:
            print("[GIT-CLIENT] Unable to reset to commit hash: ", e)
            return None
        return None

    def execute_fetch(self):
        try:
            return subprocess.check_output("git --git-dir='" + self.git_repo_path + "' fetch", shell=True)
        except subprocess.CalledProcessError as e:
            print("[GIT-CLIENT] Unable to fetch from remote: ", e)
            return None
