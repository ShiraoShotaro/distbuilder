
def _launch(libraryName: str):
    import importlib
    buildModule = importlib.import_module(f"libs.{libraryName}.build")
    buildModule.build()


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

