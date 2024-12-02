import os
import subprocess
import toml
import shutil


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
            return toml.load(fp)
    except Exception as e:
        raise BuildError(f"Failed to load library config. {e}")


def cleanCache():
    print("!!! Clean Cache !!!")
    if os.path.exists(_globalConfig["directories"]["build"]):
        shutil.rmtree(_globalConfig["directories"]["build"])
    print("-- OK.")


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
        "build", variant, buildConfig)
    if os.path.exists(buildDirectory):
        shutil.rmtree(buildDirectory)
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
    installDirectory = os.path.join(
        _globalConfig["directories"]["install"], libraryName, version, variant, buildConfig)
    if os.path.exists(installDirectory):
        shutil.rmtree(installDirectory)
    os.makedirs(installDirectory, exist_ok=True)
    print(f"-- install directory: {installDirectory}")
    return installDirectory
