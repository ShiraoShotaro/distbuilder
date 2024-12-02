import os
import utils


def _build(srcPath: str, buildPath: str, installPath: str, buildConfig: str):
    utils.cmake(
        f"-DCLI11_BUILD_DOCS=0",
        f"-DCLI11_BUILD_EXAMPLES=0",
        f"-DCLI11_BUILD_TESTS=0",
        f"-DCLI11_INSTALL=1",
        f"-DCLI11_PRECOMPILED=1",
        f"-DCLI11_SANITIZERS=0",
        f"-DCLI11_SINGLE_FILE=0",
        "-S", srcPath, "-B", buildPath)
    utils.cmake(f"--build", buildPath, "--config", buildConfig)
    utils.cmake(f"--install", buildPath, "--prefix", installPath, "--config", buildConfig)


versions = {
    "2.4.2": {
        "url": "https://github.com/CLIUtils/CLI11/archive/refs/tags/v2.4.2.zip",
        "root": "CLI11-2.4.2",
        "builder": _build,
    },
}


def build():
    print("Build CLI11")
    cfg = utils.loadLibraryConfig()

    for variant, cfg in cfg.items():
        try:
            version = cfg["version"]
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
                versionConfig["builder"](
                    srcDirectory,
                    buildDirectoryPath,
                    installDirectoryPath,
                    buildConfig)

        except KeyError as e:
            raise utils.BuildError(f"KeyError. {e}")

