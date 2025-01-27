from osbot_utils.type_safe.Type_Safe import Type_Safe

from osbot_playwright.playwright.api.Playwright_CLI import Playwright_CLI
from osbot_utils.utils.Files import file_exists, path_combine, files_list


class Playwright__Install_Check(Type_Safe):
    playwright_cli: Playwright_CLI

    def browser__install_check(self):
        with self.playwright_cli as _:
            path_to_chrome                 = _.install_location('chromium')
            path_to_ffmpeg                 = path_combine(path_to_chrome             , '../ffmpeg-1010'         )
            chrome__dependencies_validated = file_exists (path_combine(path_to_chrome, 'DEPENDENCIES_VALIDATED'))
            chrome__installation_complete  = file_exists (path_combine(path_to_chrome, 'INSTALLATION_COMPLETE' ))
            ffmpeg__installation_complete  = file_exists (path_combine(path_to_ffmpeg, 'INSTALLATION_COMPLETE' ))
            installed_ok                   = chrome__dependencies_validated and chrome__installation_complete and ffmpeg__installation_complete
            return dict(chrome__dependencies_validated = chrome__dependencies_validated,
                        chrome__installation_complete  = chrome__installation_complete ,
                        ffmpeg__installation_complete  = ffmpeg__installation_complete ,
                        installed_ok                   = installed_ok                  )

