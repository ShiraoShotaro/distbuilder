import os
import utils


def main(*libraryNames: str):
    class CwdScope:
        def __init__(self):
            self._cwd = None

        def __enter__(self, *_):
            self._cwd = os.getcwd()

        def __exit__(self, *_):
            if self._cwd is not None:
                os.chdir(self._cwd)

    for libraryName in libraryNames:
        buildFunc, path = utils.searchBuildFunctionAndPath(libraryName)
        with CwdScope():
            os.chdir(os.path.dirname(path))
            buildFunc()  # TODO: version, variant 指定できるように


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("libraryName",
                        type=str, nargs="+",
                        help="Library Name")
    parser.add_argument("--config",
                        type=str, default=None,
                        help="Config path, Default is ./config.toml.")
    parser.add_argument("--clean",
                        action="store_true", default=False,
                        help="Clean build. (Clear all cache.)")

    args = parser.parse_args()
    configPath = args.config
    if configPath is None:
        configPath = os.path.join(os.path.dirname(__file__), "config.toml")
    utils.loadGlobalConfig(configPath)

    if args.clean:
        utils.cleanCache()

    main(*args.libraryName)
