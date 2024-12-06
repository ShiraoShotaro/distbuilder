import os
import utils


def _build(config, srcPath: str, buildPath: str, installPath: str):
    args = [
        "-DPYTHON=0",
        "-DCMAKE_CONFIGURATION_TYPES=Release;Debug",
        f"-DBUILD_SHARED_LIBS={config['shared']}",
        "-DBUILD_TESTING=0",
        "-DBUILD_WEBSITE=0",
        "-DIMATH_INSTALL=1",
        "-DIMATH_INSTALL_PKG_CONFIG=0",
        "-DIMATH_INSTALL_SYM_LINK=0",
        "-DIMATH_USE_NOEXCEPT=1",
    ]
    utils.cmake(*args, "-S", srcPath, "-B", buildPath)
    utils.cmake("--build", buildPath, "--config", "Debug")
    utils.cmake("--build", buildPath, "--config", "Release")
    utils.cmake("--install", buildPath, "--config", "Debug", "--prefix", installPath)
    utils.cmake("--install", buildPath, "--config", "Release", "--prefix", installPath)


versions = {
    "3.1.12": {
        "url": "https://github.com/AcademySoftwareFoundation/Imath/archive/refs/tags/v3.1.12.zip",
        "root": "Imath-3.1.12",
        "builder": _build,
    },
}


_libraryName = "Imath"


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

            buildDirectoryPath = utils.getBuildDirectory(_libraryName, version, variant, None)
            installDirectoryPath = utils.getInstallDirectory(_libraryName, version, variant, None)
            versionConfig["builder"](cfg,
                                     srcDirectory,
                                     buildDirectoryPath,
                                     installDirectoryPath)

        except KeyError as e:
            raise utils.BuildError(f"KeyError. {e}")
