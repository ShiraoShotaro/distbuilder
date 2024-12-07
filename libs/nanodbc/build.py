import os
import utils


def _build(config, srcPath: str, buildPath: str, installPath: str, buildConfig: str):
    args = [
        f"-DBUILD_SHARED_LIBS={config['shared']}",
        "-DNANODBC_DISABLE_EXAMPLES=1",
        "-DNANODBC_DISABLE_INSTALL=0",
        "-DNANODBC_DISABLE_LIBCXX=0",
        "-DNANODBC_DISABLE_TESTS=1",
        "-DNANODBC_ENABLE_BOOST=0",
        "-DNANODBC_ENABLE_COVERAGE=0",
        "-DNANODBC_ENABLE_UNICODE=1",
        "-DNANODBC_ENABLE_WORKAROUND_NODATA=1",
    ]
    utils.cmake(*args, "-S", srcPath, "-B", buildPath)
    utils.cmake("--build", buildPath, "--config", buildConfig)
    utils.cmake("--install", buildPath, "--config", buildConfig, "--prefix", installPath)


versions = {
    "2.14.0": {
        "url": "https://github.com/nanodbc/nanodbc/archive/refs/tags/v2.14.0.zip",
        "root": "nanodbc-2.14.0",
        "builder": _build,
    },
}


_libraryName = "nanodbc"


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
