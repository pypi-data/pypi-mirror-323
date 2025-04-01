"""
Module for processing Grype scan results and loading them into RegScale.
"""

import json
import logging
import traceback
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Union

import click

from regscale.core.app.api import Api
from regscale.core.app.utils.file_utils import (
    find_files,
    read_file,
    iterate_files,
    get_processed_file_path,
    move_file,
    download_from_s3,
)
from regscale.integrations.scanner_integration import ScannerIntegration, IntegrationAsset, IntegrationFinding
from regscale.models.regscale_models import (
    IssueSeverity,
    AssetStatus,
    IssueStatus,
)

logger = logging.getLogger(__name__)


class GrypeProcessingError(Exception):
    """Custom exception for Grype processing errors."""

    pass


class GrypeIntegration(ScannerIntegration):
    """Class for handling Grype scanner integration."""

    title = "GrypeIntegration"
    scanner_name = "Grype"
    plan_id = None
    file_path = None
    asset_identifier_field = "otherTrackingNumber"
    owner_id = None
    scan_date = None
    data = {}
    name = None
    identifier = None
    os = "Linux"

    def __init__(self, plan_id: int, **kwargs: Any):
        self.plan_id = plan_id
        self.api = Api()
        self.config = self.api.config
        self.owner_id = self.config.get("userId")
        self.assessor_id = self.config.get("userId")
        self.scan_date = kwargs.get("scan_date") if kwargs.get("scan_date") else datetime.now().isoformat()
        if "data" in kwargs:
            self.data = kwargs.get("data")
        if "identifier" in kwargs:
            self.identifier = kwargs.get("identifier")
        """Initialize the Grype integration."""
        super().__init__(plan_id=plan_id)

    def fetch_findings(self, **kwargs) -> List[IntegrationFinding]:
        """
        Fetch findings from Grype scan data.
        :param self:
        :param finding_data:
        :return: List of IntegrationFinding
        :rtype: List[IntegrationFinding]
        """

        self.scan_date = kwargs.get("scan_date")
        self.data = kwargs.get("data")
        self.identifier = kwargs.get("identifier")

        findings = []
        try:
            for item in self.data:
                finding = item.get("vulnerability", {})
                cve_id = finding.get("id")
                artifact = item.get("artifact", {})
                cvss = finding.get("cvss", [])
                related_vulns = item.get("relatedVulnerabilities", [])
                description = "No description available"
                if related_vulns:
                    for v in related_vulns:
                        if v.get("id") == cve_id:
                            description = v.get("description", "No description available")
                            cvss = v.get("cvss", [])
                            break

                findings.append(
                    IntegrationFinding(
                        title=artifact.get("name", "unknown"),
                        description=description,
                        severity=(
                            self.process_severity(finding.get("severity"))
                            if finding.get("severity")
                            else IssueSeverity.NotAssigned.value
                        ),
                        status=IssueStatus.Open.value,
                        cvss_v3_score=self.get_cvss_score(cvss_list=cvss),
                        cvs_sv3_base_score=self.get_cvss_base_score(cvss_list=cvss),
                        plugin_name="grype",
                        asset_identifier=self.identifier,
                        cve=finding.get("id"),
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
            raise GrypeProcessingError(f"Error fetching findings: {error_message}")

    @staticmethod
    def get_cvss_base_score(cvss_list: List) -> float:
        """
        Get the CVSS base score from the vulnerability data.
        :param cvss_list:
        :return: The CVSS base score
        :rtype: float
        """
        v3_base_score = 0.0
        for cvss in cvss_list:
            if cvss.get("type") == "Primary":
                if cvs := cvss.get("metrics"):
                    v3_base_score = cvs.get("baseScore")
                    break
        return v3_base_score

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
    def get_cvss_score(cvss_list: List) -> float:
        """
        Get the CVSS score from the finding data.
        :param finding:
        :return:
        """
        value = 0.0
        for cvss in cvss_list:
            if cvss.get("type") == "Primary":
                if cvs := cvss.get("metrics"):
                    if impact_score := cvs.get("impactScore"):
                        value = impact_score
                return value

    def fetch_assets(self, **kwargs) -> List[IntegrationAsset]:
        """
        Fetch assets from Grype scan data.
        :param List[Dict] data: integration data
        :return: List of IntegrationAsset
        :rtype: List[IntegrationAsset]
        """
        self.scan_date = kwargs.get("scan_date")
        self.identifier = kwargs.get("identifier")
        self.name = kwargs.get("name")
        self.os = kwargs.get("os")
        assets: List[IntegrationAsset] = []
        try:
            assets.append(
                IntegrationAsset(
                    identifier=self.identifier,
                    name=self.name,
                    ip_address="0.0.0.0",
                    cpu=0,
                    ram=0,
                    status=AssetStatus.Active.value,
                    asset_owner_id=self.owner_id,
                    asset_type="Other",
                    asset_category="Software",
                    operating_system=self.os,
                    parent_id=self.plan_id,
                    parent_module="securityplans",
                    notes="Grype",
                )
            )
            return assets
        except Exception:
            error_message = traceback.format_exc()
            logger.error(f"Error fetching assets: {error_message}")
            raise GrypeProcessingError(f"Error fetching assets: {error_message}")


@click.group()
def grype():
    """Performs actions from the Grype scanner integration."""
    pass


@grype.command("import_scans")
@click.option("--file_path", "-f", type=click.Path(exists=True, dir_okay=True), required=False)
@click.option("--ssp_id", "-s", type=int, required=True)
@click.option("--destination", "-d", type=click.Path(exists=True, dir_okay=True), required=False)
@click.option("--file_pattern", "-p", type=str, required=False, default="grype*.json")
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
    destination: Path,
    file_pattern: str,
    s3_bucket: str,
    s3_prefix: str,
    aws_profile: str,
) -> None:
    """
    Process Grype scan results from a folder container trivy scan files and load into RegScale.

    :param file_pattern: File pattern to search for in the directory
    :param file_path: Path to the Grype scan results JSON files
    :param ssp_id: RegScale SSP ID to which to import the scan results
    :param destination: Destination folder for processed files
    :param s3_bucket: S3 bucket to download scan files from
    :param s3_prefix: Prefix (folder path) within the S3 bucket
    :param aws_profile: AWS profile to use for S3 access
    """
    try:
        files = []
        if s3_bucket and s3_prefix and aws_profile:
            download_from_s3(bucket=s3_bucket, prefix=s3_prefix, local_path=destination, aws_profile=aws_profile)
            files = find_files(path=destination, pattern=file_pattern)
            logger.info("Downloaded all Grype scan files from S3. Processing...")
        elif destination and not s3_bucket:
            logger.info("Moving Grype scan files to %s", destination)
            stored_file_collection = find_files(path=file_path, pattern=file_pattern)
            move_all_files(stored_file_collection, destination)
            files = find_files(path=destination, pattern=file_pattern)
            logger.info("Done moving files")
        else:
            stored_file_collection = find_files(path=file_path, pattern=file_pattern)
            files = stored_file_collection
        if not files:
            logger.error("No Grype scan results found in the specified directory")
            return

        for file in files:
            raw_data = json.loads(read_file(file))
            data = raw_data.get("matches", [])
            scan_date = raw_data.get("timestamp") if raw_data.get("timestamp") else datetime.now().isoformat()
            identifier = raw_data.get("source", {}).get("target", {}).get("imageID", "Unknown")
            integration = GrypeIntegration(plan_id=ssp_id, scan_date=scan_date, data=data, identifier=identifier)
            integration.os = raw_data.get("source", {}).get("target", {}).get("os", "Linux")
            integration.name = raw_data.get("source", {}).get("target", {}).get("userInput", "Unknown")
            integration.sync_assets(
                plan_id=ssp_id,
                data=data,
                scan_date=scan_date,
                identifier=identifier,
                os=integration.os,
                name=integration.name,
            )
            integration.sync_findings(
                plan_id=ssp_id,
                data=data,
                scan_date=scan_date,
                identifier=identifier,
                os=integration.os,
                name=integration.name,
            )

        move_grype_files(file_path=destination, file_pattern=file_pattern)
        logger.info("Completed Grype processing.")
    except Exception as e:
        logger.error(f"Error processing Grype results: {str(e)}")
        logger.error(traceback.format_exc())
        raise GrypeProcessingError(f"Failed to process Grype results: {str(e)}")


def move_all_files(file_collection: List[Union[Path, str]], destination: Union[Path, str]) -> None:
    """
    Move all Grype files in the current directory to a folder called 'processed'.

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


def move_grype_files(file_path: Union[Path, str], file_pattern: str) -> None:
    """
    Move the a files to a folder called 'processed' in the same directory.

    :param Union[Path, str] file: A file paths or S3 URIs
    :param str file_pattern: The file pattern to search for
    """
    file_collection = find_files(path=file_path, pattern=file_pattern)
    for file in iterate_files(file_collection):
        new_file = get_processed_file_path(file)
        move_file(file, new_file)
        logger.info("Moved Grype file %s to %s", file, new_file)
