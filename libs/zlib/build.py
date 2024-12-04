import os
import utils


def _build(srcPath: str, buildPath: str, installPath: str, buildConfig: str):
    utils.cmake(
        "-DZLIB_BUILD_EXAMPLES=0",
        "-S", srcPath, "-B", buildPath)
    utils.cmake("--build", buildPath, "--config", buildConfig)
    utils.cmake("--install", buildPath, "--config", buildConfig, "--prefix", installPath)


versions = {
    "11.4.5": {
        "url": "https://github.com/madler/zlib/archive/refs/tags/v1.3.1.zip",
        "root": "zlib-1.3.1",
        "builder": _build,
    },
}


def build():
    print("Build zlib")

    for version, variant, cfg in utils.loadLibraryConfig():
        try:
            versionConfig = versions[version]
            url = versionConfig["url"]
            if url is None:
                raise utils.BuildError("Invalid version")

            srcDirectory = os.path.join(
                utils.getOrDownloadSource(url, "zlib", version), versionConfig["root"])

            for buildConfig in cfg["config"]:
                print(f"Config: {buildConfig}")
                buildDirectoryPath = utils.getBuildDirectory(
                    "zlib", version, variant, buildConfig)
                installDirectoryPath = utils.getInstallDirectory(
                    "zlib", version, variant, buildConfig)
                versionConfig["builder"](srcDirectory,
                                         buildDirectoryPath,
                                         installDirectoryPath,
                                         buildConfig)

        except KeyError as e:
            raise utils.BuildError(f"KeyError. {e}")
