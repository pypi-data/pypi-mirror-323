import os
import time
import requests
import LibHanger.Library.uwLogger as Logger
from os import path
from bs4 import BeautifulSoup, ResultSet, Tag
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options as chromeOptions
from pandas.core.frame import DataFrame
from LibHanger.Library.uwGetter import getPlatform
from LibHanger.Library.uwGlobals import *
from Scrapinger.Library.Base.baseWebBrowserController import baseWebBrowserController
from Scrapinger.Library.scrapingConfig import scrapingConfig


class webBrowserController(baseWebBrowserController):
    """
    ブラウザーコントローラークラス
    """

    def __init__(
        self,
        _config: scrapingConfig,
        _scrapingType: scrapingConfig.settingValueStruct.ScrapingType,
    ):
        """
        コンストラクタ
        """

        # 基底コンストラクタ
        super().__init__(_config, _scrapingType)

        # コールバック関数
        self.cbCreateSearchResultDictionaryByWebDriver = (
            webBrowserController.createSearchResultDictionaryByWebDriver
        )
        self.cbCreateSearchResultDictionaryByBeutifulSoup = (
            webBrowserController.createSearchResultDictionaryByBeutifulSoup
        )
        self.cbCreateSearchResultDataFrameByWebDriver = (
            webBrowserController.createSearchResultDataFrameByWebDriver
        )
        self.cbCreateSearchResultDataFrameByBeutifulSoup = (
            webBrowserController.createSearchResultDataFrameByBeutifulSoup
        )

    def getDelayWaitElement(self):
        """
        Delay取得
        未設定(None)の場合はScraping.iniで設定されているDelayWaitElementを返す
        """
        return (
            self.delayWaitElement
            if self.delayWaitElement != None
            else self.config.DelayWaitElement
        )

    def getRow(self, row: ResultSet):
        """
        行情報をディクショナリに変換して取得する

        Parameters
        ----------
        row : ResultSet
            行情報
        """

        # 行情報ディクショナリ初期化
        dictRow = dict[int, Tag]()

        # 行情報をディクショナリにセット
        colIndex = 0
        for data in row:
            dictRow[colIndex] = data
            colIndex += 1

        # 戻り値を返す
        return dictRow

    @Logger.loggerDecorator("Get WebDriverPath")
    def getWebDriverPath(
        self, _webDriverPath: scrapingConfig.settingValueStruct.WebDriverPath
    ):
        """
        Webドライバーパスを取得する

        Parameters
        ----------
        _webDriverPath : scrapingConfig.settingValueStruct.WebDriverPath
            WebDriverパス列挙体
        """

        webDriverPath = ""
        if getPlatform() == gv.platForm.win:
            webDriverPath = os.path.join(
                path.dirname(self.config.scriptFilePath),
                _webDriverPath.WebDriverPathWin,
            )
        elif getPlatform() == gv.platForm.linux:
            webDriverPath = os.path.join(
                path.dirname(self.config.scriptFilePath),
                _webDriverPath.WebDriverPathLinux,
            )
        elif getPlatform() == gv.platForm.mac:
            webDriverPath = os.path.join(
                path.dirname(self.config.scriptFilePath),
                _webDriverPath.WebDriverPathMac,
            )

        # WebDriverPathログ出力
        Logger.logging.info(webDriverPath)

        # WebDriverPathを返す
        return webDriverPath

    @Logger.loggerDecorator("Get WebDriver")
    def getWebDriver(self):
        """
        ブラウザ操作用のWebドライバーを取得する

        Parameters
        ----------
        config : scrapingConfig
            共通設定クラス
        """

        pass

    @Logger.loggerDecorator("Setting BrowserSize")
    def changeBrowserSize(self, width: str, height: str):
        """
        ブラウザのウィンドウサイズを変更する

        Parameters
        ----------
        width : str
            ウィンドウ横幅(px)
        height : str
            ウィンドウ縦幅(px)
        """

        # Browserサイズログ出力
        Logger.logging.info("BrowserSize:{} x {}".format(width, height))

        # ウィンドウサイズ変更
        self.wDriver.set_window_size(width, height)

    @Logger.loggerDecorator("Load WebPage")
    def loadPage(self, url: str):
        """
        指定URLのページ内容を取得する

        Parameters
        ----------
        url : str
            ページURL
        """

        # URLログ出力
        Logger.logging.info("[TargetUrl]=" + url)

        # ページ内容取得
        if self.scrapingType == self.config.settingValueStruct.ScrapingType.selenium:
            self.wDriver.get(url)
        elif (
            self.scrapingType
            == self.config.settingValueStruct.ScrapingType.beutifulSoup
        ):
            response = requests.get(url)
            self.bSoup = BeautifulSoup(response.content, "lxml")

        # loadPageを実行した回数加算
        self.addLoadPageCount()

    @Logger.loggerDecorator("Normal-Delay")
    def Delay(self):
        """
        指定秒数待機する

        Parameters
        ----------
        None

        """

        # DelayTime-ログ出力
        Logger.logging.info("DelayTime {} Seconds".format(self.config.DelayTime))

        # 待機
        time.sleep(self.config.DelayTime)

    @Logger.loggerDecorator("WebDriver-Delay")
    def WebDriverWait(self, locater: str):
        """
        WebDriverWaitを使った待機及び対象エレメントの取得

        Parameters
        ----------
        locater : str
            By.ID,By.CSS_SELECTOR,By.CLASS_NAME,By.TAG_NAME
        """

        # DelayTime-ログ出力
        Logger.logging.info(
            "WebDriverDelayTime {} Seconds".format(self.config.WebDriverTimeout)
        )

        # タイムアウト設定
        self.wDriver.implicitly_wait(self.config.WebDriverTimeout)
        # 検索結果エレメント取得
        error_count = 0
        # DelayWaitElement取得
        delayWaitElement = self.getDelayWaitElement()
        while True:
            try:

                if locater == By.CSS_SELECTOR:
                    element = self.wDriver.find_element_by_css_selector(
                        delayWaitElement
                    )
                elif locater == By.CLASS_NAME:
                    element = self.wDriver.find_element_by_class_name(delayWaitElement)
                elif locater == By.TAG_NAME:
                    element = self.wDriver.find_element_by_tag_name(delayWaitElement)
                break
            except Exception as e:
                error_count += 1

                if error_count >= self.config.PageLoadRetryCount:
                    Logger.logging.error(
                        "Load Page Timeout Exception. ErrorDescription={}".format(
                            str(e)
                        )
                    )
                    break
                else:
                    time.sleep(0.1)
        return element

    @Logger.loggerDecorator("WebDriver-SetOption")
    def setOptions(self, options: chromeOptions):
        """
        WebDriverオプションを設定する

        Parameters
        ----------
        options : chromeOptions
        """

        for optionStr in self.config.WebDriverOptions:
            options.add_argument(optionStr)

    @Logger.loggerDecorator("Html to Beautifulsoup")
    def htmlToBSoup(self):
        """
        取得したhtmlをBeautifulSoupに変換する
        """

        # ページソースからhtml取得
        html = self.wDriver.page_source.encode("utf-8")

        # htmlをBeautifulSoupに変換して返す
        return BeautifulSoup(html, "html.parser")

    @Logger.loggerDecorator("Create SearchResultDataFrame")
    def createSearchResultDataFrame(
        self, locater: str = By.CSS_SELECTOR, *args, **kwargs
    ) -> DataFrame:
        """
        スクレイピング結果をDataFrameで返す

        Parameters
        ----------
        locater : str
            By.ID,By.CSS_SELECTOR,By.CLASS_NAME,By.TAG_NAME
        """

        try:
            # データ作成前処理
            self.createSearchResultDataFrameBeforeProc(*args, **kwargs)

            # データ作成処理
            retDataFrame = None
            if (
                self.scrapingType
                == self.config.settingValueStruct.ScrapingType.selenium
            ):
                # 待機
                element = self.WebDriverWait(locater)
                # スクレイピング
                retDataFrame = self.cbCreateSearchResultDataFrameByWebDriver(
                    element, *args, **kwargs
                )
            elif (
                self.scrapingType
                == self.config.settingValueStruct.ScrapingType.beutifulSoup
            ):
                # 待機
                self.Delay()
                # スクレイピング
                retDataFrame = self.cbCreateSearchResultDataFrameByBeutifulSoup(
                    self.bSoup, *args, **kwargs
                )

            # データ作成後処理
            retDataFrame = self.createSearchResultDataFrameAfterProc(
                retDataFrame, *args, **kwargs
            )
        except Exception as e:
            raise e

        # 戻り値を返す
        return retDataFrame

    def quitWebDriver(self):
        """
        WebDriver終了処理
        """

        if self.scrapingType == self.config.settingValueStruct.ScrapingType.selenium:

            # WebDriver終了処理
            try:
                self.wDriver.stop_client()
                self.wDriver.close()
                self.wDriver.quit()
            except Exception as e:
                Logger.logging.warning(str(e))

            # WebDriver終了処理-ログ出力
            Logger.logging.info("WebDriver-Quit.")

    @Logger.loggerDecorator("Create SearchResultDataFrame - BeforeProc")
    def createSearchResultDataFrameBeforeProc(self, *args, **kwargs):
        pass

    @Logger.loggerDecorator("Create SearchResultDataFrame - AfterProc")
    def createSearchResultDataFrameAfterProc(self, df: DataFrame, *args, **kwargs):
        return df

    @Logger.loggerDecorator("Create SearchResultDataFrame By WebDriver")
    def createSearchResultDataFrameByWebDriver(
        self, element, *args, **kwargs
    ) -> DataFrame:
        """
        WebDriverを使用してスレイピング結果からDataFrameを生成する(デリゲート用関数)

        Parameters
        ----------
        element : any
            スクレイピング結果

        Notes
        -----
            selenium用データ取得メソッド
            派生クラスで個別処理を実装する
        """

        pass

    @Logger.loggerDecorator("Create SearchResultDataFrame By BeutifulSoup")
    def createSearchResultDataFrameByBeutifulSoup(
        self, soup: BeautifulSoup, *args, **kwargs
    ) -> DataFrame:
        """
        ByBeutifulSoupを使用してスレイピング結果からDataFrameを生成する(デリゲート用関数)

        Parameters
        ----------
        soup : BeautifulSoup
            スクレイピング結果

        Notes
        -----
            BeautifulSoup用データ取得メソッド
            派生クラスで個別処理を実装する
        """

        pass

    @Logger.loggerDecorator("Create SearchResultDictionary")
    def createSearchResultDictionary(
        self,
        dfItemInfo: DataFrame,
        dictItemInfoRowCount: int,
        locater: str = By.CSS_SELECTOR,
    ) -> dict:
        """
        スクレイピング結果をディクショナリで返す

        Parameters
        ----------
        dfItemInfo : DataFrame
            列情報DataFrame
        dictItemInfoRowCount : int
            生成中のディクショナリ行数
        locater : str
            By.ID,By.CSS_SELECTOR,By.CLASS_NAME,By.TAG_NAME
        """

        if self.scrapingType == self.config.settingValueStruct.ScrapingType.selenium:
            # 待機
            element = self.WebDriverWait(locater)
            # スクレイピング
            return self.cbCreateSearchResultDictionaryByWebDriver(
                self, element, dfItemInfo, dictItemInfoRowCount
            )
        elif (
            self.scrapingType
            == self.config.settingValueStruct.ScrapingType.beutifulSoup
        ):
            # 待機
            self.Delay()
            # スクレイピング
            return self.cbCreateSearchResultDictionaryByBeutifulSoup(
                self, self.bSoup, dfItemInfo, dictItemInfoRowCount
            )

    @Logger.loggerDecorator("Create SearchResultDictionary By WebDriver")
    def createSearchResultDictionaryByWebDriver(
        self, element, dfItemInfo: DataFrame, dictItemInfoRowCount: int
    ) -> dict:
        """
        WebDriverを使用してスレイピング結果からDictionaryを生成する(デリゲート用関数)

        Parameters
        ----------
        element : any
            スクレイピング結果
        dfItemInfo : DataFrame
            取得対象DataFrame(列情報)
        config : scrapingerConfig
            共通設定クラス
        dictItemInfoRowCount : int
            取得対象Dictionary現在行数

        Notes
        -----
            selenium用データ取得メソッド
            派生クラスで個別処理を実装する
        """

        pass

    @Logger.loggerDecorator("Create SearchResultDictionary By BeutifulSoup")
    def createSearchResultDictionaryByBeutifulSoup(
        self, soup: BeautifulSoup, dfRaceInfo: DataFrame, dictRaceInfoRowCount: int
    ) -> dict:
        """
        ByBeutifulSoupを使用してスレイピング結果からDictionaryを生成する(デリゲート用関数)

        Parameters
        ----------
        soup : BeautifulSoup
            スクレイピング結果
        dfItemInfo : DataFrame
            取得対象DataFrame(列情報)
        config : scrapingerConfig
            共通設定クラス
        dictItemInfoRowCount : int
            取得対象Dictionary現在行数

        Notes
        -----
            BeautifulSoup用データ取得メソッド
            派生クラスで個別処理を実装する
        """

        pass

    @Logger.loggerDecorator("Scraping with BeautifulSoup")
    def scrapingWithBeautifulSoup(self) -> BeautifulSoup:
        """
        BeautifulSoupを使用してスクレイピング

        Parameters
        ----------
        None
        """

        # スクレイピング結果を返す
        return BeautifulSoup(self.wDriver.page_source, features="lxml")

    @Logger.loggerDecorator("Create PandasData")
    def createPandasData(
        self, dfItemInfo: DataFrame, dictItemInfo: dict, keys: list
    ) -> DataFrame:
        """
        ディクショナリからPandasDataFrameを生成する

        Parameters
        ----------
        dfItemInfo : DataFrame
            取得データDataFrame
        dictItemInfo : dict
            取得データDictionary
        keys : list
            主キー情報
        """

        # ディクショナリの件数が0件の場合は列情報(DataFrame)のみ返す
        if len(dictItemInfo) == 0:
            return dfItemInfo

        # DictionaryをDataFrameに変換
        dfItemInfo = dfItemInfo.from_dict(dictItemInfo, orient="index")

        # 主キー指定して返す
        return dfItemInfo.set_index(keys, drop=False)
