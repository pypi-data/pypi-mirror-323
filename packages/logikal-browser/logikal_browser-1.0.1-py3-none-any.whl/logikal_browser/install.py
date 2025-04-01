from logikal_browser import Browser, BrowserVersion
from logikal_browser.chrome import ChromeBrowser
from logikal_browser.config import BROWSER_VERSIONS
from logikal_browser.edge import EdgeBrowser


class InstalledBrowser:  # pylint: disable=too-few-public-methods
    """
    Information related to an installed browser.

    Args:
        browser_name: The name of the browser to install.
        version: The browser version to install.

    """
    BROWSERS: dict[str, type[Browser]] = {
        'chrome': ChromeBrowser,
        'edge': EdgeBrowser,
    }

    def __init__(self, browser_name: str, version: str):
        try:
            #: The appropriate browser-specific :class:`~logikal_browser.Browser` sub-class.
            self.browser_class: type[Browser] = InstalledBrowser.BROWSERS[browser_name]
        except KeyError as error:
            raise RuntimeError(f'Browser "{browser_name}" is currently not supported') from error

        browser_version_class: type[BrowserVersion] = (
            self.browser_class.version_class  # type: ignore[assignment]
        )
        #: The installed browser-specific :class:`~logikal_browser.BrowserVersion` sub-class
        #: instance.
        self.browser_version: BrowserVersion = browser_version_class(version=version, install=True)


def install_all(versions: dict[str, str] | None = None) -> dict[str, InstalledBrowser]:
    """
    Install all specified browser versions.

    Args:
        versions: A mapping of browser names to versions to install.
            Defaults to :data:`~logikal_browser.config.BROWSER_VERSIONS`.

    """
    installed_browsers: dict[str, InstalledBrowser] = {}

    if not (versions := BROWSER_VERSIONS if versions is None else versions):
        raise RuntimeError('You must specify at least one browser version')

    for browser_name, version in sorted(versions.items()):
        installed_browsers[browser_name] = InstalledBrowser(
            browser_name=browser_name,
            version=version,
        )

    return installed_browsers
