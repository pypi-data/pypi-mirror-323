import random


class UserAgent:
    def __init__(self):
        self.browsers = ["Chrome", "Firefox", "Safari"]
        self.os_list = [
            "Windows NT 10.0; Win64; x64",
            "Linux; Android 10",
            "iPhone; CPU iPhone OS 14_6 like Mac OS X",
        ]
        self.browser_versions = {
            "Chrome": "Chrome/131.0.0.0",
            "Firefox": "Firefox/87.0",
            "Safari": "Safari/537.36",
        }

    def _generate_user_agent(self, browser):
        if browser not in self.browser_versions:
            raise ValueError(f"Browser '{browser}' is not supported.")
        os = random.choice(self.os_list)
        version = self.browser_versions[browser]
        return f"Mozilla/5.0 ({os}) AppleWebKit/537.36 (KHTML, like Gecko) {version} Safari/537.36"

    def chrome(self):
        return self._generate_user_agent("Chrome")

    def firefox(self):
        return self._generate_user_agent("Firefox")

    def safari(self):
        return self._generate_user_agent("Safari")

    def random_browser(self):
        browser = random.choice(self.browsers)
        return self._generate_user_agent(browser)

class XMsUserAgent:
    def __init__(self):
        self.sdk_names = ["azsdk-js-azure-storage-blob",
                          "azsdk-js-azure-keyvault", "azsdk-js-azure-eventhubs"]
        self.sdk_versions = ["12.24.0", "4.6.1", "5.12.0"]
        self.pipeline_versions = ["1.16.3", "1.15.0", "2.1.0"]
        self.browsers = ["Brave", "Edge", "Firefox"]
        self.browser_versions = ["132", "131", "130"]
        self.os_types = ["x86-Windows", "x64-Linux", "ARM-MacOS"]
        self.os_versions = ["15.0.0", "10.0.0", "13.1.0"]

    def _generate_xms_user_agent(self):
        sdk_name = random.choice(self.sdk_names)
        sdk_version = random.choice(self.sdk_versions)
        pipeline_version = random.choice(self.pipeline_versions)
        browser = random.choice(self.browsers)
        browser_version = random.choice(self.browser_versions)
        os_type = random.choice(self.os_types)
        os_version = random.choice(self.os_versions)

        return (
            f"{sdk_name}/{sdk_version} "
            f"core-rest-pipeline/{pipeline_version} "
            f"{browser}/{browser_version} "
            f"OS/{os_type}-{os_version}"
        )

    def random(self):
        return self._generate_xms_user_agent()