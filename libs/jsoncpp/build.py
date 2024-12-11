import os
import utils


def _build(config: utils.Config, srcPath: str, buildPath: str, installPath: str, buildConfig: str):
    args = [
        "-DBUILD_OBJECT_LIBS=1",
        f"-DBUILD_SHARED_LIBS={config.shared.f(False).t(bool)}",
        f"-DBUILD_STATIC_LIBS={config.shared.f(True).t(bool)}",
        "-DJSONCPP_STATIC_WINDOWS_RUNTIME=0",  # Use MD
        "-DJSONCPP_WITH_CMAKE_PACKAGE=1",
        "-DJSONCPP_WITH_EXAMPLE=0",
        "-DJSONCPP_WITH_PKGCONFIG_SUPPORT=0",
        "-DJSONCPP_WITH_POST_BUILD_UNITTEST=0",
        "-DJSONCPP_WITH_STRICT_ISO=1",
        "-DJSONCPP_WITH_TESTS=0",
        "-DJSONCPP_WITH_WARNING_AS_ERROR=1",
    ]

    utils.cmake(*args, "-S", srcPath, "-B", buildPath)
    utils.cmake("--build", buildPath, "--config", buildConfig)
    utils.cmake("--install", buildPath, "--config", buildConfig, "--prefix", installPath)


versions = {
    "1.9.6": {
        "url": "https://github.com/open-source-parsers/jsoncpp/archive/refs/tags/1.9.6.zip",
        "root": "jsoncpp-1.9.6",
        "builder": _build,
    },
}


_libraryName = "jsoncpp"


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
