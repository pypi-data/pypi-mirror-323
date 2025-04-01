"""
Web inspect Scanner Class
"""

import logging
import tempfile
from pathlib import Path
from typing import Any, Iterator, List, Optional, Union, cast

from regscale.core.app.utils.file_utils import find_files, get_processed_file_path, iterate_files, move_file
from regscale.integrations.scanner_integration import IntegrationAsset, IntegrationFinding, ScannerIntegration
from regscale.models import ImportValidater, IssueSeverity, IssueStatus, regscale_models

logger = logging.getLogger("rich")
XML = "*.xml"


class WebInspectImport(ScannerIntegration):
    """Integration class for web inspect vulnerability scanning."""

    title = "Web Inspect"
    asset_identifier_field = "tenableId"
    finding_severity_map = {
        4: regscale_models.IssueSeverity.High,
        3: regscale_models.IssueSeverity.High,
        2: regscale_models.IssueSeverity.Moderate,
        1: regscale_models.IssueSeverity.Low,
        0: regscale_models.IssueSeverity.NotAssigned,
    }

    @staticmethod
    def _check_path(path: Optional[str] = None) -> None:
        """
        Check if the path is a valid file path.

        :param Optional[str] path: The path to check, defaults to None
        :raises ValueError: If the path is provided path is not provided
        :rtype: None
        """
        if not path:
            raise ValueError("Path must be provided")
        if not any(Path(path).glob(XML)):
            raise ValueError("Path must contain .xml files")

    @staticmethod
    def check_collection(file_collection: List[Union[Path, str]], path: str) -> bool:
        """
        Check if any files were found in the given path.

        :param List[Union[Path, str]] file_collection: List of Path objects for .XML files or S3 URIs
        :param str path: Path to a .XML file or a folder containing XML files
        :return: boolean indicating if any XML files were found
        :rtype: bool
        """
        res = True
        if len(file_collection) == 0:
            logger.warning("No XML files found in path %s", path)
            res = False
        return res

    def fetch_findings(self, *args: Any, **kwargs: dict) -> Iterator[IntegrationFinding]:
        """
        Fetches findings from the XML files

        :return: A list of findings
        :rtype: List[IntegrationFinding]
        """
        path: Optional[str] = cast(Optional[str], kwargs.get("folder_path"))
        self._check_path(path)
        file_collection = find_files(path, XML)
        if self.check_collection(file_collection, path):
            for file in iterate_files(file_collection):
                content = ImportValidater(
                    file_path=file,
                    disable_mapping=True,
                    xml_tag="Scan",
                    required_headers=[],
                    mapping_file_path=tempfile.gettempdir(),
                ).data
                # Get a list of issues from xml node Issues
                issues_dict = content.get("Issues", {}).get("Issue", [])
                for issue in issues_dict:
                    if res := self.parse_finding(issue):
                        yield res
        self.move_files(file_collection)

    def fetch_assets(self, *args, **kwargs) -> Iterator[IntegrationAsset]:  # type: ignore
        """
        Fetches assets from the processed XML files

        :yields: Iterator[IntegrationAsset]
        """
        path = kwargs.get("folder_path")
        file_collection = find_files(path, XML)
        if self.check_collection(file_collection, path):
            for file in iterate_files(file_collection):
                content = ImportValidater(
                    file_path=file,
                    disable_mapping=True,
                    xml_tag="Scan",
                    required_headers=[],
                    mapping_file_path=tempfile.gettempdir(),
                ).data
                # Get a list of issues from xml node Issues
                issues_dict = content.get("Issues", {}).get("Issue", [])
                for issue in issues_dict:
                    yield from self.parse_asset(issue)

    @staticmethod
    def parse_asset(issue: dict):
        """
        Parse the asset from an element

        :param dict issue: The Issue element
        :yields: IntegrationAsset
        """
        host = issue.get("Host")
        if host:
            yield IntegrationAsset(name=host, asset_type="Other", asset_category="Hardware", identifier=host)

    @staticmethod
    def _parse_report_section(sections: List[dict], section_name: str) -> str:
        """
        Extract text from a specific report section.

        :param List[dict] sections: List of report sections
        :param str section_name: Name of the section to extract text from
        :return: Text from the specified section
        :rtype: str
        """
        return next((section.get("SectionText", "") for section in sections if section.get("Name") == section_name), "")

    def parse_finding(self, issue: dict) -> Optional[IntegrationFinding]:
        """
        Parse the dict to an Integration Finding

        :param dict issue: The Issue element
        :returns The Integration Finding
        :rtype Optional[IntegrationFinding]
        """
        severity_int = int(issue.get("Severity", 0))
        severity = self.finding_severity_map.get(severity_int, IssueSeverity.NotAssigned)
        title = issue.get("Name", "")
        host = issue.get("Host", "")
        plugin_id = issue.get("VulnerabilityID", "")
        external_id = str(host + plugin_id)
        sections = issue.get("ReportSection")
        description = self._parse_report_section(sections, "Summary")
        mitigation = self._parse_report_section(sections, "Fix")

        if severity in (IssueSeverity.High, IssueSeverity.Moderate, IssueSeverity.Low):
            return IntegrationFinding(
                external_id=external_id,
                asset_identifier=host,
                control_labels=[],
                description=description,
                status=IssueStatus.Open,
                title=title,
                severity=severity,
                severity_int=severity_int,
                category=f"{self.title} Vulnerability",
                plugin_id=plugin_id,
                plugin_name=title,
                rule_id=plugin_id,
                recommendation_for_mitigation=mitigation,
                source_report=self.title,
            )
        return None

    @staticmethod
    def move_files(file_collection: List[Union[Path, str]]) -> None:
        """
        Move the list of files to a folder called 'processed' in the same directory.

        :param List[Union[Path, str]] file_collection: List of file paths or S3 URIs
        :rtype: None
        """
        for file in file_collection:
            new_file = get_processed_file_path(file)
            move_file(file, new_file)
            logger.info("Moved XML file %s to %s", file, new_file)
