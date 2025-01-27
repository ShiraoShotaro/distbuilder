import os
import utils


def _build(config: utils.Config, srcPath: str, buildPath: str, installPath: str, buildConfig: str):
    args = [
        "-DSOCKPP_BUILD_CAN=0",
        "-DSOCKPP_BUILD_DOCUMENTATION=0",
        "-DSOCKPP_BUILD_EXAMPLES=0",
        f"-DSOCKPP_BUILD_SHARED={config.shared.f(False).t(bool)}",
        f"-DSOCKPP_BUILD_STATIC={not config.shared.f(True).t(bool)}",
        "-DSOCKPP_BUILD_TESTS=0"
    ]

    utils.cmakeConfigure(srcPath, buildPath, *args)
    utils.cmakeBuildAndInstall(buildPath, buildConfig, installPath)


versions = {
    "1.0.0": {
        "url": "https://github.com/fpagliughi/sockpp/archive/refs/tags/v1.0.0.zip",
        "root": "sockpp-1.0.0",
        "builder": _build,
    },
}


_libraryName = "sockpp"


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
