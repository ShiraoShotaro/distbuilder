import os
import utils


def _build(config, srcPath: str, buildPath: str, installPath: str, buildConfig: str):
    args = [
        f"-DBUILD_SHARED_LIBS={config['shared']}",
        "-DUSE_MSVC_RUNTIME_LIBRARY_DLL=0",
        "-DGLFW_BUILD_DOCS=0",
        "-DGLFW_BUILD_EXAMPLES=0",
        "-DGLFW_BUILD_TEST=0",
        "-DGLFW_INSTALL=1",
    ]
    if os.name == "nt":
        args.append("-DGLFW_BUILD_WIN32=1")

    utils.cmake(*args, "-S", srcPath, "-B", buildPath)
    utils.cmake("--build", buildPath, "--config", buildConfig)
    utils.cmake("--install", buildPath, "--config", buildConfig, "--prefix", installPath)


versions = {
    "3.4": {
        "url": "https://github.com/glfw/glfw/archive/refs/tags/3.4.zip",
        "root": "glfw-3.4",
        "builder": _build,
    },
}


_libraryName = "glfw"


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
