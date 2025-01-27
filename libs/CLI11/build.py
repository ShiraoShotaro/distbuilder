import os
import utils


def _build(srcPath: str, buildPath: str, installPath: str, buildConfig: str):
    utils.cmakeConfigure(
        srcPath, buildPath,
        "-DCLI11_BUILD_DOCS=0",
        "-DCLI11_BUILD_EXAMPLES=0",
        "-DCLI11_BUILD_TESTS=0",
        "-DCLI11_INSTALL=1",
        "-DCLI11_PRECOMPILED=1",
        "-DCLI11_SANITIZERS=0",
        "-DCLI11_SINGLE_FILE=0")
    utils.cmakeBuildAndInstall(buildPath, buildConfig, installPath)


versions = {
    "2.4.2": {
        "url": "https://github.com/CLIUtils/CLI11/archive/refs/tags/v2.4.2.zip",
        "root": "CLI11-2.4.2",
        "builder": _build,
    },
}


def build():
    print("Build CLI11")

    for version, variant, cfg in utils.loadLibraryConfig():
        try:
            versionConfig = versions[version]
            url = versionConfig["url"]
            if url is None:
                raise utils.BuildError("Invalid version")

            srcDirectory = os.path.join(
                utils.getOrDownloadSource(url, "CLI11", version), versionConfig["root"])

            for buildConfig in cfg["config"]:
                print(f"Config: {buildConfig}")
                buildDirectoryPath = utils.getBuildDirectory("CLI11", version, variant, buildConfig)
                installDirectoryPath = utils.getInstallDirectory("CLI11", version, variant, buildConfig)
                versionConfig["builder"](srcDirectory,
                                         buildDirectoryPath,
                                         installDirectoryPath,
                                         buildConfig)

        except KeyError as e:
            raise utils.BuildError(f"KeyError. {e}")
