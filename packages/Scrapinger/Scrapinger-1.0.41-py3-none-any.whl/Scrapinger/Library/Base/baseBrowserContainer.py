from Scrapinger.Library.scrapingConfig import scrapingConfig
from Scrapinger.Library.scrapingerGlobals import *
from Scrapinger.Library.webBrowserController import webBrowserController


class baseBrowserContainer:

    def __init__(self) -> None:
        """
        コンストラクタ
        """

        # 共通設定のセット
        self.config: scrapingConfig = gv.scrapingerConfig

    @property
    def scrapingType(self):
        """
        ScrapingType
        スクレイピング方法を指定する(unknownの場合はconfig側で指定した設定を優先する)
        """

        return scrapingConfig.settingValueStruct.ScrapingType.unknown

    def getScrapingType(self):
        """
        ScrapingType取得
        未設定(unknown)の場合はScraping.iniで設定されているScrapingTypeを返す
        """
        return (
            self.scrapingType
            if self.scrapingType
            != scrapingConfig.settingValueStruct.ScrapingType.unknown
            else self.config.ScrapingType
        )

    class beautifulSoup(webBrowserController):
        """
        beautifulSoup用コンテナ
        """

        def __init__(
            self,
            _config: scrapingConfig,
            _scrapingType: scrapingConfig.settingValueStruct.ScrapingType,
        ):
            """
            コンストラクタ

            Parameters
            ----------
            _config : scrapingConfig
                共通設定クラス
            _scrapingType : scrapingConfig.settingValueStruct.ScrapingType
                スクレイピングタイプ
            """

            # 基底側コンストラクタ呼び出し
            super().__init__(_config, _scrapingType)

    class chrome(webBrowserController):
        """
        GoogleCheromブラウザコンテナ
        """

        def __init__(
            self,
            _config: scrapingConfig,
            _scrapingType: scrapingConfig.settingValueStruct.ScrapingType,
        ):
            """
            コンストラクタ

            Parameters
            ----------
            _config : scrapingConfig
                共通設定クラス
            _scrapingType : scrapingConfig.settingValueStruct.ScrapingType
                スクレイピングタイプ
            """

            # 基底側コンストラクタ呼び出し
            super().__init__(_config, _scrapingType)

        def getWebDriver(self):
            """
            Webドライバーを取得する

            Parameters
            ----------
            None

            """

            return None

    class firefox(webBrowserController):
        """
        FireFoxブラウザコンテナ
        """

        def __init__(
            self,
            _config: scrapingConfig,
            _scrapingType: scrapingConfig.settingValueStruct.ScrapingType,
        ):
            """
            コンストラクタ

            Parameters
            ----------
            _config : scrapingConfig
                共通設定クラス
            _scrapingType : scrapingConfig.settingValueStruct.ScrapingType
                スクレイピングタイプ
            """

            # 基底側コンストラクタ呼び出し
            super().__init__(_config, _scrapingType)

        def getWebDriver(self):
            """
            Webドライバーを取得する

            Parameters
            ----------
            None

            """
            return None
