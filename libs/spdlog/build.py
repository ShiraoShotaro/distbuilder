import os
import utils


def _build(config, srcPath: str, buildPath: str, installPath: str, buildConfig: str):
    # HO = header only
    args = [
        f"-DSPDLOG_BUILD_SHARED={config['shared']}",
        "-DSPDLOG_BUILD_EXAMPLE=0",
        "-DSPDLOG_BUILD_EXAMPLE_HO=0",
        "-DSPDLOG_BUILD_PIC=0",
        "-DSPDLOG_BUILD_TESTS=0",
        "-DSPDLOG_BUILD_TESTS_HO=0",
        "-DSPDLOG_BUILD_WARNINGS=0",
        f"-DSPDLOG_DISABLE_DEFAULT_LOGGER={config['disableDefaultLogger']}",
        "-DSPDLOG_INSTALL=1",
        "-DSPDLOG_MSVC_UTF8=1",
        "-DSPDLOG_FMT_EXTERNAL_HO=0",
    ]
    if config['useStdFormat'] is True:
        args.append(f"-DSPDLOG_USE_STD_FORMAT={config['useStdFormat']}")
    else:
        args.append(f"-DSPDLOG_FMT_EXTERNAL={config['fmtExternal']}")

    utils.cmake(*args, "-S", srcPath, "-B", buildPath)
    utils.cmake("--build", buildPath, "--config", buildConfig)
    utils.cmake("--install", buildPath, "--config", buildConfig, "--prefix", installPath)


versions = {
    "1.15.0": {
        "url": "https://github.com/gabime/spdlog/archive/refs/tags/v1.15.0.zip",
        "root": "spdlog-1.15.0",
        "builder": _build,
    },
}


_libraryName = "spdlog"


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
