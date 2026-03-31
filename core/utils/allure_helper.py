import json
import os
from typing import Any, Dict, Optional

import allure


class AllureHelper:

    @staticmethod
    def attach_screenshot(file_path: str, name: str = "screenshot") -> None:
        if os.path.exists(file_path):
            with open(file_path, "rb") as f:
                allure.attach(f.read(), name=name, attachment_type=allure.attachment_type.PNG)

    @staticmethod
    def attach_text(text: str, name: str = "text", attachment_type: Optional[str] = None) -> None:
        allure.attach(
            text, name=name, attachment_type=attachment_type or allure.attachment_type.TEXT
        )

    @staticmethod
    def attach_json(json_data: Any, name: str = "json") -> None:
        if isinstance(json_data, dict):
            json_str = json.dumps(json_data, ensure_ascii=False, indent=2)
        else:
            json_str = str(json_data)
        allure.attach(json_str, name=name, attachment_type=allure.attachment_type.JSON)

    @staticmethod
    def attach_html(html_data: str, name: str = "html") -> None:
        allure.attach(html_data, name=name, attachment_type=allure.attachment_type.HTML)

    @staticmethod
    def attach_video(file_path: str, name: str = "video") -> None:
        if os.path.exists(file_path):
            with open(file_path, "rb") as f:
                allure.attach(f.read(), name=name, attachment_type=allure.attachment_type.WEBM)

    @staticmethod
    def attach_file(file_path: str, name: str, attachment_type: Any) -> None:
        if os.path.exists(file_path):
            with open(file_path, "rb") as f:
                allure.attach(f.read(), name=name, attachment_type=attachment_type)

    @staticmethod
    def add_tags(*tags: str) -> None:
        for tag in tags:
            allure.tag(tag)

    @staticmethod
    def add_severity(severity: str) -> None:
        severity_map = {
            "blocker": allure.severity_level.BLOCKER,
            "critical": allure.severity_level.CRITICAL,
            "normal": allure.severity_level.NORMAL,
            "minor": allure.severity_level.MINOR,
            "trivial": allure.severity_level.TRIVIAL,
        }
        allure.severity(severity_map.get(severity, allure.severity_level.NORMAL))

    @staticmethod
    def add_feature(feature: str) -> None:
        allure.feature(feature)

    @staticmethod
    def add_story(story: str) -> None:
        allure.story(story)

    @staticmethod
    def add_description(description: str) -> None:
        allure.description(description)

    @staticmethod
    def add_description_html(description: str) -> None:
        allure.description_html(description)

    @staticmethod
    def add_link(url: str, name: str, link_type: str = "link") -> None:
        allure.link(url, name=name, link_type=link_type)

    @staticmethod
    def add_issue(url: str, name: str) -> None:
        allure.issue(url, name=name)

    @staticmethod
    def add_test_case(url: str, name: str) -> None:
        allure.testcase(url, name=name)

    @staticmethod
    def add_parameter(name: str, value: Any) -> None:
        allure.dynamic.parameter(name, value)

    @staticmethod
    def add_parameters(parameters: Dict[str, Any]) -> None:
        for name, value in parameters.items():
            allure.dynamic.parameter(name, value)

    @staticmethod
    def step(name: str) -> Any:
        return allure.step(name)

    @staticmethod
    def epic(name: str) -> None:
        allure.epic(name)

    @staticmethod
    def suite(name: str) -> None:
        allure.suite(name)

    @staticmethod
    def parent_suite(name: str) -> None:
        allure.parent_suite(name)

    @staticmethod
    def sub_suite(name: str) -> None:
        allure.sub_suite(name)
