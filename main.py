import os


def _launch(libraryName: str):
    import importlib
    import importlib.util
    dirs = utils.getSourceDirectories()
    for dirpath in dirs:
        filepath = os.path.join(dirpath, libraryName, "build.py")
        print(filepath)
        if os.path.exists(filepath):
            print(f"Found library script. {filepath}")
            break
    else:
        raise utils.BuildError(f"Not found {libraryName}")

    spec = importlib.util.spec_from_file_location(libraryName, filepath)
    builder = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(builder)

    os.chdir(os.path.dirname(filepath))
    builder.build()


def main(*libraryNames: str):
    for libraryName in libraryNames:
        _launch(libraryName)


if __name__ == "__main__":
    import argparse
    import utils
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
    utils.loadGlobalConfig(args.config)

    if args.clean:
        utils.cleanCache()

    main(*args.libraryName)
