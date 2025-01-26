'''Functions to find vast.ai offers. Does not start them yet.'''
from .patched_vastai import VastAI
from .patched_vastai.vast import REGIONS
import logging
from typing import List
import asyncio
from .persist import save_pickle, load_pickle
import os
import requests
from .instance_state import InstanceState
from pydantic import BaseModel
from .requirements import Requirements
from typing import Optional

logger = logging.getLogger(__name__)

vast_sdk = VastAI(
    api_key=os.environ.get("VASTAI_API_KEY"))


class InstanceCreationResult:
    '''Stores the result of a create_instance call.'''

    def __init__(self, success: bool, new_contract: str = None, error: str = None):
        self.success = success
        self.instance_id = new_contract
        self.error = error


def create_instance(regions: List[str] = ['Europe', 'North_America'], **kwargs) -> InstanceCreationResult:
    """
    Launch a new VastAI instance with specified parameters.

    Args:
    - regions: list of regions to search for offers in. Will search in order of the list. One of
        REGIONS = {
            "North_America": "[US, CA]",
            "South_America": "[BR, AR, CL]",
            "Europe": "[SE, UA, GB, PL, PT, SI, DE, IT, CH, LT, GR, FI, IS, AT, FR, RO, MD, HU, NO, MK, BG, ES, HR, NL, CZ, EE]",
            "Asia": "[CN, JP, KR, ID, IN, HK, MY, IL, TH, QA, TR, RU, VN, TW, OM, SG, AE, KZ]",
            "Oceania": "[AU, NZ]",
            "Africa": "[EG, ZA]",
        }
    - kwargs: Additional parameters to pass to the VastAI launch_instance method.
    """
    result = {'success': False, 'error': 'not started'}
    for region in regions:
        logger.info(f"Trying to launch instance in {region}")

        # Remove 'regions' from kwargs if it exists
        filtered_kwargs = {k: v for k, v in kwargs.items() if k != 'regions'}
        # Also replace spaces with underscores
        filtered_kwargs = {k.replace(' ', '_'): v for k, v in filtered_kwargs.items()}

        try:
            result = vast_sdk.launch_instance(
                **filtered_kwargs
            )
            logger.debug(f'Result of calling patched SDK: {result}')
            parsed = result.strip().removeprefix('Started. ').split('\n')[0]
            logger.debug(f"Parsed: {parsed}")
            try:
                result = eval(parsed)
            except Exception as e:
                logger.info(f"Error while parsing response: {e}. Input: {parsed}")
                result = {'success': False, 'error': str(e) + result}
            if result['success']:
                # blacklist = load_pickle('blacklist', default=set())
                # state = get_instance_state(result['new_contract'])
                # # If this is blacklisted, recursively try the next region
                # if state.machine_id in blacklist:
                #     logger.warning(f"Instance {state.machine_id} is blacklisted. Destroying and retrying.")
                #     vast_sdk.destroy_instance(id=result['new_contract'])
                #     # This is a hack to search in the next possible region
                #     return create_instance(regions[1:], **kwargs)
                break
        except Exception as e:
            logger.error(f"Error while launching instance in {region}: {e}")
            result = {'success': False, 'error': str(e)}

    # Create an instance creation result
    return InstanceCreationResult(**result)


def get_instance_state(instance_id: str) -> InstanceState:
    """
    Retrieve the state of a VastAI instance and parse it into a Pydantic model.
    """
    api_key = os.environ.get("VASTAI_API_KEY")
    if not api_key:
        logger.error("VASTAI_API_KEY environment variable is not set.")
        return None
    
    url = f"https://console.vast.ai/api/v0/instances/{instance_id}/?api_key={api_key}"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for HTTP errors
        data = response.json()

        instance = data.get("instances", None)
        if not instance:
            logger.info(f"Instance {instance_id} not found in VastAI.")
            return None
        
        return InstanceState(**instance)  # Parse JSON into Pydantic model
    except requests.RequestException as e:
        logger.error(f"Error while fetching instance state for {instance_id}: {e}")
        return None


def get_all_active_instance_ids():
    """
    Function that returns all running instance IDs from the VastAI API.
    """
    api_key = os.environ.get("VASTAI_API_KEY")
    if not api_key:
        logger.error("VASTAI_API_KEY environment variable is not set.")
        return []

    url = f"https://console.vast.ai/api/v0/instances/?api_key={api_key}"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for HTTP errors
        data = response.json()

        # Extract instance IDs from the "instances" key
        instances = data.get("instances", [])
        instances = [InstanceState(**instance) for instance in instances]
        instance_ids = [instance.id for instance in instances]
        logger.info(f"Retrieved {len(instance_ids)} instance(s) from VastAI.")
        return instance_ids
    except requests.RequestException as e:
        logger.error(f"Error while fetching instance IDs from VastAI API: {e}")
        return []
    

def get_all_active_instances() -> List[InstanceState]:
    """
    Function that returns all running instance IDs from the VastAI API.
    """
    api_key = os.environ.get("VASTAI_API_KEY")
    if not api_key:
        logger.error("VASTAI_API_KEY environment variable is not set.")
        return []

    url = f"https://console.vast.ai/api/v0/instances/?api_key={api_key}"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for HTTP errors
        data = response.json()

        # Extract instance IDs from the "instances" key
        instances = data.get("instances", [])
        logger.info(f"Retrieved {len(instances)} instance(s) from VastAI.")
        # Parse JSON into Pydantic model
        instances = [InstanceState(**instance) for instance in instances]
        return instances
    except requests.RequestException as e:
        logger.error(f"Error while fetching instance IDs from VastAI API: {e}")
        return []



def flatten_model(instance_state: InstanceState) -> dict:
    """
    Recursively converts a Pydantic model (and any nested models) into a dictionary.
    """
    if isinstance(instance_state, BaseModel):
        return {
            key: flatten_model(value) for key, value in instance_state.model_dump().items()
        }
    elif isinstance(instance_state, list):
        return [flatten_model(item) for item in instance_state]
    elif isinstance(instance_state, dict):
        return {key: flatten_model(value) for key, value in instance_state.items()}
    else:
        return instance_state  # Base case: return the value as-is


def get_active_instance_with_requirements(requirements: Requirements) -> Optional[int]:
    """
    Finds the first instance that meets the requirements.
    """
    instances = get_all_active_instances()
    for instance in instances:
        logging.info(f"Found existing instance with state: {instance}")
        if requirements.matches(instance):
            logging.info(f"Existing instance matches requirements {instance.id} ({instance.ssh_host}:{instance.ssh_port})")
            return instance.id
    return None



def get_active_or_launch_instance(requirements: Requirements, regions: List[str] = ['Europe', 'North_America']):
    '''function that returns the first instance that meets the requirements, or launches a new one.'''
    instance_id =  get_active_instance_with_requirements(requirements)
    if instance_id:
        return instance_id
    else:
        instance_creation = create_instance(
            **requirements.model_dump(),
        )
        return instance_creation.instance_id

