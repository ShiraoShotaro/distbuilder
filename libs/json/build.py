import os
import utils


def _build(config, srcPath: str, buildPath: str, installPath: str, buildConfig: str):
    args = [
        "-DJSON_BuildTests=0",
        "-DJSON_CI=0",
        "-DJSON_DisableEnumSerialization=0",
        "-DJSON_GlobalUDLs=0",
        "-DJSON_ImplicitConversions=1",
        "-DJSON_Install=1",
        "-DJSON_LegacyDiscardedValueComparison=0",
        "-DJSON_MultipleHeaders=1",
        "-DJSON_SystemInclude=0",
    ]
    utils.cmake(*args, "-S", srcPath, "-B", buildPath)
    utils.cmake("--build", buildPath, "--config", buildConfig)
    utils.cmake("--install", buildPath, "--config", buildConfig, "--prefix", installPath)


versions = {
    "3.11.3": {
        "url": "https://github.com/nlohmann/json/archive/refs/tags/v3.11.3.zip",
        "root": "json-3.11.3",
        "builder": _build,
    },
}


_libraryName = "json"


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

            for buildConfig in cfg["config"]:
                print(f"Config: {buildConfig}")
                buildDirectoryPath = utils.getBuildDirectory(_libraryName, version, variant, buildConfig)
                installDirectoryPath = utils.getInstallDirectory(_libraryName, version, variant, buildConfig)
                versionConfig["builder"](cfg,
                                         srcDirectory,
                                         buildDirectoryPath,
                                         installDirectoryPath,
                                         buildConfig)

        except KeyError as e:
            raise utils.BuildError(f"KeyError. {e}")
