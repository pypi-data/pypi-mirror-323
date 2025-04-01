"""
This module contains the Click commands for the opentext integration.
"""

# pylint: disable=W0621
import logging
import sys

import click
from pathlib import Path

from regscale.integrations.commercial.opentext.scanner import WebInspectImport
from regscale.models.app_models.click import regscale_ssp_id


@click.group()
def fortify():
    """Performs actions on the OpenText Fortify"""


@fortify.group(name="web_inspect")
def web_inspect():
    """Performs actions on the OpenText Web Inspect files."""


@web_inspect.command(name="import_file")
@click.option(
    "--folder_path",
    prompt="Enter the folder path of the Fortify WebInspect XML files to process",
    help="RegScale will load the Fortify WebInspect XML Scans",
    type=click.Path(exists=True),
)
@regscale_ssp_id()
# Add Prompt for RegScale SSP name
def import_file(folder_path: click.Path, regscale_ssp_id: int):
    """
    Import and process a folder of Fortify WebInspect XML file(s).

    :param click.Path file_path: The Path to a folder of XML file(s) to import
    :param int regscale_ssp_id: RegScale SSP ID
    """
    logger = logging.getLogger("rich")

    # Assert files exist in path
    xml_files = list(Path(folder_path).glob("*.xml"))
    if not xml_files:
        logger.warning("No XML files found in the folder: %s", folder_path)
        sys.exit(0)

    # Add your XML processing logic here
    integration = WebInspectImport(plan_id=regscale_ssp_id)
    integration.sync_assets(
        plan_id=regscale_ssp_id,
        folder_path=folder_path,
    )
    integration.sync_findings(
        plan_id=regscale_ssp_id,
        folder_path=folder_path,
    )
