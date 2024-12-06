import os
import utils


def _build(config, srcPath: str, buildPath: str, installPath: str, buildConfig: str):
    args = [
        f"-DCMAKE_INSTALL_PREFIX={installPath}",  # config 時に直接使っているみたいで, これは必須でした
        f"-DLIBDEFLATE_BUILD_GZIP={config['buildGzip']}",
        f"-DLIBDEFLATE_BUILD_SHARED_LIB={config['shared']}",
        f"-DLIBDEFLATE_BUILD_STATIC_LIB={not config['shared']}",
        "-DLIBDEFLATE_BUILD_TESTS=0",
        "-DLIBDEFLATE_COMPRESSION_SUPPORT=1",
        "-DLIBDEFLATE_DECOMPRESSION_SUPPORT=1",
        f"-DLIBDEFLATE_GZIP_SUPPORT={config['gzipSupport']}",
        f"-DLIBDEFLATE_ZLIB_SUPPORT={config['zlibSupport']}",
        "-DLIBDEFLATE_USE_SHARED_LIB=0",
    ]
    utils.cmake(*args, "-S", srcPath, "-B", buildPath)
    utils.cmake("--build", buildPath, "--config", buildConfig)
    utils.cmake("--install", buildPath, "--config", buildConfig, "--prefix", installPath)


versions = {
    "1.22": {
        "url": "https://github.com/ebiggers/libdeflate/archive/refs/tags/v1.22.zip",
        "root": "libdeflate-1.22",
        "builder": _build,
    },
    "1.18": {
        "url": "https://github.com/ebiggers/libdeflate/archive/refs/tags/v1.18.zip",
        "root": "libdeflate-1.18",
        "builder": _build,
    },
}


_libraryName = "libdeflate"


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
