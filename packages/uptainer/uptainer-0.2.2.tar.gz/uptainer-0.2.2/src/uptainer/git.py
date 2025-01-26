from structlog._config import BoundLoggerLazyProxy
from uptainer.typer import TyperGenericReturn
import tempfile
import git


class Git:
    def __init__(self, log: BoundLoggerLazyProxy, remote_url: str, branch: str, ssh_private_key: str) -> None:
        """Wrapper for all git function like clone, push, etc.

        Args:
            log (BoundLoggerLazyProxy): Log class to inject into the vars. Class: structlog
            remote_url (str): Remote git url, that needs to starts with ssh:// or git@
            branch (str): Working git branch to use.
            ssh_private_key (str): Private key to use for pull and push data

        Returns:
            None
        """
        self.private_key = ssh_private_key
        self.work_directory = None
        self.remote_url = remote_url
        self.branch = branch
        self.log = log

    def create_workdir(self) -> str:
        """Create a working directory under TMPDIR (platform based) and set it as workdir.

        Args:
            None

        Returns:
            Work Directory path created (str)
        """
        obj = tempfile.TemporaryDirectory()
        self.work_directory = obj.name
        self.log.info(f"The current working directory is: {obj.name}")
        return obj.name

    def push_repo(self, fpath: str, newversion: str) -> TyperGenericReturn:
        """Push the new changes into git.

        Args:
            fpath (str): RELATIVE path of the file to push.
            newversion (str): New version to apply, needed for the commit msg.

        Returns:
            TyperGenericReturn Object
        """
        out = TyperGenericReturn(error=False)
        commit_msg = f"chore: Update version to {newversion}"
        try:
            repo = git.Repo(self.work_directory)
            # Inject ssh key
            repo.git.custom_environment(GIT_SSH_COMMAND=f"ssh -i {self.private_key}")
            if repo.is_dirty():
                self.log.info(f"Pushing the new version with the commit msg: '{commit_msg}'")
                repo.index.add([fpath])
                repo.index.commit(commit_msg)
                repo.remotes.origin.push()
            else:
                self.log.info("No changes to push.")
        # TODO: Adding more catch strategy
        except Exception as error:
            self.log.error(f"Error: {error}")
            out["error"] = True
        return out

    def clone_repo(self) -> TyperGenericReturn:
        """Clone the repo provided in the temporary dir and switch to the branch.

        Args:
            None

        Returns:
            Return a dict that contain a boolean value for the errors.
        """
        out = TyperGenericReturn(error=False)
        if self.remote_url.startswith("git@") or self.remote_url.startswith("ssh://"):
            git_env = {"GIT_SSH_COMMAND": f"ssh -i {self.private_key}"}
            self.log.info(f"Pulling '{self.remote_url}' to '{self.work_directory}' using the key '{self.private_key}'")
            try:
                self.repo = git.Repo.clone_from(url=self.remote_url, to_path=self.work_directory, env=git_env)
                self.log.info(f"Pull success. Switching to the branch '{self.branch}'")
                self.repo.git.checkout(self.branch)
            # TODO: Adding more catch strategy
            except git.exc.GitCommandError as error:
                self.log.error(f"Error during pulling the repo, error: '{error}'")
                out["error"] = True
        else:
            self.log.error("Uptainer currently support clone only via SSH. Exiting.")
            out["error"] = True
        return out
