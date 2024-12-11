import os
import glob
from typing import Optional
from distbuilder.errors import BuildError
from distbuilder.functions import (
    getInstallRootDirectory,
    searchBuildFunctionAndPath,
)


class ConfigValue:
    def __init__(self, key: str, value):
        self._key = key
        self._value = value

    def fallback(self, value):
        if self._value is None:
            self._value = value
        return self

    def f(self, value):
        return self.fallback(value)

    def type(self, tp):
        if not isinstance(self._value, tp):
            raise BuildError(f"Invalid configure value type. Key: {self._key} value must be {tp}")
        return self

    def t(self, tp):
        return self.type(tp)

    def __bool__(self):
        self.type(bool)
        return self._value

    def __str__(self):
        if isinstance(self._value, bool):
            return "1" if self._value else "0"
        else:
            return str(self._value)


class Dependency:
    def __init__(self, libraryName: str, depInfo: str, buildConfig: Optional[str]):
        self._libraryName = libraryName
        self._version = None
        self._variant = None
        self._buildConfig = buildConfig
        if depInfo is not None:
            self._version, self._variant = depInfo.split("/", 1)

        # レシピに登録されているかどうか
        func, path = searchBuildFunctionAndPath(self._libraryName)
        self._builder = func
        self._builderPath = path

        # ビルドされているか
        if depInfo is not None:
            self._isBuilt = os.path.exists(self._getInstallDirectoryPath())
        else:
            self._isBuilt = False

    def _getInstallDirectoryPath(self):
        # ライブラリが install されるべきディレクトリパスを返す.
        installDirectory = os.path.join(
            getInstallRootDirectory(), self._libraryName, self._version, self._variant)
        if self._buildConfig:
            installDirectory = os.path.join(installDirectory, self._buildConfig)
        return installDirectory

    def _searchCMakeConfig(self, cmakeName):
        # config.cmake を探す.
        # これが無いとどうしようもない.
        if cmakeName is None:
            cmakeName = self._libraryName
        cmakeName = cmakeName.lower()
        print(f"Searching cmake config. {cmakeName}")
        installDirectory = self._getInstallDirectoryPath()
        candidates = glob.glob(os.path.join(installDirectory, "**/*.cmake"),
                               recursive=True)
        candidates = [(fp, os.path.basename(fp).lower()) for fp in candidates]
        for fp, fn in candidates:
            print(f"-- search: {fp}")
            if fn.endswith("config.cmake") and fn.startswith(cmakeName):
                print(f"Library '{self._libraryName}' is found. {os.path.dirname(fp)}")
                return os.path.dirname(fp)
        else:
            raise BuildError(f"Library '{self._libraryName}' cmake file is not found.")

    def req(self, *, cmakeReq=True, cmakeName=None):
        # 必須.
        if self._version is None or self._variant is None:
            raise BuildError(
                f"Library '{self._libraryName}' is required, "
                "but is not specified by config.toml")

        if not self._isBuilt:
            # 自動的にビルドする？
            # TODO: 今はエラーに.
            raise BuildError(
                f"Library '{self._libraryName}/{self._version}/{self._variant}' is required, "
                "but is not built")

        if cmakeReq:
            return self._searchCMakeConfig(cmakeName)
        else:
            return self._getInstallDirectoryPath()

    def opt(self, *, cmakeReq=True, cmakeName=None):
        if self._version is None or self._variant is None:
            return None

        if not self._isBuilt:
            # version, variant が明示されていたら, 使うという意思表示とする.
            # 自動的にビルドする？
            # TODO: 今はエラーに.
            raise BuildError(
                f"Library '{self._libraryName}/{self._version}/{self._variant}' is required, "
                "but is not built")

        if cmakeReq:
            return self._searchCMakeConfig(cmakeName)
        else:
            return self._getInstallDirectoryPath()


class Config:
    def __init__(self, configDict: dict, buildConfig: Optional[str]):
        self._cfg: dict = configDict.copy()
        self._buildConfig = buildConfig

    def __getattr__(self, name):
        return ConfigValue(name, self._cfg.get(name, None))

    def dep(self, libraryName):
        dep = None
        if "deps" in self._cfg:
            dep = self._cfg["deps"].get(libraryName)
        return Dependency(libraryName, dep, self._buildConfig)
