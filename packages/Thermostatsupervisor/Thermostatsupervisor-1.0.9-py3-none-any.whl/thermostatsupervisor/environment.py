"""Environment variable handling."""

# built-in libraries
import importlib.util
import io
import os
import platform
import socket
import sys
import traceback

# third party libraries
import psutil

# local imports
from thermostatsupervisor import utilities as util

# thermostat config files
from thermostatsupervisor import honeywell_config
from thermostatsupervisor import kumocloud_config
from thermostatsupervisor import kumolocal_config
from thermostatsupervisor import mmm_config
from thermostatsupervisor import sht31_config

MIN_PYTHON_MAJOR_VERSION = 3  # minimum python major version required
MIN_PYTHON_MINOR_VERSION = 7  # minimum python minor version required

# all environment variables required by code should be registered here
env_variables = {
    "GMAIL_USERNAME": None,
    "GMAIL_PASSWORD": None,
}
env_variables.update(honeywell_config.env_variables)
env_variables.update(kumocloud_config.env_variables)
env_variables.update(kumolocal_config.env_variables)
env_variables.update(mmm_config.env_variables)
env_variables.update(sht31_config.env_variables)


def get_env_variable(env_key):
    """
    Get environment variable.

    Results will be logged but passwords will be masked off.

    inputs:
       env_key(str): env variable of interest
       debug(bool): verbose debugging
    returns:
       (dict): {status, value, key}
    """
    # defaults
    return_buffer = {
        "status": util.NO_ERROR,
        "value": None,
        "key": env_key,
    }

    try:
        # unit test key is not required to be in env var list
        if env_key == sht31_config.UNIT_TEST_ENV_KEY:
            return_buffer["value"] = get_local_ip()
        else:
            return_buffer["value"] = os.environ[env_key]

        # mask off any password keys
        if "PASSWORD" in return_buffer["key"]:
            value_shown = "(hidden)"
        else:
            value_shown = return_buffer["value"]

        util.log_msg(f"{env_key}={value_shown}", mode=util.DEBUG_LOG)
    except KeyError:
        util.log_msg(
            f"FATAL ERROR: required environment variable '{env_key}'" " is missing.",
            mode=util.STDOUT_LOG + util.DATA_LOG,
        )
        return_buffer["status"] = util.ENVIRONMENT_ERROR
    return return_buffer


def set_env_variable(key, val):
    """
    Set environment variable.

    inputs:
        key(str): env var name
        val(str, int, bool): env value
    returns:
        None
    """
    if val is None:
        raise AttributeError("environment value cannot be none")
    if key is None:
        raise AttributeError("environment key cannot be none")
    elif not isinstance(key, str):
        raise AttributeError(
            f"environment key '{key}' must be a string, " f"is type {type(key)}"
        )
    os.environ[key] = str(val)


def load_all_env_variables():
    """
    Load all environment variables into a dictionary.

    inputs:
        None
    returns:
        None, populates env_variables dict.
    """
    for key in env_variables:
        util.log_msg(f"checking key: {key}", mode=util.BOTH_LOG, func_name=1)
        env_variables[key] = get_env_variable(key)["value"]


def is_interactive_environment():
    """Return True if script is run through IDE."""
    parent = psutil.Process(os.getpid()).parent().name()
    if parent in ["cmd.exe", "py.exe", "bash", "sphinx-build.exe"]:
        return False
    elif parent in ["eclipse.exe", "python.exe", "pycharm.exe"]:
        return True
    else:
        print(f"DEBUG: parent process={parent}")
        raise OSError(f"unrecognized environment: {parent}")


def get_local_ip():
    """Get local IP address for this PC."""
    socket_obj = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        socket_obj.connect(("10.255.255.255", 1))
        ip_address = socket_obj.getsockname()[0]
    except Exception:
        util.log_msg(traceback.format_exc(), mode=util.BOTH_LOG, func_name=1)
        ip_address = "127.0.0.1"
    finally:
        socket_obj.close()
    return ip_address


def is_azure_environment():
    """
    Return True if machine is Azure pipeline.

    Function assumes '192.' IP addresses are not Azure,
    everything else is Azure.
    """
    return "192." not in get_local_ip()


def is_windows_environment(verbose=False):
    """
    Return True if running on Windows PC.

    inputs:
        verbose(bool): debug flag.
    returns:
        (bool)
    """
    if verbose:
        print(f"platform={platform.system().upper()}")
    return "WINDOWS" in platform.system().upper()


def is_raspberrypi_environment(verbose=False):
    """
    Return True if running on Raspberry pi.

    inputs:
        verbose(bool): debug flag.
    returns:
        (bool)
    """
    try:
        with io.open("/sys/firmware/devicetree/base/model", "r", encoding="utf8") as m:
            if "raspberry pi" in m.read().lower():
                if verbose:
                    print("raspberry pi environment is detected")
                return True
    except Exception:  # noqa W703
        pass
    if verbose:
        print("raspberry pi environment is not detected")
    return False


def get_python_version(
    min_major_version=MIN_PYTHON_MAJOR_VERSION,
    min_minor_version=MIN_PYTHON_MINOR_VERSION,
    display_version=True,
):
    """
    Print current Python version to the screen.

    inputs:
        min_major_version(int): min allowed major version
        min_minor_version(int): min allowed minor version
        display_version(bool): True to print to screen.
    return:
        (tuple): (major version, minor version)
    """
    major_version = sys.version_info.major
    minor_version = sys.version_info.minor

    # display version
    if display_version:
        print(f"running on Python version {major_version}.{minor_version}")

    # check major version
    major_version_fail = False
    if min_major_version is not None:
        if not isinstance(min_major_version, (int, float)):
            raise TypeError(
                f"input parameter 'min_major_version is type "
                f"({type(min_major_version)}), not int or float"
            )
        if major_version < min_major_version:
            major_version_fail = True

    # check major version
    minor_version_fail = False
    if min_minor_version is not None:
        if not isinstance(min_minor_version, (int, float)):
            raise TypeError(
                f"input parameter 'min_minor_version is type "
                f"({type(min_minor_version)}), not int or float"
            )
        if minor_version < min_minor_version:
            minor_version_fail = True

    if major_version_fail or minor_version_fail:
        raise OSError(
            f"current python major version ({major_version}.{minor_version}) "
            f"is less than min python version required "
            f"({min_major_version}.{min_minor_version})"
        )

    return (major_version, minor_version)


def dynamic_module_import(name, path=None, pkg=None, verbose=False):
    """
    Find and load python module.

    TODO: this module results in a resource warning within unittest:
    sys:1: ResourceWarning: unclosed <socket.socket fd=628,
    family=AddressFamily.AF_INET, type=SocketKind.SOCK_DGRAM, proto=0,
    laddr=('0.0.0.0', 64963)>

    inputs:
        name(str): module name
        path(str): file path (either relative or abs path),
                   if path is None then will import from installed packages
        pkg(str): package to add to path
        verbose(bool): debug flag
    returns:
        mod(module): module object
    """
    # add package to path
    if pkg is not None:
        pkg_path = get_parent_path(os.getcwd()) + "//" + pkg
        print(f"adding package '{pkg_path}' to path...")
        # add to front(0) of path to ensure that package folder is prioritized over
        # local folder
        sys.path.insert(0, pkg_path)
        if verbose:
            print(f"sys.path={sys.path}")

    try:
        if path:
            # convert to abs path
            path = convert_to_absolute_path(path)

            # local file import from relative or abs path
            print(f"WARNING: attempting local import of {name} from " f"path {path}...")
            if verbose:
                print(f"target dir contents={os.listdir(path)}")
                print(f"adding '{path}' to system path")
            sys.path.insert(1, path)
            mod = importlib.import_module(name)
            if mod is None:
                raise ModuleNotFoundError(
                    f"module '{name}' could not " f"be found at {path}"
                )
        else:
            # installed package import
            spec = importlib.util.find_spec(name, path)
            if spec is None:
                raise ModuleNotFoundError(f"module '{name}' could not be found")
            mod = importlib.util.module_from_spec(spec)
            sys.modules[name] = mod
            spec.loader.exec_module(mod)
    except Exception as ex:
        util.log_msg(traceback.format_exc(), mode=util.BOTH_LOG, func_name=1)
        util.log_msg("module load failed: " + name, mode=util.BOTH_LOG, func_name=1)
        raise ex
    else:
        show_package_version(mod)
        return mod


def convert_to_absolute_path(relative_path):
    """
    Convert a relative path to an absolute path.

    inputs:
        relative_path(str): relative path
    returns:
        (str): absolute path
    """
    if not isinstance(relative_path, str):
        raise TypeError("relative_path must be a string")
    return os.path.abspath(relative_path).replace("\\", "/")


def get_parent_path(source_path, verbose=False):
    """
    Return the absolute path to the parent folder.

    inputs:
        source_path(str): source path
        verbose(bool): prints debug data.
    returns:
        (str): abs path to parent folder.
    """
    parent_path = os.path.abspath(os.path.join(source_path, os.pardir)).replace(
        "\\", "/"
    )
    if verbose:
        print(f"parent path={parent_path}")
    return parent_path


def get_package_version(module, element=None, verbose=False):
    """
    Get the package version for an installed package.

    inputs:
        module(obj): imported module
        element(str): element, if None will return the entire package
        verbose(bool): debug flag
    returns:
        (tuple) of ints if element is None, else returns int.
    """
    # cast lowercase if string
    if isinstance(element, str):
        element = element.lower()

    # trim off any dev suffixes from module version
    try:
        module_version = ".".join(module.__version__.split(".")[:3])
    except AttributeError:
        # __version__ attribute not available for pkg use dummy verison.
        module_version = "0.0.0"

    # parse the version string into a tuple of ints
    ver_tuple = tuple(map(int, module_version.split(".")))
    if verbose:
        print(f"{module} element {element} package version={ver_tuple}")
    if element is None:
        return_val = ver_tuple
    elif element in ["major", 0]:
        return_val = ver_tuple[0]
    elif element in ["minor", 1]:
        return_val = ver_tuple[1]
    elif element in ["patch", 2]:
        try:
            return_val = ver_tuple[2]
        except IndexError:
            return_val = 0
    else:
        raise AttributeError(f"{element} is not a valid choice for element input")
    return return_val


def show_package_version(module):
    """
    Display the current package version.

    inputs:
        module(obj): imported module.
    returns:
        (None): displays package version to stdio.
    """
    pkg_path = get_package_path(module).replace("\\", "/")
    pkg_version = get_package_version(module)
    pkg_version_str = ".".join(tuple(map(str, pkg_version)))
    print(f"'{module.__name__}' version {pkg_version_str} installed from {pkg_path}")


def get_package_path(module):
    """
    Get the path to the installed package.

    inputs:
        module(obj): imported module.
    returns:
        (str): path to installed package.
    """
    return module.__dict__["__file__"]
