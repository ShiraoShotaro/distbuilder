import os
import utils


def _build(config: utils.Config, srcPath: str, buildPath: str, installPath: str, buildConfig: str):
    args = [
        "-DgRPC_ABSL_PROVIDER=package",
        f"-Dabsl_DIR={config.dep('abseil').req(cmakeName='absl')}",
        "-DgRPC_BUILD_CODEGEN=1",
        "-DgRPC_BUILD_GRPCPP_OTEL_PLUGIN=0",
        "-DgRPC_BUILD_GRPC_CPP_PLUGIN=1",
        "-DgRPC_BUILD_GRPC_CSHARP_PLUGIN=0",
        "-DgRPC_BUILD_GRPC_NODE_PLUGIN=0",
        "-DgRPC_BUILD_GRPC_OBJECTIVE_C_PLUGIN=0",
        "-DgRPC_BUILD_GRPC_PHP_PLUGIN=0",
        "-DgRPC_BUILD_GRPC_PYTHON_PLUGIN=0",
        "-DgRPC_BUILD_GRPC_RUBY_PLUGIN=0",
        "-DgRPC_BUILD_MSVC_MP_COUNT=0",
        "-DgRPC_BUILD_TESTS=0",
        "-DgRPC_CARES_PROVIDER=package",
        f"-Dc-ares_DIR={config.dep('c-ares').req()}",
        "-DgRPC_DOWNLOAD_ARCHIVES=0",
        "-DgRPC_INSTALL=1",
        "-DgRPC_MSVC_STATIC_RUNTIME=0",  # Use MD
        "-DgRPC_PROTOBUF_PROVIDER=package",
        f"-DProtobuf_DIR={config.dep('protobuf').req(cmakeName='protobuf')}",
        f"-Dutf8_range_DIR={config.dep('protobuf').req(cmakeName='utf8_range')}",
        "-DgRPC_RE2_PROVIDER=package",
        f"-Dre2_DIR={config.dep('re2').req()}",
        "-DgRPC_SSL_PROVIDER=package",
        f"-DOPENSSL_ROOT_DIR={config.dep('boringssl').req(cmakeReq=False)}",
        "-DgRPC_USE_PROTO_LITE=0",
        "-DgRPC_ZLIB_PROVIDER=package",
        f"-DZLIB_ROOT={config.dep('zlib').req(cmakeReq=False)}",
        "-DZLIB_USE_STATIC_LIBS=1",
    ]

    utils.cmake(*args, "-S", srcPath, "-B", buildPath)
    utils.cmake("--build", buildPath, "--config", buildConfig)
    utils.cmake("--install", buildPath, "--config", buildConfig, "--prefix", installPath)


versions = {
    "1.68.2": {
        "url": "https://github.com/grpc/grpc/archive/refs/tags/v1.68.2.zip",
        "root": "grpc-1.68.2",
        "builder": _build,
    },
}


_libraryName = "grpc"


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
