import os
import utils


def _build(config: utils.Config, srcPath: str, buildPath: str, installPath: str, buildConfig: str):
    args = [
        "-DLIBUSB_BUILD_EXAMPLES=0",
        "-DLIBUSB_BUILD_TESTING=0",
        "-DLIBUSB_INSTALL_TARGETS=1",
        f"-DLIBUSB_BUILD_SHARED_LIBS={config.shared.f(False).t(bool)}",
        f"-DLIBUSB_ENABLE_LOGGING={config.logging.f(False).t(bool)}",
        f"-DLIBUSB_ENABLE_DEBUG_LOGGING={config.debugLogging.f(False).t(bool)}",
        f"-DLIBUSB_TARGETS_INCLUDE_USING_SYSTEM={config.targetsIncludeUsingSystem.f(False).t(bool)}",
        "-DCMAKE_C_FLAGS=/utf-8",
    ]

    utils.cmakeConfigure(srcPath, buildPath, *args)
    utils.cmakeBuildAndInstall(buildPath, buildConfig, installPath)


versions = {
    "1.0.27": {
        "url": "https://github.com/libusb/libusb-cmake/archive/8f0b4a38fc3eefa2b26a99dff89e1c12bf37afd4.zip",
        "root": "libusb-cmake-8f0b4a38fc3eefa2b26a99dff89e1c12bf37afd4",
        "builder": _build,
    },
}


_libraryName = "libusb"


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
