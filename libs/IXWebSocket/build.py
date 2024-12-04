import os
import utils


def _build(config: dict, srcPath: str, buildPath: str, installPath: str, buildConfig: str):
    zlibVersion, zlibVariant = config['deps']['zlib'].split("/", 1)
    configArgs = list()

    # ZLIB
    configArgs.append(f"-DUSE_ZLIB={config['useZLIB']}")
    if config["useZLIB"]:
        configArgs.append(f"-DZLIB_ROOT={utils.searchLibrary('zlib', zlibVersion, zlibVariant, buildConfig)}")

    # TLS
    configArgs.append(f"-DUSE_TLS={config['useTLS']}")

    configArgs.append("-DIXWEBSOCKET_INSTALL=1")

    utils.cmake(*configArgs, "-S", srcPath, "-B", buildPath)
    utils.cmake("--build", buildPath, "--config", buildConfig)
    utils.cmake("--install", buildPath, "--config", buildConfig, "--prefix", installPath)


versions = {
    "11.4.5": {
        "url": "https://github.com/machinezone/IXWebSocket/archive/refs/tags/v11.4.5.zip",
        "root": "IXWebSocket-11.4.5",
        "builder": _build,
    },
}


def build():
    print("Build IXWebSocket")

    for version, variant, cfg in utils.loadLibraryConfig():
        try:
            versionConfig = versions[version]
            url = versionConfig["url"]
            if url is None:
                raise utils.BuildError("Invalid version")

            srcDirectory = os.path.join(
                utils.getOrDownloadSource(url, "IXWebSocket", version), versionConfig["root"])

            for buildConfig in cfg["config"]:
                print(f"Config: {buildConfig}")
                buildDirectoryPath = utils.getBuildDirectory("IXWebSocket", version, variant, buildConfig)
                installDirectoryPath = utils.getInstallDirectory("IXWebSocket", version, variant, buildConfig)
                versionConfig["builder"](cfg,
                                         srcDirectory,
                                         buildDirectoryPath,
                                         installDirectoryPath,
                                         buildConfig)

        except KeyError as e:
            raise utils.BuildError(f"KeyError. {e}")
