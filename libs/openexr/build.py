import os
import utils


def _build(config, srcPath: str, buildPath: str, installPath: str):
    args = [
        "-DPYTHON=0",
        f"-DBUILD_SHARED_LIBS={config['shared']}",
        "-DBUILD_TESTING=0",
        "-DBUILD_WEBSITE=0",
        "-DOPENEXR_BUILD_EXAMPLES=0",
        "-DOPENEXR_BUILD_LIBS=1",
        "-DOPENEXR_BUILD_PYTHON=0",
        "-DOPENEXR_BUILD_TOOLS=0",
        "-DOPENEXR_ENABLE_THREADING=1",
        "-DOPENEXR_INSTALL=1",
        "-DOPENEXR_INSTALL_DOCS=0",
        "-DOPENEXR_INSTALL_PKG_CONFIG=0",
        "-DOPENEXR_INSTALL_TOOLS=0",
        "-DOPENEXR_TEST_LIBRARIES=0",
        "-DOPENEXR_TEST_PYTHON=0",
        "-DOPENEXR_TEST_TOOLS=0",
    ]

    imathPath = utils.searchLibrary(config, "Imath", None)
    args.append(f"-DImath_DIR={imathPath}")

    for buildConfig in config["config"]:
        libdeflatePath = utils.searchLibrary(config, "libdeflate", buildConfig)
        utils.cmake(*args, f"-Dlibdeflate_DIR={libdeflatePath}",
                    "-S", srcPath, "-B", buildPath)
        utils.cmake("--build", buildPath, "--config", buildConfig)
        utils.cmake("--install", buildPath, "--config", buildConfig, "--prefix", installPath)


versions = {
    "3.3.2": {
        "url": "https://github.com/AcademySoftwareFoundation/openexr/archive/refs/tags/v3.3.2.zip",
        "root": "openexr-3.3.2",
        "builder": _build,
    },
}


_libraryName = "openexr"


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
