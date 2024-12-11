import os
import utils


def _build(config: utils.Config,
           srcPath: str, buildPath: str,
           installPath: str, buildConfig: str):

    zlibPath = config.dep('zlib').opt(cmakeReq=False)

    args = [
        "-Dprotobuf_ABSL_PROVIDER=package",
        f"-Dabsl_DIR={config.dep('abseil').req(cmakeName='absl')}",
        "-Dprotobuf_ALLOW_CCACHE=0",
        "-Dprotobuf_BUILD_CONFORMANCE=0",
        "-Dprotobuf_BUILD_EXAMPLES=0",
        "-Dprotobuf_BUILD_LIBPROTOC=1",
        "-Dprotobuf_BUILD_LIBUPB=1",
        "-Dprotobuf_BUILD_PROTOBUF_BINARIES=1",  # これはあったほうが便利か？
        "-Dprotobuf_BUILD_PROTOC_BINARIES=1",  # Default: 1
        f"-Dprotobuf_BUILD_SHARED_LIBS={config.shared.f(False).t(bool)}",
        "-Dprotobuf_BUILD_TESTS=0",
        "-Dprotobuf_DISABLE_RTTI=0",
        "-Dprotobuf_INSTALL=1",
        "-Dprotobuf_JSONCPP_PROVIDER=package",
        "-Dprotobuf_MSVC_STATIC_RUNTIME=0",  # use MD
        "-Dprotobuf_TEST_XML_OUTDIR=0",
        "-Dprotobuf_USE_UNITY_BUILD=0",
        "-Dutf8_range_ENABLE_INSTALL=1",
        "-Dutf8_range_ENABLE_TESTS=0",
        f"-Dprotobuf_WITH_ZLIB={'1' if zlibPath is not None else '0'}",
    ]

    if config.withZlib.f(False):
        # zlib は cmake 側が FindZLib を持っている.
        args.append(f"-DZLIB_ROOT={zlibPath}")
        args.append("-DZLIB_USE_STATIC_LIBS=1")

    utils.cmake(*args, "-S", srcPath, "-B", buildPath)
    utils.cmake("--build", buildPath, "--config", buildConfig)
    utils.cmake("--install", buildPath, "--config", buildConfig, "--prefix", installPath)


versions = {
    "29.1": {
        "url": "https://github.com/protocolbuffers/protobuf/archive/refs/tags/v29.1.zip",
        "root": "protobuf-29.1",
        "builder": _build,
    },
}


_libraryName = "protobuf"


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
