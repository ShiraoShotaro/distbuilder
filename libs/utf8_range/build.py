import os
import utils


def _build(config: utils.Config, srcPath: str, buildPath: str, installPath: str, buildConfig: str):
    args = [
        f"-Dabsl_DIR={config.dep('abseil').req(cmakeName='absl')}",
        "-Dutf8_range_ENABLE_INSTALL=1",
        "-Dutf8_range_ENABLE_TESTS=0",
    ]

    utils.cmake(*args, "-S", srcPath, "-B", buildPath)
    utils.cmake("--build", buildPath, "--config", buildConfig)
    utils.cmake("--install", buildPath, "--config", buildConfig, "--prefix", installPath)


versions = {
    "0": {
        "url": "https://github.com/protocolbuffers/utf8_range/archive/1d1ea7e3fedf482d4a12b473c1ed25fe0f371a45.zip",
        "root": "utf8_range-1d1ea7e3fedf482d4a12b473c1ed25fe0f371a45",
        "builder": _build,
    },
}


_libraryName = "utf8_range"


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
                cfgutil = utils.Config(cfg, buildConfig)
                buildDirectoryPath = utils.getBuildDirectory(_libraryName, version, variant, buildConfig)
                installDirectoryPath = utils.getInstallDirectory(_libraryName, version, variant, buildConfig)
                versionConfig["builder"](cfgutil,
                                         srcDirectory,
                                         buildDirectoryPath,
                                         installDirectoryPath,
                                         buildConfig)

        except KeyError as e:
            raise utils.BuildError(f"KeyError. {e}")
