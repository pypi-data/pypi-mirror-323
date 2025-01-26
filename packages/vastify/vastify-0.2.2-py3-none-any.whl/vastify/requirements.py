from pydantic import BaseModel, Field
from typing import Optional, List
from .instance_state import InstanceState

class Requirements(BaseModel):
    gpu_name: Optional[str] = None
    price: Optional[float] = None  # Maximum acceptable price
    disk: Optional[float] = None  # Minimum disk space
    image: Optional[str] = None
    num_gpus: Optional[int] = None
    cpu_cores: Optional[int] = None
    ram: Optional[int] = None
    env: Optional[str] = None
    regions: Optional[List[str]] = None

    def matches(self, instance: InstanceState) -> bool:
        # Compare each field in the requirements with the instance
        if self.gpu_name and self.gpu_name.lower() != (instance.gpu_name or "").lower():
            return False
        if self.price and self.price < (instance.instance.totalHour or 0):
            return False
        if self.disk and self.disk > (instance.disk_space or 0):
            return False
        if self.image and self.image.lower() != (instance.image_uuid or "").lower():
            return False
        if self.num_gpus and self.num_gpus > (instance.num_gpus or 0):
            return False
        if self.cpu_cores and self.cpu_cores > (instance.cpu_cores_effective or 0):
            return False
        if self.ram and self.ram > (instance.cpu_ram or 0):
            return False
        if self.env and self.env not in [env[0] for env in (instance.extra_env or [])]:
            return False

        return True
