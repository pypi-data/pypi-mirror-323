from playwright.sync_api import sync_playwright
from .gg_api.y4a_drive import upload_file_to_gdrive
from .y4a_retry import retry_on_error
import time  
from .y4a_credentials import get_credentials


import logging
import warnings

warnings.filterwarnings("ignore", category=UserWarning)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)

class DashboardService:
    '''
        Use for screenshot dashboard or get dashboard pdf

        :param acc_name: The account name of power bi account
        :param acc_password: The password of power bi account
        :param creds_ggdrive: The service account credentials
        :param parent_directory_id: Id of the folder containing folder_name
        :param executable_path: The executable_path of playwright
        :param path_file: The directory where to get file, defauld is tmp

    '''
    def __init__(
        self, 
        acc_name: str, 
        acc_password: str, 
        parent_directory_id: str, 
        executable_path: str = "/home/airflow/.cache/ms-playwright/chromium-1080/chrome-linux/chrome", 
        path_file: str = "/tmp/",
        creds_ggdrive: dict = None,
    ):
        self.__acc_name = acc_name
        self.__acc_password = acc_password
        self.__parent_directory_id = parent_directory_id
        self.__executable_path = executable_path
        self.__path_file = path_file
        if creds_ggdrive == None:
            self.__creds_ggdrive = get_credentials(
                platform="gg_api",
                account_name="da_full"
            )
        else:
            self.__creds_ggdrive = creds_ggdrive
    
    @retry_on_error(delay=20)
    def get_pdf_dashboard_get_link(
        self, 
        dashboard_url: str,
        is_only_current_page: bool = True
    ) -> str:
        self.__is_only_current_page = is_only_current_page
        self.__dashboard_url = dashboard_url

        """
            :param dashboard_url: The url of dashboard want to get pdf
            :param is_only_current_page: default is True, get all page of dashboard
        """


        file_name = self.__run_get_pdf() 
        gg_drive_file = upload_file_to_gdrive("Dashboard_PDF_File", self.__parent_directory_id, self.__path_file,file_name, self.__creds_ggdrive)

        return gg_drive_file
    

    @retry_on_error(delay=20)
    def screenshot_dashboard_get_image_link(
        self, 
        dashboard_embed_url: str,
        height: float, 
        width: float
    ) -> str:
        self.__dashboard_embed_url = dashboard_embed_url
        self.__height = height
        self.__width = width

        """
            :param dashboard_embed_url: The embed url of dashboard want to screenshot. File -> Embed report -> Website or portal -> Copy the embed link
            :param height: The height of screen capture
            :param width: The width of screen capture
        """

        file_name = self.__run_screenshot() 
        gg_drive_file = upload_file_to_gdrive("Dashboard_Image_File", self.__parent_directory_id, self.__path_file,file_name,  self.__creds_ggdrive)

        return gg_drive_file
    

    # private function

    def __run_get_pdf(self):
        with sync_playwright() as playwright:
            return self.__get_pdf_file(playwright, self.__dashboard_url, self.__is_only_current_page)
        
    def __run_screenshot(self):
        with sync_playwright() as playwright:            
            return self.__screenshot(playwright, self.__dashboard_embed_url, self.__height, self.__width)

    def __get_pdf_file(self, playwright, url, is_only_current_page):
        logging.info("-------start get file")

        # step 1: go to page and wait
        logging.info("-------waiting")

        browser = playwright.chromium.launch(executable_path=self.__executable_path)
        context = browser.new_context()  

        page = context.new_page()
    
        logging.info("-------step 1")

        page.goto(url)
        page.wait_for_timeout(3000)

        logging.info("-------step 2")

        input_selector = 'input[id="email"]'
        page.fill(input_selector, self.__acc_name)
        button_id = 'submitBtn'
        page.click(f'#{button_id}')

        page.wait_for_timeout(5000)

        logging.info("-------step 3")

        input_selector = 'input[id="i0118"]'
        page.fill(input_selector, self.__acc_password)
        button_id = 'idSIButton9'
        page.click(f'#{button_id}')

        page.wait_for_timeout(5000)

        logging.info("-------step 4")

        button_id = 'idBtn_Back'
        page.click(f'#{button_id}')

        page.wait_for_selector('#exportMenuBtn')

        button_id = 'exportMenuBtn'
        page.click(f'#{button_id}')

        logging.info("-------step 5")

        page.wait_for_selector('[data-testid="export-to-pdf-btn"]')
        page.click('[data-testid="export-to-pdf-btn"]')

        page.wait_for_timeout(1500)

        logging.info("-------step 6")

        page.wait_for_selector('#okButton')
        if is_only_current_page:
            page.evaluate('''() => {
            const checkbox = document.getElementById("$pbi-checkbox-1");
            if (checkbox) {
                checkbox.click();
            }
        }''')

        with page.expect_download(timeout=240000) as download_info:
            page.click('#okButton')

        download = download_info.value

        nano_time = time.time_ns() 
        file_name = f'gpdf_{nano_time}_{download.suggested_filename}'
        download.save_as(f'{self.__path_file}{file_name}')

        page.wait_for_timeout(3000)

        page.wait_for_selector('[data-testid="toast-notification-title"]')
        page.wait_for_timeout(2000)
        page.wait_for_selector('[data-testid="toast-notification-title"]', state="detached", timeout=120000)

        page.wait_for_timeout(1000)

        return file_name
    

    def __screenshot(self, playwright, url, height, width):
        logging.info("-------start screenshot")

        # step 1: go to page and wait
        logging.info("-------waiting")

        browser = playwright.chromium.launch(executable_path=self.__executable_path)
        page = browser.new_page()
        page.set_viewport_size({"width": width, "height": height})
        page.goto(url)
        page.wait_for_selector('input[name="loginfmt"]')
        page.wait_for_timeout(1500)

        # step 2: input the login account
        input_selector = 'input[name="loginfmt"]'
        page.fill(input_selector, self.__acc_name)
        button_id = 'idSIButton9'
        page.click(f'#{button_id}')
        page.wait_for_timeout(1500)

        
        # step 3: input the password account
        page.wait_for_selector('input[name="passwd"]')
        input_selector_pass = 'input[name="passwd"]'
        page.fill(input_selector_pass, self.__acc_password)
        button_id = 'idSIButton9'
        page.click(f'#{button_id}')
        page.wait_for_timeout(1500)

        # step 4: confirm no
        page.wait_for_selector('#idBtn_Back')
        button_id = 'idBtn_Back'
        page.click(f'#{button_id}')
        page.wait_for_timeout(1500) 

        # step 5: hidden filter
        # page.wait_for_selector('.btn.collapseIcon.pbi-borderless-button.glyphicon.glyph-mini.pbi-glyph-doublechevronright')
        page.wait_for_timeout(3000)
        page.evaluate("() => { const element = document.querySelector('[data-automation-type=\"outspacePane\"]'); if (element) element.style.display = 'none'; }")

        # step 6: final
        page.wait_for_timeout(10000)
        nano_time = time.time_ns() 
        file_name = f'ss_img_{nano_time}.png'
        page.screenshot(path=f'{self.__path_file}{file_name}')

        # always close the browser
        page.close()
        browser.close()
        logging.info("-------done")

        return file_name
