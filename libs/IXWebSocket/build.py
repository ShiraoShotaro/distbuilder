import os
import utils


def _build(config: utils.Config, srcPath: str, buildPath: str, installPath: str, buildConfig: str):
    configArgs = list()

    # ZLIB
    configArgs.append(f"-DUSE_ZLIB={config.useZLIB.f(False).t(bool)}")
    if config.useZLIB.f(False).t(bool):
        path = config.dep("zlib").req(cmakeReq=False)
        configArgs.append(f"-DZLIB_ROOT={path}")
        configArgs.append("-DZLIB_USE_STATIC_LIBS=1")

    # TLS
    # configArgs.append(f"-DUSE_TLS={config['useTLS']}")

    configArgs.append("-DIXWEBSOCKET_INSTALL=1")

    utils.cmakeConfigure(srcPath, buildPath, *configArgs)
    utils.cmakeBuildAndInstall(buildPath, buildConfig, installPath)


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
                versionConfig["builder"](utils.Config(cfg, buildConfig),
                                         srcDirectory,
                                         buildDirectoryPath,
                                         installDirectoryPath,
                                         buildConfig)

        except KeyError as e:
            raise utils.BuildError(f"KeyError. {e}")
