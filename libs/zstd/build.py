import os
import utils


def _build_1_5_6(srcPath: str, buildPath: str, installPath: str, buildConfig: str):
    # https://github.com/facebook/zstd/issues/3999
    utils.cmake(f"-DCMAKE_RC_FLAGS=-I{srcPath}/lib",
                "-DCMAKE_CONFIGURATION_TYPE=Debug;Release",
                "-S", os.path.join(srcPath, "build", "cmake"),
                "-B", buildPath)
    utils.cmake("--build", buildPath, "--config", buildConfig)
    utils.cmake("--install", buildPath, "--prefix",
                installPath, "--config", buildConfig)


versions = {
    "1.5.6": {
        "url": "https://github.com/facebook/zstd/archive/refs/tags/v1.5.6.zip",
        "root": "zstd-1.5.6",
        "builder": _build_1_5_6,
    },
}


def build():
    print("Build ZSTD")
    for version, variant, cfg in utils.loadLibraryConfig():
        try:
            versionConfig = versions[version]
            url = versionConfig["url"]
            if url is None:
                raise utils.BuildError("Invalid version")

            srcDirectory = os.path.join(
                utils.getOrDownloadSource(url, "zstd", version), versionConfig["root"])

            for buildConfig in cfg["config"]:
                print(f"Config: {buildConfig}")
                buildDirectoryPath = utils.getBuildDirectory("zstd", version, variant, buildConfig)
                installDirectoryPath = utils.getInstallDirectory("zstd", version, variant, buildConfig)
                versionConfig["builder"](srcDirectory,
                                         buildDirectoryPath,
                                         installDirectoryPath,
                                         buildConfig)

        except KeyError as e:
            raise utils.BuildError(f"KeyError. {e}")
