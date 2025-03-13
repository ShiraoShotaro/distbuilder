import os
import utils


def _build(config: utils.Config, srcPath: str, buildPath: str, installPath: str, buildConfig: str):
    args = [
        "-DBASE64_BUILD_TESTS=0",
        "-DBASE64_REGENERATE_TABLES=0",
        "-DBASE64_WERROR=1",
        f"-DBASE64_WITH_AVX={config.withAVX.t(bool)}",
        f"-DBASE64_WITH_AVX2={config.withAVX2.t(bool)}",
        f"-DBASE64_WITH_AVX512={config.withAVX512.t(bool)}",
        f"-DBASE64_WITH_OpenMP={config.withOpenMP.t(bool)}",
        f"-DBASE64_WITH_SSE41={config.withSSE41.t(bool)}",
        f"-DBASE64_WITH_SSE42={config.withSSE42.t(bool)}",
        f"-DBASE64_WITH_SSSE3={config.withSSSE3.t(bool)}",
    ]

    utils.cmake(*args, "-S", srcPath, "-B", buildPath)
    utils.cmake("--build", buildPath, "--config", buildConfig)
    utils.cmake("--install", buildPath, "--config", buildConfig, "--prefix", installPath)


versions = {
    "0.5.2": {
        "url": "https://github.com/aklomp/base64/archive/refs/tags/v0.5.2.zip",
        "root": "base64-0.5.2",
        "builder": _build,
    },
}


_libraryName = "base64"


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
