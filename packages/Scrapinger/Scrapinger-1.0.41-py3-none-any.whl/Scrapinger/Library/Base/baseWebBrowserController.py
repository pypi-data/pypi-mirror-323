from bs4 import BeautifulSoup
from selenium.webdriver.android.webdriver import WebDriver
from LibHanger.Library.uwGlobals import *
from Scrapinger.Library.scrapingConfig import scrapingConfig


class baseWebBrowserController:
    """
    ブラウザーコントローラー基底クラス
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

        # 共通設定のセット
        self.config = _config

        # Webドライバーインスタンス格納用変数初期化
        self.wDriver: WebDriver = None

        # BeautifulSoupインスタンス格納用変数初期化
        self.bSoup: BeautifulSoup = None

        # loadPageを実行した回数
        self.__loadPageCount = 0

        # ScrapingTypeをメンバ変数にセット
        self.__scrapingType = _scrapingType

    @property
    def loadPageCount(self):
        """
        loadPageを実行した回数
        """

        return self.__loadPageCount

    @property
    def scrapingType(self):
        """
        ScrapingType
        スクレイピング方法を指定する(unknownの場合はconfig側で指定した設定を優先する)
        """

        return self.__scrapingType

    @property
    def delayWaitElement(self):
        """
        delayWaitElement
        delayWaitElementを文字列で指定する(指定したlocatorに対応するElementを指定する。未指定の場合はconfig側で指定した設定を優先する)
        """

        return None

    def addLoadPageCount(self):
        """
        loadPage回数を加算する
        """

        # loadPageCount加算
        self.__loadPageCount += 1

    def resetLoadPageCount(self):
        """
        loadPage回数をリセットする
        """

        # loadPageCount初期化
        self.__loadPageCount = 0
