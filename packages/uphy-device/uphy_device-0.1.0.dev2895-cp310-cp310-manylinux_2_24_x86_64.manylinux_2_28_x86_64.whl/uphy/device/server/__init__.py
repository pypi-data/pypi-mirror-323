import importlib.resources
import logging
from pathlib import Path
import subprocess
import sys

if sys.platform == "win32":
    server_name = "server.exe"
else:
    server_name = "server"

LOGGER = logging.getLogger(__name__)


def server_binary() -> Path:
    with importlib.resources.as_file(importlib.resources.files(__name__)) as base:
        if (path := base / "bin" / server_name).exists():
            log_setcap_info(path)
            return path

        raise Exception("Can't find server binary")


def log_setcap_info(server: str):
    capabilities = "cap_net_raw,cap_net_admin,cap_net_bind_service+ep"
    try:
        subprocess.check_output(["setcap", "-v", capabilities, server])
    except subprocess.CalledProcessError:
        LOGGER.error(
            "You need to allow raw sockets for server to function. Run the following command:\n"
            "sudo setcap %s %s",
            capabilities,
            server,
        )
        exit(-1)
    except FileNotFoundError:
        # System does not support setcap, could be widows for example
        pass
