import os
import subprocess
import toml
import shutil
import glob
import stat


class BuildError(RuntimeError):
    def __init__(self, message: str):
        super().__init__(message)


_globalConfig: dict = None


def loadGlobalConfig(path=None):
    global _globalConfig
    if path is None:
        tomlPath = os.path.join(os.path.dirname(__file__), "config.toml")
    else:
        tomlPath = os.path.abspath(path)

    with open(tomlPath, mode="r", encoding="utf-8") as fp:
        _globalConfig = toml.load(fp)


def getGlobalConfig() -> dict:
    return _globalConfig.copy()


def loadLibraryConfig():
    import inspect
    try:
        with open(os.path.join(os.path.dirname(inspect.stack()[1].filename), "config.toml"),
                  mode="r", encoding="utf-8") as fp:
            data = toml.load(fp)
        # (version, variant, config) に展開する
        ret = list()
        for version, variants in data.items():
            for variant, cfg in variants.items():
                ret.append((version, variant, cfg))
        return ret
    except Exception as e:
        raise BuildError(f"Failed to load library config. {e}")


def cleanCache():
    print("!!! Clean Cache !!!")
    if os.path.exists(_globalConfig["directories"]["build"]):
        shutil.rmtree(_globalConfig["directories"]["build"])
    print("-- OK.")


def recreateDirectory(rootPath: str):
    if os.path.exists(rootPath):
        for root, _, files in os.walk(rootPath):
            for filename in files:
                fullpath = os.path.join(root, filename)
                if not os.access(fullpath, os.W_OK):
                    os.chmod(fullpath, stat.S_IWRITE)
        shutil.rmtree(rootPath)
    os.makedirs(rootPath)


def getOrDownloadSource(url: str, libraryName: str, version: str) -> str:
    import urllib.error
    import urllib.request
    print(f"getOrDownloadSource(), {libraryName}@{version}, {url}")
    libraryBuildDirectory = os.path.join(
        _globalConfig["directories"]["build"], libraryName, version)
    os.makedirs(libraryBuildDirectory, exist_ok=True)

    zipFilepath = os.path.join(libraryBuildDirectory, "src.zip")
    unzipDirpath = os.path.join(libraryBuildDirectory, "src")
    if not os.path.exists(zipFilepath):
        print(f"-- Downloading, destination = {zipFilepath}")
        try:
            urllib.request.urlretrieve(url, zipFilepath)
        except urllib.error.HTTPError as e:
            raise BuildError(f"Failed to download source. {e}")

        print(f"-- Unzipping, destination = {unzipDirpath}")
        shutil.unpack_archive(zipFilepath, unzipDirpath)

    else:
        print("-- Cached.")
    return unzipDirpath


def getBuildDirectory(libraryName: str, version: str, variant: str, buildConfig: str):
    print(f"getBuildDirectory(), {libraryName}@{version}/{variant}/{buildConfig}")
    buildDirectory = os.path.join(
        _globalConfig["directories"]["build"], libraryName, version,
        "build", variant)
    if buildConfig:
        buildDirectory = os.path.join(buildDirectory, buildConfig)
    recreateDirectory(buildDirectory)
    os.makedirs(buildDirectory, exist_ok=True)
    print(f"-- build directory: {buildDirectory}")
    return buildDirectory


def cmake(*args):
    args = [_globalConfig["cmake"]["path"]] + [str(arg) for arg in args]
    print("> {}".format(" ".join(args)))
    if subprocess.run(args).returncode != 0:
        raise BuildError("Failed to cmake.")


def getInstallDirectory(libraryName: str, version: str, variant: str, buildConfig: str):
    print(f"getInstallDirectory(), {libraryName}@{version}/{variant}/{buildConfig}")
    installDirectory = os.path.join(_globalConfig["directories"]["install"],
                                    libraryName, version, variant)
    if buildConfig:
        installDirectory = os.path.join(installDirectory, buildConfig)
    recreateDirectory(installDirectory)
    print(f"-- install directory: {installDirectory}")
    return installDirectory


def searchLibrary(config: dict, libraryName: str, buildConfig: str):
    version, variant = config.get("deps", dict())[libraryName].split("/", 1)
    print(f"searchPackage(), {libraryName}@{version}/{variant}/{buildConfig}")
    installDirectory = os.path.join(_globalConfig["directories"]["install"],
                                    libraryName, version, variant)
    if buildConfig:
        installDirectory = os.path.join(installDirectory, buildConfig)
    if not os.path.exists(installDirectory):
        raise BuildError(f"Library '{libraryName}' is not found.")
    # cmake を探す
    candidates = glob.glob(os.path.join(installDirectory, "**/*.cmake"), recursive=True)
    candidates = [(fp, os.path.basename(fp).lower()) for fp in candidates]
    for fp, fn in candidates:
        print(f"-- search: {fp}")
        if fn.endswith("config.cmake") and fn.startswith(libraryName.lower()):
            print(f"Library '{libraryName}' is found. {os.path.dirname(fp)}")
            return os.path.dirname(fp)
    raise BuildError(f"Library '{libraryName}' cmake file is not found.")
