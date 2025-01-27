import os
import subprocess
import contextlib
from contextlib import ExitStack


LOCAL_WORKSPACE_FILE_NAMES = [".dvimws.lua", ".dvimws.yaml", ".dvimws.json"]
WORKSPACE_FILE_ENV = "DVIM_NEOVIM_WORSPACE_FILE"
SESSION_NAME_ENV = "DVIM_NEOVIM_SESSION_NAME"
GLOBAL_WORKSPACES_DIR = os.path.expanduser("~/.config/nvim/workspaces")
SESSIONS_DIR = os.path.expanduser("~/.local/share/nvim/sessions")
SOCKETS_DIR = os.path.expanduser("~/.cache/nvim/pipes")


class Runner:
    def __init__(self, debug, executable, workspace, session):
        self.debug = debug
        self.executable = executable
        self.workspace = get_workspace_file_path(workspace)
        self.session = session

    def attach(self, args):
        self._execute(["--remote-ui", *args])

    def send(self, args):
        self._execute(["--remote-send", *args])

    def remote(self, args):
        self._execute(["--remote", *args])

    def _execute(self, args):
        socket_path = find_running_instance_socket_path(self.build_socket_prefix())
        check_socket_exists(socket_path)
        self._run_nvim("--server", socket_path, *args)

    def server(self, args):
        with ExitStack() as stack:
            socket_path = self.build_socket_path()
            stack.callback(lambda: cleanup_socket(socket_path))

            check_socket_does_not_exist(socket_path)
            self._run_nvim("--listen", socket_path, *args)

    def headless(self, args):
        with ExitStack() as stack:
            socket_path = self.build_socket_path()
            stack.callback(lambda: cleanup_socket(socket_path))

            check_socket_does_not_exist(socket_path)
            self._run_nvim("--headless", "--listen", socket_path, *args)

    def local(self, args):
        self._run_nvim(*args)

    def _run_nvim(self, *nvim_args):
        extra_env = dict()

        if self.workspace is not None:
            extra_env[WORKSPACE_FILE_ENV] = self.workspace

        if self.session is not None:
            extra_env[SESSION_NAME_ENV] = self.session

        run(
            [
                self.executable,
                *nvim_args,
            ],
            extra_env,
            self.debug,
        )

    def build_socket_prefix(self):
        return f"{self.workspace or ''}"

    def build_socket_path(self):
        return os.path.join(SOCKETS_DIR, f"{self.workspace or ''}.server.pipe")


def get_workspace_file_path(provided_workspace):
    if provided_workspace is None:
        return None

    provided_workspace = os.path.expanduser(provided_workspace)

    if os.path.isfile(provided_workspace):
        return provided_workspace

    if os.path.isdir(provided_workspace):
        cur_dir = os.path.abspath(provided_workspace)

        while True:
            file_list = os.listdir(cur_dir)
            parent_dir = os.path.dirname(cur_dir)

            for local_name in LOCAL_WORKSPACE_FILE_NAMES:
                if local_name in file_list:
                    return os.path.join(cur_dir, local_name)

            if cur_dir == parent_dir:
                break

            cur_dir = parent_dir

    return None


def cleanup_socket(socket_path):
    with contextlib.suppress(FileNotFoundError):
        os.remove(socket_path)


def run(cmd, extra_env, debug):
    if debug:
        print(extra_env, cmd)
    else:
        extra_env.update(dict(os.environ))
        subprocess.run(cmd, env=extra_env)


def find_running_instance_socket_path(socket_prefix):
    sockets = [
        os.path.join(SOCKETS_DIR, path)
        for path in os.listdir(SOCKETS_DIR)
        if path.startswith(socket_prefix)
    ]

    if not sockets:
        raise RuntimeError("Failed to find a running server")
    elif len(sockets) == 1:
        return sockets[0]
    else:
        return choose_one_of(sockets)


def choose_one_of(items):
    import inquirer

    answers = (
        inquirer.prompt(
            [
                inquirer.List(
                    "chosen",
                    message="Choose the running instance",
                    choices=items,
                ),
            ]
        )
        or {}
    )

    return answers["chosen"]


def check_socket_exists(socket_path):
    if not os.path.exists(socket_path):
        raise RuntimeError(f"socket does not exist on {socket_path}")


def check_socket_does_not_exist(socket_path):
    if os.path.exists(socket_path):
        raise RuntimeError(f"socket already exists on {socket_path}")
