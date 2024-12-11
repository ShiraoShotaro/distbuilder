import os
import utils


def _build(config, srcPath: str, buildPath: str, installPath: str, buildConfig: str):
    args = [
        f"-DCARES_STATIC={not config['shared']}",
        f"-DCARES_SHARED={config['shared']}",
        "-DCARES_INSTALL=1",
        "-DCARES_STATIC_PIC=0",
        "-DCARES_BUILD_TESTS=0",
        "-DCARES_BUILD_CONTAINER_TESTS=0",
        "-DCARES_BUILD_TOOLS=0",
        "-DCARES_SYMBOL_HIDING=1",  # Default is off
        "-DCARES_THREADS=1",
        "-DCARES_MSVC_STATIC_RUNTIME=0",  # MD
    ]

    utils.cmake(*args, "-S", srcPath, "-B", buildPath)
    utils.cmake("--build", buildPath, "--config", buildConfig)
    utils.cmake("--install", buildPath, "--config", buildConfig, "--prefix", installPath)


versions = {
    "1.34.3": {
        "url": "https://github.com/c-ares/c-ares/archive/refs/tags/v1.34.3.zip",
        "root": "c-ares-1.34.3",
        "builder": _build,
    },
}


_libraryName = "c-ares"


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
