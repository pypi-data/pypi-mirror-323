"""
Module for processing Trivy scan results and loading them into RegScale.
"""

import json
import logging
import traceback
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List, Union

import click

from regscale.core.app.api import Api
from regscale.core.app.utils.file_utils import (
    find_files,
    read_file,
    move_file,
    get_processed_file_path,
    iterate_files,
    download_from_s3,
)
from regscale.integrations.scanner_integration import ScannerIntegration, IntegrationAsset, IntegrationFinding
from regscale.models.regscale_models import (
    Property,
    IssueSeverity,
    AssetStatus,
    IssueStatus,
)

logger = logging.getLogger(__name__)


class TrivyProcessingError(Exception):
    """Custom exception for Trivy processing errors."""

    pass


class TrivyIntegration(ScannerIntegration):
    """Class for handling Trivy scanner integration."""

    title = "TrivyIntegration"
    scanner_name = "Trivy"
    plan_id = None
    file_path = None
    asset_identifier_field = "otherTrackingNumber"
    owner_id = None
    scan_date = None
    data = {}

    def __init__(self, plan_id: int, **kwargs: Any):
        self.plan_id = plan_id
        self.api = Api()
        self.config = self.api.config
        self.owner_id = self.config.get("userId")
        self.assessor_id = self.config.get("userId")
        self.scan_date = kwargs.get("scan_date") if kwargs.get("scan_date") else datetime.now().isoformat()
        self.identifier = None
        if "data" in kwargs:
            self.data = kwargs.get("data")
        """Initialize the Trivy integration."""
        super().__init__(plan_id=plan_id)

    def create_properties(self, issue_id: str, vuln_data: Dict[str, Any], scan_data: Dict[str, Any]) -> None:
        """
        Create property records associated with an issue.

        Args:
            issue_id (str): ID of the associated issue
            vuln_data (Dict[str, Any]): The vulnerability data from Trivy
            scan_data (Dict[str, Any]): The complete scan data
        """
        try:
            # Add relevant properties from vuln_data
            for key, value in vuln_data.items():
                if key not in [
                    "VulnerabilityID",
                    "PkgName",
                    "InstalledVersion",
                    "FixedVersion",
                    "Title",
                    "Severity",
                    "Description",
                    "References",
                ]:
                    prop = Property()
                    prop.issue_id = issue_id
                    prop.key = key
                    prop.value = str(value)
                    prop.save()
        except Exception as e:
            logger.error(f"Error creating properties: {str(e)}")

    def fetch_findings(self, **kwargs) -> List[IntegrationFinding]:
        """
        Fetch findings from Trivy scan data.
        :param self:
        :param finding_data:
        :return: List of IntegrationFinding
        :rtype: List[IntegrationFinding]
        """

        self.scan_date = kwargs.get("scan_date")
        self.data = kwargs.get("data")
        self.identifier = self.data.get("Metadata", {}).get("ImageID")
        findings = []
        try:
            for item in self.data.get("Results", []):
                for finding in item.get("Vulnerabilities", []):
                    findings.append(
                        IntegrationFinding(
                            title=finding.get("Title", finding.get("PkgName")),
                            description=finding.get("Description", "No description available"),
                            severity=(
                                self.process_severity(finding.get("Severity"))
                                if finding.get("Severity")
                                else IssueSeverity.NotAssigned.value
                            ),
                            status=IssueStatus.Open.value,
                            cvss_v3_score=self.get_cvss_score(finding),
                            cvs_sv3_base_score=self.get_cvss_score(finding),
                            plugin_name=finding.get("DataSource", {}).get("Name", "Trivy"),
                            plugin_id=finding.get("DataSource", {}).get("ID", "Trivy"),
                            asset_identifier=self.identifier,
                            cve=finding.get("VulnerabilityID"),
                            first_seen=self.scan_date,
                            last_seen=self.scan_date,
                            scan_date=self.scan_date,
                            category="Software",
                            control_labels=[],
                        )
                    )

            return findings
        except Exception:
            error_message = traceback.format_exc()
            logger.error(f"Error fetching findings: {error_message}")
            raise TrivyProcessingError(f"Error fetching findings: {error_message}")

    @staticmethod
    def process_severity(severity: str) -> str:
        """
        Process the severity of a finding.
        :param severity:
        :return:
        """
        severity_level = {
            "CRITICAL": IssueSeverity.High.value,
            "HIGH": IssueSeverity.High.value,
            "MEDIUM": IssueSeverity.Moderate.value,
            "LOW": IssueSeverity.Low.value,
            "UNKNOWN": IssueSeverity.NotAssigned.value,
            "NEGLIGIBLE": IssueSeverity.Low.value,
        }
        return severity_level.get(severity.upper(), IssueSeverity.NotAssigned.value)

    @staticmethod
    def process_status(status: str) -> IssueStatus:
        """
        Process the status of a finding.
        :param status: The status of the finding
        :return: The processed status
        """
        if status.lower() == "fixed":
            return IssueStatus.Closed.value
        else:
            return IssueStatus.Open.value

    @staticmethod
    def get_cvss_score(finding: Dict) -> float:
        """
        Get the CVSS score from the finding data.
        :param finding:
        :return:
        """
        value = 0.0
        if cvs := finding.get("CVSS"):
            if nvd := cvs.get("nvd"):
                value = nvd.get("V3Score", 0.0)
            elif redhat := cvs.get("redhat"):
                value = redhat.get("V3Score", 0.0)
        return value

    def fetch_assets(self, **kwargs) -> List[IntegrationAsset]:
        """
        Fetch assets from Trivy scan data.
        :param List[Dict] data: integration data
        :return: List of IntegrationAsset
        :rtype: List[IntegrationAsset]
        """
        self.scan_date = kwargs.get("scan_date")
        data = kwargs.get("data")
        assets: List[IntegrationAsset] = []
        try:
            self.identifier = data.get("Metadata", {}).get("ImageID")
            assets.append(
                IntegrationAsset(
                    identifier=self.identifier,
                    name=data.get("ArtifactName"),
                    ip_address="0.0.0.0",
                    cpu=0,
                    ram=0,
                    status=AssetStatus.Active.value,
                    asset_owner_id=self.owner_id,
                    asset_type="Other",
                    asset_category="Software",
                    operating_system=f"{data['Metadata']['OS']['Family']} {data['Metadata']['OS']['Name']}",
                    parent_id=self.plan_id,
                    parent_module="securityplans",
                    notes="Trivy",
                )
            )
            return assets
        except Exception:
            error_message = traceback.format_exc()
            logger.error(f"Error fetching assets: {error_message}")
            raise TrivyProcessingError(f"Error fetching assets: {error_message}")


@click.group()
def trivy():
    """Performs actions from the Trivy scanner integration."""
    pass


@trivy.command("import_scans")
@click.option("--file_path", "-f", type=click.Path(exists=True, dir_okay=True), required=False)
@click.option("--ssp_id", "-s", type=int, required=True)
@click.option("--destination", "-d", type=click.Path(exists=True, dir_okay=True), required=False)
@click.option("--file_pattern", "-p", type=str, required=False, default="trivy*.json")
@click.option(
    "--s3-bucket",
    "-b",
    help="S3 bucket to download scan files from",
    type=str,
    required=False,
)
@click.option(
    "--s3-prefix",
    "-pre",
    help="Prefix (folder path) within the S3 bucket",
    type=str,
    required=False,
)
@click.option(
    "--aws-profile",
    "-pro",
    help="AWS profile to use for S3 access",
    type=str,
    required=False,
)
def import_scans(
    file_path: Path,
    ssp_id: int,
    destination: Optional[Path],
    file_pattern: str,
    s3_bucket: str,
    s3_prefix: str,
    aws_profile: str,
) -> None:
    """
    Process Trivy scan results from a folder container trivy scan files and load into RegScale.

    :param ssp_id: RegScale SSP ID
    :param file_pattern: The file pattern to search for in the file path Default: trivy*.json
    :param destination: The destination folder for the processed files
    :param file_path: Path to the Trivy scan results JSON file
    :param s3_bucket: S3 bucket to download scan files from
    :param s3_prefix: Prefix (folder path) within the S3 bucket
    :param aws_profile: AWS profile to use for S3 access
    """
    try:
        files = []
        if s3_bucket and s3_prefix and aws_profile:
            download_from_s3(bucket=s3_bucket, prefix=s3_prefix, local_path=destination, aws_profile=aws_profile)
            files = find_files(path=destination, pattern=file_pattern)
            logger.info("Downloaded all Trivy scan files from S3. Processing...")
        elif destination and not s3_bucket:
            logger.info("Moving Trivy scan files to %s", destination)
            stored_file_collection = find_files(path=file_path, pattern=file_pattern)
            move_all_files(stored_file_collection, destination)
            files = find_files(path=destination, pattern=file_pattern)
            logger.info("Done moving files")
        else:
            stored_file_collection = find_files(path=file_path, pattern=file_pattern)
            files = stored_file_collection
        if not files:
            logger.error("No Trivy scan results found in the specified directory")
            return

        for file in files:
            data = json.loads(read_file(file))
            scan_date = data.get("CreatedAt") if data.get("CreatedAt") else datetime.now().isoformat()
            integration = TrivyIntegration(plan_id=ssp_id, scan_date=scan_date, data=data)
            integration.identifier = data.get("ArtifactName", {})
            integration.sync_assets(plan_id=ssp_id, data=data, scan_date=scan_date)
            integration.sync_findings(plan_id=ssp_id, data=data, scan_date=scan_date)
        logger.info("Done processing Trivy scan results moving files to %s", destination)
        move_trivy_files(file_path=destination, file_pattern=file_pattern)
        logger.info("Completed Trivy processing.")
    except Exception as e:
        logger.error(f"Error processing Trivy results: {str(e)}")
        logger.error(traceback.format_exc())
        raise TrivyProcessingError(f"Failed to process Trivy results: {str(e)}")


def move_all_files(file_collection: List[Union[Path, str]], destination: Union[Path, str]) -> None:
    """
    Move all Trivy files in the current directory to a folder called 'processed'.

    :param List[Union[Path, str]] file_collection: A list of file paths or S3 URIs
    :param Union[Path, str] destination: The destination folder
    :return: None
    :rtype: None
    """
    for file in iterate_files(file_collection):
        file_path = Path(file)
        new_filename = f"{file_path.stem}{file_path.suffix}"
        new_file_path = Path(destination) / new_filename
        move_file(file, new_file_path)


def move_trivy_files(file_path: Union[Path, str], file_pattern: str) -> None:
    """
    Move the a files to a folder called 'processed' in the same directory.

    :param Union[Path, str] file: A file paths or S3 URIs
    :param str file_pattern: The file pattern to search for in the file path
    """
    file_collection = find_files(path=file_path, pattern=file_pattern)
    for file in iterate_files(file_collection):
        new_file = get_processed_file_path(file)
        move_file(file, new_file)
        logger.debug("Moved Trivy file %s to %s", file, new_file)
