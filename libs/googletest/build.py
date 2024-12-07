import os
import utils


def _build(config, srcPath: str, buildPath: str, installPath: str, buildConfig: str):
    args = [
        "-DINSTALL_GTEST=1",
        "-Dgtest_force_shared_crt=1",
        f"-DBUILD_SHARED_LIBS={config['shared']}",
        f"-DBUILD_GMOCK={config['gmock']}"
    ]
    utils.cmake(*args, "-S", srcPath, "-B", buildPath)
    utils.cmake("--build", buildPath, "--config", buildConfig)
    utils.cmake("--install", buildPath, "--config", buildConfig, "--prefix", installPath)


versions = {
    "1.15.2": {
        "url": "https://github.com/google/googletest/archive/refs/tags/v1.15.2.zip",
        "root": "googletest-1.15.2",
        "builder": _build,
    },
}


_libraryName = "googletest"


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
