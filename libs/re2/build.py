import os
import utils


def _build(config: utils.Config, srcPath: str, buildPath: str, installPath: str, buildConfig: str):
    args = [
        f"-Dabsl_DIR={config.dep('abseil').req(cmakeName='absl')}",
        "-DBUILD_TESTING=0",
        f"-DBUILD_SHARED_LIBS={config.shared.f(False).t(bool)}",
        "-DRE2_BUILD_FRAMEWORK=0",
        "-DRE2_BUILD_TESTING=0",
        "-DRE2_USE_ICU=0",
    ]

    utils.cmake(*args, "-S", srcPath, "-B", buildPath)
    utils.cmake("--build", buildPath, "--config", buildConfig)
    utils.cmake("--install", buildPath, "--config", buildConfig, "--prefix", installPath)


versions = {
    "2024.07.02": {
        "url": "https://github.com/google/re2/archive/refs/tags/2024-07-02.zip",
        "root": "re2-2024-07-02",
        "builder": _build,
    },
}


_libraryName = "re2"


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
