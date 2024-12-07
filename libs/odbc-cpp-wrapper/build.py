import os
import utils


def _build(srcPath: str, buildPath: str, installPath: str, buildConfig: str):
    utils.cmake("-S", srcPath, "-B", buildPath)
    utils.cmake("--build", buildPath, "--config", buildConfig)
    utils.cmake("--install", buildPath, "--config", buildConfig, "--prefix", installPath)


def _patchCmake_1_1(srcPath: str):
    utils.insertCMakeExportCommands(
        "odbccpp", os.path.join(srcPath, "src/odbc/CMakeLists.txt"),
        "odbccpp", "odbccpp_static")


versions = {
    "1.1": {
        "url": "https://github.com/SAP/odbc-cpp-wrapper/archive/refs/tags/v1.1.zip",
        "root": "odbc-cpp-wrapper-1.1",
        "builder": _build,
        "patch": _patchCmake_1_1,
    },
}


_libraryName = "odbc-cpp-wrapper"


def build():
    print(f"Build {_libraryName}")

    for version, variant, cfg in utils.loadLibraryConfig():
        try:
            versionConfig = versions[version]
            url = versionConfig["url"]
            if url is None:
                raise utils.BuildError("Invalid version")

            srcDirectory = os.path.join(
                utils.getOrDownloadSource(url, _libraryName, version), versionConfig["root"])

            if "patch" in versionConfig:
                versionConfig["patch"](srcDirectory)

            for buildConfig in cfg["config"]:
                print(f"Config: {buildConfig}")
                buildDirectoryPath = utils.getBuildDirectory(_libraryName, version, variant, buildConfig)
                installDirectoryPath = utils.getInstallDirectory(_libraryName, version, variant, buildConfig)
                versionConfig["builder"](srcDirectory,
                                         buildDirectoryPath,
                                         installDirectoryPath,
                                         buildConfig)

        except KeyError as e:
            raise utils.BuildError(f"KeyError. {e}")
