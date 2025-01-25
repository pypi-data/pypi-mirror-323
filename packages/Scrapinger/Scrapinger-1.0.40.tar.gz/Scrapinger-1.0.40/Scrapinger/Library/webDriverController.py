import LibHanger.Library.uwLogger as Logger
from Scrapinger.Library.Base.baseBrowserContainer import baseBrowserContainer
from Scrapinger.Library.scrapingConfig import scrapingConfig
from Scrapinger.Library.scrapingerException import scrapingerException


class webDriverController:
    """
    WebDriverコントローラークラス

    Notes
    -----
        取り扱うWebDriverをブラウザータイプごとに取得する
    """

    def __init__(
        self, _config: scrapingConfig, _browserContainer: baseBrowserContainer
    ):
        """
        コンストラクタ

        Parameters
        ----------
        _config : scrapingConfig
            共通設定クラス
        _browserContainer : browserContainer
            ブラウザコンテナクラス
        """

        # 共通設定取得
        self.config = _config

        # ブラウザーコンテナインスタンス設定
        self.browserContainerInstance = _browserContainer

        # ブラウザーコントロールインスタンス初期化
        self.browserCtl = None

    @Logger.loggerDecorator("Initialize browserCtl")
    def initBrowserCtl(self):
        """
        browserCtlを初期化する
        BeutifulSoup⇒Seleniumへの切り替え時に使用
        """

        self.browserCtl = None

    @Logger.loggerDecorator("Setting Scrape")
    def settingScrape(self, browserCtlInstanceKeep=True):
        """
        スクレイピング準備

        browserCtlInstanceKeep : bool
            browserCtlインスタンスを保持するか
            (False指定時はbrowserCtlインスタンスを再生成する)
        """

        # 既にbrowserCtlインスタンスが存在する、かつbrowserCtlInstanceKeep = Trueの場合は処理を抜ける
        if not self.browserCtl is None and browserCtlInstanceKeep == True:
            return

        # ScrapingType判定(インスタンス取得)
        if (
            self.browserContainerInstance.getScrapingType()
            == scrapingConfig.settingValueStruct.ScrapingType.beutifulSoup
        ):
            self.getBeautifulSoupInstance()
        elif (
            self.browserContainerInstance.getScrapingType()
            == scrapingConfig.settingValueStruct.ScrapingType.selenium
        ):
            self.getWebDriverInstance()
        else:
            # ScrapingType指定例外
            raise scrapingerException.scrapingTypeErrorException

    @Logger.loggerDecorator("Get BeautifulSoupInstance")
    def getBeautifulSoupInstance(self):
        """
        BeautifulSoupインスタンスを取得する
        """

        self.browserCtl = self.browserContainerInstance.beautifulSoup(
            self.config, self.browserContainerInstance.scrapingType
        )

    @Logger.loggerDecorator("Get WebDriverInstance")
    def getWebDriverInstance(self):
        """
        WebDriverインスタンスを取得する
        """

        # ブラウザータイプごとに生成するインスタンスを切り替える
        browserName = "unknown"
        if (
            self.config.BrowserType
            == scrapingConfig.settingValueStruct.BrowserType.chrome
        ):
            self.browserCtl = self.browserContainerInstance.chrome(
                self.config, self.browserContainerInstance.scrapingType
            )
            browserName = scrapingConfig.settingValueStruct.BrowserType.chrome.name
        elif (
            self.config.BrowserType
            == scrapingConfig.settingValueStruct.BrowserType.firefox
        ):
            self.browserCtl = self.browserContainerInstance.firefox(
                self.config, self.browserContainerInstance.scrapingType
            )
            browserName = scrapingConfig.settingValueStruct.BrowserType.firefox.name
        else:
            # 例外とする
            raise scrapingerException.scrapingTypeErrorException

        # 取得したWebDriverをログ出力
        Logger.logging.info("BrowserType:" + str(self.config.BrowserType))
        Logger.logging.info("SelectedBrowser:" + browserName)

        # 取得したWebDriverインスタンスを返す
        return self.browserCtl.getWebDriver()
