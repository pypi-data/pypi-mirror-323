'''Functions to find vast.ai offers. Does not start them yet.'''
from .patched_vastai import VastAI
from .patched_vastai.vast import REGIONS
import logging
from typing import List
import asyncio
from .persist import save_pickle, load_pickle
import os

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
                blacklist = load_pickle('blacklist.pkl', default=set())
                state = get_instance_state(result['new_contract'])
                # If this is blacklisted, recursively try the next region
                if state['ID'] in blacklist:
                    logger.warning(f"Instance {state['Machine']} is blacklisted. Destroying and retrying.")
                    vast_sdk.destroy_instance(id=result['new_contract'])
                    # This is a hack to search in the next possible region
                    return create_instance(regions[1:], **kwargs)
                break
        except Exception as e:
            logger.error(f"Error while launching instance in {region}: {e}")
            result = {'success': False, 'error': str(e)}

    # Create an instance creation result
    return InstanceCreationResult(**result)


def get_instance_state(instance_id: str) -> dict:
    """
    Retrieve the state of a VastAI instance.
    """
    instance_state = vast_sdk.show_instance(id=instance_id)
    keys = [k.strip() for k in instance_state.split('\n')
            [0].split('  ') if k.strip()]
    values = [v for v in instance_state.split('\n')[1].split(' ') if v]
    return dict(zip(keys, values))

def get_all_instance_ids():
    '''Function that returns all running instance ids.'''
    instances = vast_sdk.show_instances()
    return [line.split(' ')[0].strip() for line in instances.split('\n')[1:] if line]

def matches_requirements(instance_state, requirements):
    # Map requirements keys to instance_state keys
    key_mapping = {
        'gpu_name': 'Model',       # gpu_name maps to Model
        'price': '$/hr',           # price maps to $/hr
        'disk': 'Storage',         # disk maps to Storage
        'image': 'Image',          # image maps to Image
    }

    for req_key, req_value in requirements.items():
        # Get the corresponding key in instance_state
        inst_key = key_mapping.get(req_key)

        # Skip if no mapping exists (e.g., for env)
        if not inst_key:
            logger.info(f"No mapping defined for requirement key: {req_key}")
            continue

        # Retrieve the instance value
        inst_value = instance_state.get(inst_key)

        # Log and return False if the key is missing in instance_state
        if inst_value is None:
            logger.info(f"Requirement failed: {req_key} (Mapped key: {inst_key}) is missing in instance state.")
            return False

        # Perform comparison
        if isinstance(req_value, (int, float)):  # Numeric comparison
            try:
                inst_value = float(inst_value)  # Ensure it's numeric
            except ValueError:
                logger.info(f"Requirement failed: {req_key} (Expected numeric value, Found: {inst_value})")
                return False

            if inst_key == '$/hr':  # For price, ensure it is <= the requirement
                if inst_value > req_value:
                    logger.info(f"Requirement failed: {req_key} (Expected <= {req_value}, Found: {inst_value})")
                    return False
            else:  # For disk, ensure it is >= the requirement
                if inst_value < req_value:
                    logger.info(f"Requirement failed: {req_key} (Expected >= {req_value}, Found: {inst_value})")
                    return False
        elif isinstance(req_value, str):  # String comparison
            if inst_value.lower() != req_value.lower():  # Case-insensitive comparison
                logger.info(f"Requirement failed: {req_key} (Expected: {req_value}, Found: {inst_value})")
                return False
        else:
            logger.info(f"Requirement failed: {req_key} (Unhandled comparison type for value: {req_value})")
            return False

    return True


def get_active_instance_with_requirements(requirements: dict):
    '''function that returns the first instance that meets the requirements.'''
    instance_ids = get_all_instance_ids()
    for instance_id in instance_ids:
        instance_state = get_instance_state(instance_id)
        if matches_requirements(instance_state, requirements):
            return instance_id
    return None


def get_active_or_launch_instance(requirements: dict, regions: List[str] = ['Europe', 'North_America']):
    '''function that returns the first instance that meets the requirements, or launches a new one.'''
    instance_id =  get_active_instance_with_requirements(requirements)
    if instance_id:
        return instance_id
    else:
        instance_creation = create_instance(
            **requirements,
        )
        return instance_creation.instance_id

