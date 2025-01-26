from LibHanger.Library.uwConfig import cmnConfig
from LibHanger.Library.uwGlobals import *
from enum import IntEnum

class scrapingConfig(cmnConfig):

    """
    scrapinger共通設定クラス(scrapingConfig)
    """ 
    
    class settingValueStruct(cmnConfig.settingValueStruct):
        
        """
        設定値構造体
        """ 
            
        class ScrapingType(IntEnum):
            
            """
            スクレイピング方法
            """ 
            
            unknown = 0
            """ unknown """
            
            selenium = 1
            """ for selenium """ 

            beutifulSoup = 2
            """ for beutifulSoup """ 
            
        class BrowserType(IntEnum):
        
            """
            ブラウザータイプ
            """ 
            
            chrome = 1
            """ Google Chrome """

            firefox = 2
            """ FireFox """

            edge = 3
            """ Microsoft Edge """

        class WebDriverPath:
            
            """
            WebDriverパス
            """ 
            
            WebDriverPathWin = ''
            """ WebDriverパス for windows """

            WebDriverPathLinux = ''
            """ WebDriverパス for linux """

            WebDriverPathMac = ''
            """ WebDriverパス for mac """

            WebDriverLogPath = ''
            """ WebDriverログ出力先パス """
            
            WebDriverPath = ''
            """ WebDriverパス """
            
            def __init__(self):
                
                """ 
                コンストラクタ
                """ 

                # メンバ変数初期化
                self.WebDriverPathWin = ''
                self.WebDriverPathLinux = ''
                self.WebDriverPathMac = ''
                self.WebDriverLogPath = ''
                
    def __init__(self):
        
        """ 
        コンストラクタ
        """ 
        
        # 基底側のコンストラクタ呼び出し
        super().__init__()
        
        self.UserEgent_Mozilla = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
        """ ユーザーエージェント Mozilla """

        self.UserEgent_AppleWebKit = 'AppleWebKit/537.36 (KHTML, like Gecko)'
        """ ユーザーエージェント AppleWebKit """

        self.UserEgent_Chrome = 'Chrome/94.0.4606.61 Safari/537.36'
        """ ユーザーエージェント Chrome """

        self.ScrapingType:int = self.settingValueStruct.ScrapingType.selenium
        """ スクレイピング方法 """

        self.BrowserType:int = self.settingValueStruct.BrowserType.chrome
        """ ブラウザータイプ """
        
        self.DelayTime:int = 2
        """ 1ページ読み込むごとに発生する待機時間(秒) """

        self.ItemTagName = '.ItemGrid__ItemGridCell-sc-14pfel3-1'
        """ 商品タグCSSクラス名(bs用) """
        
        self.DelayWaitElement = 'div-eagle-search-1580185158495-0'
        """ 指定されたエレメントがDOMに発生するまで待機する(WebDriver用) """
    
        self.WebDriverTimeout:int = 10
        """ Webドライバーのタイムアウト時間(秒) """
        
        self.WebDriverOptions = []
        """ Webドライバーオプション """
        
        self.PageLoadRetryCount:int = 50
        """ ページ読み込み処理の最大リトライ回数 """
        
        self.PageLoadStrategy = 'none'
        """ ページロード設定(none,normal,eagerのいずれか) """
        
        self.chrome = self.settingValueStruct.WebDriverPath()
        """ Chrome-Webドライバーパス(列挙体) """
        
        self.chrome.WebDriverPathWin = ''
        """ Chrome-Webドライバーパス(Windows) """

        self.chrome.WebDriverPathLinux = ''
        """ Chrome-Webドライバーパス(Linux) """

        self.chrome.WebDriverPathMac = ''
        """ Chrome-Webドライバーパス(Mac) """

        self.chrome.WebDriverLogPath = ''
        """ Chrome-Webドライバーログ出力先パス """
        
        self.firefox = self.settingValueStruct.WebDriverPath()
        """ Firefox-Webドライバーパス(列挙体) """
        
        self.firefox.WebDriverPathWin = ''
        """ Firefox-Webドライバーパス(Windows) """

        self.firefox.WebDriverPathLinux = ''
        """ Firefox-Webドライバーパス(Linux) """

        self.firefox.WebDriverPathMac = ''
        """ Firefox-Webドライバーパス(Mac) """

        self.firefox.WebDriverLogPath = ''
        """ Firefox-Webドライバーログ出力先パス """

        # 設定ファイル追加
        self.setConfigFileName('Scrapinger.ini')

    def getConfig(self, _scriptFilePath: str, configFileDir: str = ''):
        
        # 基底側のiniファイル読込
        super().getConfig(_scriptFilePath, configFileDir)
        
    def setInstanceMemberValues(self):
        
        """ 
        インスタンス変数に読み取った設定値をセットする
        """
        
        # 基底側setInstanceMemberValues
        super().setInstanceMemberValues()
        
        # ユーザーエージェント Mozilla
        self.setConfigValue('UserEgent_Mozilla',self.config_ini,'USER_EGENT','USEREGENT_MOZILLA',str)

        # ユーザーエージェント AppleWebKit
        self.setConfigValue('UserEgent_AppleWebKit',self.config_ini,'USER_EGENT','USEREGENT_APPLEWEBKIT',str)

        # ユーザーエージェント Chrome
        self.setConfigValue('UserEgent_Chrome',self.config_ini,'USER_EGENT','USEREGENT_CHROME',str)

        # スクレイピング方法
        self.setConfigValue('ScrapingType',self.config_ini,'SITE','SCRAPING_TYPE',int)

        # ブラウザータイプ
        self.setConfigValue('BrowserType',self.config_ini,'SITE','BROWSER_TYPE',int)

        # 待機時間
        self.setConfigValue('DelayTime',self.config_ini,'SITE','DELAY_TIME',int)

        # Webドライバータイムアウト(秒)
        self.setConfigValue('WebDriverTimeout', self.config_ini,'SITE','WEBDRIVER_TIMEOUT',int)

        # Webドライバーオプション
        self.setConfigValue('WebDriverOptions', self.config_ini,'SITE','WEBDRIVER_OPTIONS',list)

        # ページ読み込み処理の最大リトライ回数
        self.setConfigValue('PageLoadRetryCount', self.config_ini,'SITE','PAGELOAD_RETRYCOUNT',int)

        # ページ読み込み処理の待機の無効/有効
        self.setConfigValue('PageLoadStrategy', self.config_ini,'SITE','PAGELOAD_STRATEGY',str)

        # 商品タグCSS名
        self.setConfigValue('ItemTagName', self.config_ini,'SITE','ITEM_TAG_NAME',str)

        # 指定されたエレメントがDOMに発生するまで待機する
        self.setConfigValue('DelayWaitElement', self.config_ini,'SITE','DELAY_WAIT_ELEMENT',str)
                
        # Chrome-WebDriverパス(Windows)
        self.setConfigValue('chrome.WebDriverPathWin', self.config_ini,'WEBDRIVER-CHROME','CHR_WEBDRIVER_PATH_WIN',str)

        # Chrome-WebDriverパス(Linux)
        self.setConfigValue('chrome.WebDriverPathLinux', self.config_ini,'WEBDRIVER-CHROME','CHR_WEBDRIVER_PATH_LINUX',str)

        # Chrome-WebDriverパス(Mac)
        self.setConfigValue('chrome.WebDriverPathMac', self.config_ini,'WEBDRIVER-CHROME','CHR_WEBDRIVER_PATH_MAC',str)

        # Chrome-WebDriverログ出力先パス
        self.setConfigValue('chrome.WebDriverLogPath', self.config_ini,'WEBDRIVER-CHROME','CHR_WEBDRIVER_LOGPATH',str)
    
        # Firefox-WebDriverパス(Windows)
        self.setConfigValue('firefox.WebDriverPathWin', self.config_ini,'WEBDRIVER-FIREFOX','FOX_WEBDRIVER_PATH_WIN',str)

        # Firefox-WebDriverパス(Linux)
        self.setConfigValue('firefox.WebDriverPathLinux', self.config_ini,'WEBDRIVER-FIREFOX','FOX_WEBDRIVER_PATH_LINUX',str)

        # Firefox-WebDriverパス(Mac)
        self.setConfigValue('firefox.WebDriverPathMac', self.config_ini,'WEBDRIVER-FIREFOX','FOX_WEBDRIVER_PATH_MAC',str)

        # Firefox-WebDriverログ出力先パス
        self.setConfigValue('firefox.WebDriverLogPath', self.config_ini,'WEBDRIVER-FIREFOX','FOX_WEBDRIVER_LOGPATH',str)
