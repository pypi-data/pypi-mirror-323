#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=C0415
"""standard python imports"""
import json
import re
from collections import Counter
from concurrent.futures import as_completed
from concurrent.futures.thread import ThreadPoolExecutor
from typing import Dict, List, Literal, Optional, Tuple
from urllib.parse import urljoin

import click

from regscale.core.app.api import Api
from regscale.core.app.utils.app_utils import create_progress_object, error_and_exit, get_current_datetime
from regscale.integrations.public.fedramp.parts_mapper import PartMapper
from regscale.integrations.public.fedramp.ssp_logger import SSPLogger
from regscale.models import ControlObjective, ImplementationObjective
from regscale.models.regscale_models import (
    ControlImplementation,
    File,
    LeveragedAuthorization,
    SecurityControl,
    SecurityPlan,
)
from regscale.models.regscale_models.control_implementation import ControlImplementationStatus

logger = SSPLogger()
part_mapper = PartMapper()
progress = create_progress_object()

SERVICE_PROVIDER_CORPORATE = "Service Provider Corporate"
CONTROL_ID = "Control ID"
ALT_IMPLEMENTATION = "Alternate Implementation"
SVC_PROV_SYS_SPEC = "Service Provider System Specific"
CAN_BE_INHERITED_CSP = "Can Be Inherited from CSP"
IMPACT_LEVEL = "Impact Level"
SYSTEM_NAME = "System Name"
CSP = "CSP"

STATUS_MAPPING = {
    "Implemented": ControlImplementationStatus.FullyImplemented,
    "Partially Implemented": ControlImplementationStatus.PartiallyImplemented,
    "Planned": ControlImplementationStatus.Planned,
    "N/A": ControlImplementationStatus.NA,
    "Alternative Implementation": ControlImplementationStatus.Alternative,
    "Alternate Implementation": ControlImplementationStatus.Alternative,
}
RESPONSIBILITY_MAP = {
    "Service Provider Corporate": "Provider",
    "Service Provider System Specific": "Provider (System Specific)",
    "Service Provider Hybrid": "Hybrid",
    "Provided by Customer": "Customer",
    "Configured by Customer": "Customer Configured",
    "Shared": "Shared",
    "Inherited": "Inherited",
}


def transform_control(control: str) -> str:
    """
    Function to parse the control string and transform it to the RegScale format
    ex: AC-1 (a) -> ac-1.a or AC-6 (10) -> ac-6.10

    :param str control: Control ID as a string
    :return: Transformed control ID to match RegScale control ID format
    :rtype: str
    """
    # Use regex to match the pattern and capture the parts
    match = re.match(r"([A-Za-z]+)-(\d+)\s\((\d+|[a-z])\)", control)
    if match:
        control_name = match.group(1).lower()
        control_number = match.group(2)
        sub_control = match.group(3)

        if sub_control.isdigit():
            transformed_control = f"{control_name}-{control_number}.{sub_control}"
        else:
            transformed_control = f"{control_name}-{control_number}"

        return transformed_control
    return control.lower()


def new_leveraged_auth(
    ssp: SecurityPlan, user_id: str, instructions_data: dict, version: Literal["rev4", "rev5"]
) -> int:
    """
    Function to create a new Leveraged Authorization in RegScale.

    :param SecurityPlan ssp: RegScale SSP Object
    :param str user_id: RegScale user ID
    :param dict instructions_data: Data parsed from Instructions worksheet in the FedRAMP CIS CRM workbook
    :param str version: FedRAMP revision version
    :return: Newly created Leveraged Authorization ID in RegScale
    :rtype: int
    """
    leveraged_auth = LeveragedAuthorization(
        title=instructions_data[CSP],
        servicesUsed=instructions_data[CSP],
        fedrampId=(instructions_data["System Identifier"] if version == "rev5" else instructions_data[SYSTEM_NAME]),
        authorizationType="FedRAMP Ready",
        impactLevel=instructions_data[IMPACT_LEVEL],
        dateAuthorized="",
        natureOfAgreement="Other",
        dataTypes="Other",
        authorizedUserTypes="Other",
        authenticationType="Other",
        createdById=user_id,
        securityPlanId=ssp.id,
        ownerId=user_id,
        lastUpdatedById=user_id,
        description="Imported from FedRAMP CIS CRM Workbook on " + get_current_datetime("%m/%d/%Y %H:%M:%S"),
    )
    new_leveraged_auth_id = leveraged_auth.create()
    return new_leveraged_auth_id.id


def gen_key(control_id: str):
    """
    Function to generate a key for the control ID

    :param str control_id: The control ID to generate a key for
    :return: The generated key
    :rtype: str
    """
    # Match pattern: captures everything up to either:
    # 1. The last (number) if it exists
    # 2. The main control number if no enhancement exists
    # And excludes any trailing (letter)
    pattern = r"^((?:\w+-\d+(?:\(\d+\))?))(?:\([a-zA-Z]\))?$"

    match = re.match(pattern, control_id)
    if match:
        return match.group(1)
    return control_id


def map_implementation_status(control_id: str, cis_data: dict) -> str:
    """
    Function to map the selected implementation status on the CIS worksheet to a RegScale status

    :param str control_id: The control ID from RegScale
    :param dict cis_data: Data from the CIS worksheet to map the status from
    :return: RegScale control implementation status
    :rtype: str
    """

    # Extract matching records
    cis_records = [
        value
        for value in cis_data.values()
        if gen_key(value.get("regscale_control_id", "")).lower() == control_id.lower()
    ]

    status_ret = ControlImplementationStatus.NotImplemented

    logger.debug("Found %d CIS records for control %s", len(cis_records), control_id)

    if not cis_records:
        logger.warning(f"No CIS records found for control {control_id}")
        return status_ret

    # Count implementation statuses
    status_counts = Counter(record.get("implementation_status", "") for record in cis_records)
    logger.debug("Status distribution for %s: %s", control_id, dict(status_counts))

    # Early returns for simple cases
    if len(status_counts) == 1:
        status = next(iter(status_counts))
        return STATUS_MAPPING.get(status, ControlImplementationStatus.NotImplemented)

    # Priority-based status determination
    if any(status in ["N/A", "Alternative Implementation"] for status in status_counts):
        status_ret = ControlImplementationStatus.NA

    implemented_count = status_counts.get("Implemented", 0)
    total_count = sum(status_counts.values())

    if implemented_count == total_count:
        status_ret = ControlImplementationStatus.FullyImplemented
    elif implemented_count > 0 or any(status == "Partially Implemented" for status in status_counts):
        status_ret = ControlImplementationStatus.PartiallyImplemented
    elif any(status == "Planned" for status in status_counts):
        status_ret = ControlImplementationStatus.Planned

    return status_ret


def map_origination(control_id: str, cis_data: dict) -> dict:
    """
    Function to map the responsibility for a control implementation from the CRM worksheet

    :param str control_id: RegScale control ID
    :param dict cis_data: Data from the CRM worksheet
    :return: The responsibility information in regscale format
    :rtype: dict
    """
    origination_bools = {
        "bInherited": False,
        "bServiceProviderCorporate": False,
        "bServiceProviderSystemSpecific": False,
        "bServiceProviderHybrid": False,
        "bConfiguredByCustomer": False,
        "bProvidedByCustomer": False,
        "bShared": False,
        "record_text": "",
    }
    cis_records = [
        value for _, value in cis_data.items() if gen_key(value["regscale_control_id"]).lower() == control_id.lower()
    ]
    for record in cis_records:
        # Create the implementation objective, and save.
        control_origination = record.get("control_origination", "")
        if SERVICE_PROVIDER_CORPORATE in control_origination:
            # responsibility = "Provider"
            origination_bools["bServiceProviderCorporate"] = True
        if "Service Provider System Specific" in control_origination:
            # responsibility = "Provider (System Specific)"
            origination_bools["bServiceProviderSystemSpecific"] = True
        if "Service Provider Hybrid" in control_origination:
            # responsibility = "Hybrid"
            origination_bools["bServiceProviderHybrid"] = True
        if "Provided by Customer" in control_origination:
            # responsibility = "Customer"
            origination_bools["bProvidedByCustomer"] = True
        if "Configured by Customer" in control_origination:
            # responsibility = "Customer Configured"
            origination_bools["bConfiguredByCustomer"] = True
        if "Shared" in control_origination:
            # responsibility = "Shared"
            origination_bools["bShared"] = True
        if "Inherited" in control_origination:
            # responsibility = "Inherited"
            origination_bools["bInherited"] = True
        origination_bools["record_text"] += control_origination
    return origination_bools


def update_imp_objective(
    leverage_auth_id: int,
    existing_imp_obj: List[ImplementationObjective],
    imp: ControlImplementation,
    objective: ControlObjective,
    record: dict,
) -> Optional[ImplementationObjective]:
    """
    Update the control objective with the given record data.

    :param int leverage_auth_id: The leveraged authorization ID
    :param List[ImplementationObjective] existing_imp_obj: The existing implementation objective
    :param ControlImplementation imp: The control implementation to update
    :param ControlObjective objective: The control objective to update
    :param dict record: The CIS/CRM record data to update the objective with
    :rtype: Optional[ImplementationObjective]
    :return: The updated or created implementation objective
    """
    status_map = {
        "Implemented": "Fully Implemented",
        "Planned": "Planned",
        "Partially Implemented": "Partially Implemented",
        "N/A": "Not Applicable",
        "Not Implemented": "Not Implemented",
    }

    cis_record = record.get("cis", {})
    crm_record = record.get("crm", {})
    responsibility = RESPONSIBILITY_MAP.get(cis_record.get("control_origination", ""), "Not Applicable")
    customer_responsibility = crm_record.get("specific_inheritance_and_customer_agency_csp_responsibilities")
    # if crm_record.get("can_be_inherited_from_csp") == "Partial":
    #     responsibility = "Shared"
    # else:
    #     responsibility = "Provider"

    if (objective.id, imp.id) not in [(imp_obj.objectiveId, imp_obj.implementationId) for imp_obj in existing_imp_obj]:
        imp_obj = ImplementationObjective(
            id=0,
            uuid="",
            inherited=crm_record.get("can_be_inherited_from_csp") == "Yes",
            implementationId=imp.id,
            status=status_map.get(cis_record.get("implementation_status", "Not Implemented"), "Not Implemented"),
            objectiveId=objective.id,
            # optionId=option_id,  #
            notes=objective.name,
            securityControlId=objective.securityControlId,
            responsibility=responsibility,
            cloudResponsibility=customer_responsibility,
            customerResponsibility=customer_responsibility,
            authorizationId=leverage_auth_id,
        )
        return imp_obj.create()

    else:
        ex_obj = next((obj for obj in existing_imp_obj if obj.objectiveId == objective.id), None)
        if ex_obj:
            ex_obj.status = status_map.get(
                cis_record.get("implementation_status", "Not Implemented"), "Not Implemented"
            )
            ex_obj.responsibility = responsibility
            ex_obj.cloudResponsibility = customer_responsibility
            ex_obj.customerResponsibility = customer_responsibility
            return ex_obj.save()


def parse_control_details(control_imp: ControlImplementation, control_id: str, cis_data: dict) -> ControlImplementation:
    """
    Function to parse control details from RegScale and CIS data and returns an updated ControlImplementation object

    :param ControlImplementation control_imp: RegScale ControlImplementation object to update
    :param str control_id: RegScale control ID
    :param dict cis_data: Data from the CIS worksheet
    :return: Updated ControlImplementation object
    :rtype: ControlImplementation
    """
    status = map_implementation_status(control_id=control_id, cis_data=cis_data)
    origination_bool = map_origination(control_id=control_id, cis_data=cis_data)
    control_imp.status = status
    if status == ControlImplementationStatus.Planned:
        control_imp.plannedImplementationDate = get_current_datetime("%Y-%m-%d")
        control_imp.stepsToImplement = "To be updated"
    control_imp.controlSource = "Baseline" if not origination_bool["bInherited"] else "Inherited"
    control_imp.exclusionJustification = (
        "Imported from FedRAMP CIS CRM Workbook" if status == ControlImplementationStatus.NA else None
    )
    control_imp.bStatusImplemented = status == ControlImplementationStatus.FullyImplemented
    control_imp.bStatusPartiallyImplemented = status == ControlImplementationStatus.PartiallyImplemented
    control_imp.bStatusPlanned = status == "Planned"
    control_imp.bStatusNotApplicable = status == ControlImplementationStatus.NA
    control_imp.bInherited = origination_bool["bInherited"]
    control_imp.inheritable = origination_bool["bInherited"]
    control_imp.bServiceProviderCorporate = origination_bool["bServiceProviderCorporate"]
    control_imp.bServiceProviderSystemSpecific = origination_bool["bServiceProviderSystemSpecific"]
    control_imp.bServiceProviderHybrid = origination_bool["bServiceProviderHybrid"]
    control_imp.bConfiguredByCustomer = origination_bool["bConfiguredByCustomer"]
    control_imp.bProvidedByCustomer = origination_bool["bProvidedByCustomer"]
    control_imp.responsibility = RESPONSIBILITY_MAP.get(origination_bool.get("record_text", ""), "Not Applicable")

    if updated_control := control_imp.save():
        logger.debug("Control Implementation #%s updated successfully", control_imp.id)
        return updated_control
    logger.error("Failed to update Control Implementation \n" + json.dumps(control_imp.model_dump()))
    return control_imp


def get_responsibility(origination_bool: dict) -> str:
    """
    Function to map the responsibility based on origination booleans.

    :param dict origination_bool: Dictionary containing origination booleans
    :return: Responsibility string
    :rtype: str
    """
    responsibility = "Unknown"

    if sum(origination_bool.values()) > 1 or origination_bool["bShared"]:
        return "Shared"

    elif origination_bool["bServiceProviderCorporate"]:
        responsibility = "Provider"
    elif origination_bool["bServiceProviderSystemSpecific"]:
        responsibility = "Provider (System Specific)"
    elif origination_bool["bServiceProviderHybrid"]:
        responsibility = "Hybrid"
    elif origination_bool["bProvidedByCustomer"]:
        responsibility = "Customer"
    elif origination_bool["bConfiguredByCustomer"]:
        responsibility = "Customer Configured"
    elif origination_bool["bInherited"]:
        responsibility = "Inherited"

    return responsibility


def fetch_and_update_imps(control: dict, api: Api, cis_data: dict) -> Optional[ControlImplementation]:
    """
    Function to fetch implementation objectives from RegScale via API

    :param dict control: RegScale control as a dictionary
    :param Api api: RegScale API object
    :param dict cis_data: Data from the CIS worksheet
    :return: An updated control implementation if found
    :rtype: Optional[ControlImplementation]
    """
    # get the control and control implementation objects
    regscale_control = SecurityControl.get_object(control["scId"])
    regscale_control_imp = ControlImplementation.get_object(control["id"])

    if not regscale_control or not regscale_control_imp:
        api.logger.error("Failed to fetch control or control implementation")
        return regscale_control_imp

    updated_control = parse_control_details(
        control_imp=regscale_control_imp, control_id=regscale_control.controlId, cis_data=cis_data
    )
    return updated_control


def get_all_imps(api: Api, ssp_id: int, cis_data: dict) -> list:
    """
    Function to retrieve control implementations and their objectives from RegScale

    :param Api api: The RegScale API object
    :param int ssp_id: The SSP ID
    :param dict cis_data: The data from the CIS worksheet
    :return: List of updated control implementations
    :rtype: list
    """
    from requests import RequestException

    updated_controls = []
    url = urljoin(api.config["domain"], f"/api/controlImplementation/getSCListByPlan/{ssp_id}")
    response = api.get(url)

    # Check if the response is successful
    if response.status_code == 200:
        ssp_controls = response.json()
        # Get Control Implementations For SSP
        fetching_imps = progress.add_task(
            f"[magenta]Fetching & updating {len(ssp_controls)} implementation(s)...", total=len(ssp_controls)
        )
        with ThreadPoolExecutor(max_workers=50) as executor:
            futures = [executor.submit(fetch_and_update_imps, control, api, cis_data) for control in ssp_controls]
            for future in as_completed(futures):
                progress.update(fetching_imps, advance=1)
                try:
                    controls = future.result()
                    updated_controls.append(controls)
                except (RequestException, TimeoutError) as ex:
                    api.logger.error(f"Error fetching control implementations: {ex}")
    else:
        api.logger.error(f"Failed to fetch controls: {response.status_code}: {response.reason}")

    return updated_controls


def update_all_objectives(
    leveraged_auth_id: int,
    cis_data: Dict[str, Dict[str, str]],
    crm_data: Dict[str, Dict[str, str]],
    control_implementations: List[ControlImplementation],
):
    """
    Updates all objectives for the given control implementations based on CIS worksheet data.
    Uses parallel processing and displays progress bars.

    :param int leveraged_auth_id: The leveraged authorization ID
    :param Dict[str, Dict[str, str]] cis_data: The CIS data to update from
    :param Dict[str, Dict[str, str]] crm_data: The CRM data to update from
    :param List[ControlImplementation] control_implementations: The control implementations to update
    """
    task = progress.add_task("[cyan]Processing control objectives...", total=len(control_implementations))
    # Create an easier to use combo crm/cis dataset
    combo = {}
    for key in cis_data:
        if key in [crm["control_id_original"] for crm in crm_data.values()]:
            crm_dat = next((crm for crm in crm_data.values() if crm["control_id_original"] == key))
            combo[key] = {"cis": cis_data[key], "crm": crm_dat}

    # Process implementations in parallel
    with ThreadPoolExecutor(max_workers=50) as executor:
        # Submit all tasks
        future_to_control = {
            executor.submit(process_implementation, leveraged_auth_id, imp, combo): imp
            for imp in control_implementations
        }

        # Process results as they complete
        for future in as_completed(future_to_control):
            result = future.result()
            if isinstance(result[0], list):
                error_lst = result[0]
                for inf in error_lst:
                    logger.error(inf)
            progress.update(task, advance=1)


def process_implementation(
    leveraged_auth_id: int, implementation: ControlImplementation, sheet_data: dict
) -> Tuple[List[str], List[ImplementationObjective]]:
    """
    Processes a single implementation and its associated records.

    :param int leverage_auth_id: The leveraged authorization ID
    :param ControlImplementation implementation: The control implementation to process
    :param dict sheet_data: The CIS/CRM data to process
    :rtype Tuple[List[str], List[ImplementationObjective]]
    :returns A list of updated implementation objectives
    """

    errors = []
    processed_objectives = []

    control_objectives, existing_objectives, filtered_records = gen_filtered_records(implementation, sheet_data)
    result = None
    for record in filtered_records:
        res = process_single_record(
            leveraged_auth_id=leveraged_auth_id,
            implementation=implementation,
            record=record,
            control_objectives=control_objectives,
            existing_objectives=existing_objectives,
        )
        if isinstance(res, tuple):
            method_errors, result = res
            errors.extend(method_errors)
        if result:
            processed_objectives.append(result)
    return errors, processed_objectives


def gen_filtered_records(implementation, sheet_data):
    """
    Generates filtered records for a given implementation.

    :param ControlImplementation implementation: The control implementation to filter records for
    :param dict sheet_data: The CIS/CRM data to filter
    :rtype Tuple[List[ControlObjective], List[ImplementationObjective], List[Dict[str, str]]]
    :returns A tuple of control objectives, existing objectives, and filtered records
    :rtype Tuple[List[ControlObjective], List[ImplementationObjective], List[Dict[str, str]]]
    """
    security_control = SecurityControl.get_object(implementation.controlID)
    control_objectives = ControlObjective.get_by_control(implementation.controlID)
    existing_objectives = ImplementationObjective.get_by_control(implementation.id)
    filtered_records = filter(
        lambda r: extract_control_name(r["cis"]["regscale_control_id"]).lower() == security_control.controlId.lower(),
        sheet_data.values(),
    )
    return control_objectives, existing_objectives, filtered_records


def get_matching_cis_records(control_id: str, cis_data: dict) -> List[Dict[str, str]]:
    """
    Finds matching CIS records for a given control ID.

    :param str control_id: The control ID to match
    :param dict cis_data: The CIS data to search
    :rtype List[Dict[str, str]]
    :returns A list of matching CIS records
    """
    return [value for value in cis_data.values() if value["regscale_control_id"].lower() == control_id.lower()]


def process_single_record(**kwargs) -> Tuple[List[str], Optional[ImplementationObjective]]:
    """
    Processes a single CIS record and returns updated objective if successful.

    :param dict kwargs: Keyword arguments containing the required parameters
    :rtype Tuple[List[str], Optional[ImplementationObjective]]
    :returns A list of errors and the Implementation Objective if successful, otherwise None
    """
    errors = []
    leveraged_auth_id: int = kwargs.get("leveraged_auth_id")
    implementation: ControlImplementation = kwargs.get("implementation")
    record: dict = kwargs.get("record")
    control_objectives: List[ControlObjective] = kwargs.get("control_objectives")
    existing_objectives: List[ImplementationObjective] = kwargs.get("existing_objectives")
    source = ""
    try:
        key = record["cis"]["control_id"]
        source = part_mapper.find_by_source(key)
        if not source:
            errors.append(f"Unable to find source for control {key}")
            return errors, None

        objective = next(obj for obj in control_objectives if obj.otherId == source)

        result = update_imp_objective(
            leverage_auth_id=leveraged_auth_id,
            existing_imp_obj=existing_objectives,
            imp=implementation,
            objective=objective,
            record=record,
        )

        return errors, result
    except StopIteration:
        errors.append(f"Unable to find control objective for control {source}")
        return errors, None
    except (KeyError, AttributeError) as e:
        error_type = e.__class__.__name__
        errors.append(
            f"{error_type} : Error processing record for control {implementation.controlID} and "
            f"part {source}: {str(e)}"
        )
        return errors, None


def parse_crm_worksheet(file_path: click.Path, crm_sheet_name: str, version: Literal["rev4", "rev5"]) -> dict:
    """
    Function to format CRM content.

    :param click.Path file_path: The file path to the FedRAMP CIS CRM workbook
    :param str crm_sheet_name: The name of the CRM sheet to parse
    :return: Formatted CRM content
    :rtype: dict
    """
    import pandas as pd  # Optimize import performance

    if version == "rev5":
        skip_rows = 2
    else:
        skip_rows = 3

    formatted_crm = {}
    data = pd.read_excel(
        str(file_path),
        sheet_name=crm_sheet_name,
        skiprows=skip_rows,
        usecols=[
            CONTROL_ID,
            "Can Be Inherited from CSP",
            "Specific Inheritance and Customer Agency/CSP Responsibilities",
        ],
    )

    # Filter rows where "Can Be Inherited from CSP" is not equal to "No"
    exclude_no = data[data[CAN_BE_INHERITED_CSP] != "No"]

    # Iterate through each row and add to the dictionary
    for _, row in exclude_no.iterrows():
        control_id = row[CONTROL_ID]

        # Convert camel case to snake case, remove special characters, and convert to lowercase
        clean_control_id = re.sub(r"\W+", "", control_id)
        clean_control_id = re.sub("([a-z0-9])([A-Z])", r"\1_\2", clean_control_id).lower()

        # Use clean_control_id as the key to avoid overwriting
        formatted_crm[clean_control_id] = {
            "control_id": clean_control_id,
            "control_id_original": control_id,
            "regscale_control_id": transform_control(control_id),
            "can_be_inherited_from_csp": row[CAN_BE_INHERITED_CSP],
            "specific_inheritance_and_customer_agency_csp_responsibilities": row[
                "Specific Inheritance and Customer Agency/CSP Responsibilities"
            ],
        }

    return formatted_crm


def parse_cis_worksheet(file_path: click.Path, cis_sheet_name: str) -> dict:
    """
    Function to parse and format the CIS worksheet content

    :param click.Path file_path: The file path to the FedRAMP CIS CRM workbook
    :param str cis_sheet_name: The name of the CIS sheet to parse
    :return: Formatted CIS content
    :rtype: dict
    """
    import pandas as pd  # Optimize import performance

    # Parse the worksheet named 'CIS GovCloud U.S.+DoD (H)', skipping the initial rows
    cis_df = pd.read_excel(file_path, sheet_name=cis_sheet_name, skiprows=2)

    # Set the appropriate headers
    cis_df.columns = cis_df.iloc[0]

    # Drop any fully empty rows
    cis_df.dropna(how="all", inplace=True)

    # Reset the index
    cis_df.reset_index(drop=True, inplace=True)

    # Rename columns to standardize names
    cis_df.columns = [
        CONTROL_ID,
        "Implemented",
        ControlImplementationStatus.PartiallyImplemented,
        "Planned",
        ALT_IMPLEMENTATION,
        ControlImplementationStatus.NA,
        SERVICE_PROVIDER_CORPORATE,
        SVC_PROV_SYS_SPEC,
        "Service Provider Hybrid",
        "Configured by Customer",
        "Provided by Customer",
        "Shared Responsibility",
        "Inherited Authorization",
    ]

    # Fill NaN values with an empty string for processing
    cis_df = cis_df.fillna("")

    # Function to extract the first non-empty implementation status
    def _extract_status(data_row: pd.Series) -> str:
        """
        Function to extract the first non-empty implementation status from the CIS worksheet

        :param pd.Series data_row: The data row to extract the status from
        :return: The implementation status
        :rtype: str
        """
        for col in [
            "Implemented",
            ControlImplementationStatus.PartiallyImplemented,
            "Planned",
            ALT_IMPLEMENTATION,
            ControlImplementationStatus.NA,
        ]:
            if data_row[col]:
                return col
        return ""

    # Function to extract the first non-empty control origination
    def _extract_origination(data_row: pd.Series) -> str:
        """
        Function to extract the first non-empty control origination from the CIS worksheet

        :param pd.Series data_row: The data row to extract the origination from
        :return: The control origination
        :rtype: str
        """
        selected_origination = []
        for col in [
            SERVICE_PROVIDER_CORPORATE,
            SVC_PROV_SYS_SPEC,
            "Service Provider Hybrid",
            "Configured by Customer",
            "Provided by Customer",
            "Shared Responsibility",
            "Inherited Authorization",
        ]:
            if data_row[col]:
                selected_origination.append(col)
        return ", ".join(selected_origination) if selected_origination else ""

    def _process_row(row: pd.Series) -> dict:
        """
        Function to process a row from the CIS worksheet

        :param pd.Series row: The row to process
        :return: The processed row
        :rtype: dict
        """
        return {
            "control_id": row[CONTROL_ID],
            "regscale_control_id": transform_control(row[CONTROL_ID]),
            "implementation_status": _extract_status(row),
            "control_origination": _extract_origination(row),
        }

    # use a threadexecutor to process the rows in parallel
    with ThreadPoolExecutor() as executor:
        results = list(executor.map(_process_row, [row for _, row in cis_df.iterrows()]))

    # iterate the results and index by control_id
    return {result["control_id"]: result for result in results}


def parse_instructions_worksheet(
    file_path: click.Path, version: Literal["rev4", "rev5"], instructions_sheet_name: str = "Instructions"
) -> list[dict]:
    """
    Function to parse the instructions sheet from the FedRAMP Rev5 CIS/CRM workbook

    :param click.Path file_path: The file path to the FedRAMP CIS CRM workbook
    :param Literal["rev4", "rev5"] version: The version of the FedRAMP CIS CRM workbook
    :param str instructions_sheet_name: The name of the instructions sheet to parse, defaults to "Instructions"
    :return: List of formatted instructions content as a dictionary
    :rtype: list[dict]
    """
    import pandas as pd  # Optimize import performance

    instructions_df = pd.read_excel(str(file_path), sheet_name=instructions_sheet_name, skiprows=2)

    if version == "rev5":
        # Set the appropriate headers
        instructions_df.columns = instructions_df.iloc[0]
        instructions_df = instructions_df[1:]
        relevant_columns = [SYSTEM_NAME, CSP, "System Identifier", IMPACT_LEVEL]
    else:
        for index in range(len(instructions_df)):
            if CSP in instructions_df.iloc[index].values:
                instructions_df.columns = instructions_df.iloc[index]
                instructions_df = instructions_df[index + 1 :]
                break
        # delete the rows before the found row
        relevant_columns = [SYSTEM_NAME, CSP, IMPACT_LEVEL]
    try:
        instructions_df = instructions_df[relevant_columns]
    except KeyError:
        error_and_exit(
            f"Unable to find the relevant columns in the Instructions worksheet. Do you have the correct "
            f"revision set?\nRevision: {version}",
            show_exec=False,
        )
    # convert the dataframe to a dictionary
    return instructions_df.to_dict(orient="records")


def parse_and_map_data(leveraged_auth_id: int, api: Api, ssp_id: int, cis_data: dict, crm_data: dict) -> None:
    """
    Function to parse and map data from RegScale and the workbook.

    :param int leverage_auth_id: The leveraged authorization ID
    :param Api api: RegScale API object
    :param int ssp_id: RegScale SSP ID #
    :param dict cis_data: Parsed CIS data to update the control implementations and objectives
    :param dict crm_data: Parsed CRM data to update the control implementations and objectives
    :return: None
    :rtype: None
    """
    with progress:
        implementations = get_all_imps(api=api, ssp_id=ssp_id, cis_data=cis_data)
        update_all_objectives(
            leveraged_auth_id=leveraged_auth_id,
            cis_data=cis_data,
            crm_data=crm_data,
            control_implementations=implementations,
        )


def extract_control_name(control_string: str) -> str:
    """
    Extracts the control name (e.g., 'AC-20(1)') from a given string.

    :param str control_string: The string to extract the control name from
    :return: The extracted control name
    :rtype: str
    """
    pattern = r"^[A-Z]{2}-\d{1,3}(?:\(\d+\))?"
    match = re.match(pattern, control_string.upper())
    return match.group() if match else ""


def parse_and_import_ciscrm(
    file_path: click.Path,
    version: Literal["rev4", "rev5", "4", "5"],
    cis_sheet_name: str,
    crm_sheet_name: str,
    regscale_ssp_id: int,
    leveraged_auth_id: int = 0,
) -> None:
    """
    Parse and import the FedRAMP Rev5 CIS/CRM Workbook into a RegScale System Security Plan

    :param click.Path file_path: The file path to the FedRAMP CIS CRM .xlsx file
    :param Literal["rev4", "rev5"] version: FedRAMP revision version
    :param str cis_sheet_name: CIS sheet name in the FedRAMP CIS CRM .xlsx to parse
    :param str crm_sheet_name: CRM sheet name in the FedRAMP CIS CRM .xlsx to parse
    :param int regscale_ssp_id: The ID number from RegScale of the System Security Plan
    :param int leveraged_auth_id: RegScale Leveraged Authorization ID #, if none provided, one will be created
    :raises ValueError: If the SSP with the given ID is not found in RegScale
    :rtype: None
    """
    sys_name_key = "System Name"
    api = Api()
    ssp: SecurityPlan = SecurityPlan.get_object(regscale_ssp_id)
    if not ssp:
        raise ValueError(f"SSP with ID {regscale_ssp_id} not found in RegScale.")

    if "5" in version:
        version = "rev5"
    else:
        version = "rev4"

    part_mapper.load_fedramp_version_5_mapping()
    # parse the instructions worksheet to get the csp name, system name, and other data
    instructions_data = parse_instructions_worksheet(file_path=file_path, version=version)  # type: ignore

    # get the system names from the instructions data by dropping any non-string values
    system_names = [entry[sys_name_key] for entry in instructions_data if isinstance(entry[sys_name_key], str)]
    name_match: str = system_names[0]

    # update the instructions data to the matched system names
    instructions_data = [
        (
            entry
            if isinstance(entry[sys_name_key], str)
            and entry[sys_name_key] == name_match
            or entry[sys_name_key] == ssp.systemName
            else None
        )
        for entry in instructions_data
    ]
    # remove any None values from the instructions data
    instructions_data = [entry for entry in instructions_data if entry][0]
    if not any(instructions_data):
        raise ValueError("Unable to parse data from Instructions sheet.")

    # start parsing the workbook
    cis_data = parse_cis_worksheet(file_path=file_path, cis_sheet_name=cis_sheet_name)
    crm_data = parse_crm_worksheet(file_path=file_path, crm_sheet_name=crm_sheet_name, version=version)  # type: ignore
    if leveraged_auth_id == 0:
        auths = LeveragedAuthorization.get_all_by_parent(ssp.id)
        if auths:
            leveraged_auth_id = next((auth.id for auth in auths))
        else:
            leveraged_auth_id = new_leveraged_auth(
                ssp=ssp,
                user_id=api.config["userId"],
                instructions_data=instructions_data,
                version=version,  # type: ignore
            )
    # Update objectives using the mapped data using threads
    parse_and_map_data(
        leveraged_auth_id=leveraged_auth_id,
        api=api,
        ssp_id=regscale_ssp_id,
        cis_data=cis_data,
        crm_data=crm_data,
    )

    # upload workbook to the SSP
    File.upload_file_to_regscale(
        file_name=str(file_path),
        parent_id=regscale_ssp_id,
        parent_module="securityplans",
        api=api,
    )
