import os
import utils


def _build(config: utils.Config, srcPath: str, buildPath: str, installPath: str, buildConfig: str):
    args = [
        "-DBUILD_TESTING=0",
        f"-DABSL_BUILD_MONOLITHIC_SHARED_LIBS={config.shared.f(False).t(bool)}",
        "-DABSL_BUILD_TESTING=0",
        "-DABSL_BUILD_TEST_HELPERS=0",
        "-DABSL_ENABLE_INSTALL=1",
        "-DABSL_MSVC_STATIC_RUNTIME=0",  # Use MD
        "-DABSL_USE_SYSTEM_INCLUDES=0",
    ]

    utils.cmake(*args, "-S", srcPath, "-B", buildPath)
    utils.cmake("--build", buildPath, "--config", buildConfig)
    utils.cmake("--install", buildPath, "--config", buildConfig, "--prefix", installPath)


versions = {
    "20240722.0": {
        "url": "https://github.com/abseil/abseil-cpp/archive/refs/tags/20240722.0.zip",
        "root": "abseil-cpp-20240722.0",
        "builder": _build,
    },
}


_libraryName = "abseil"


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
