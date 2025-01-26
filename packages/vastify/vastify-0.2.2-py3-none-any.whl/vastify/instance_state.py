from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Union


class InstanceDetails(BaseModel):
    gpuCostPerHour: Optional[float] = Field(None, alias="gpuCostPerHour")
    diskHour: Optional[float]
    totalHour: Optional[float]
    discountTotalHour: Optional[float]
    discountedTotalPerHour: Optional[float]


class Ports(BaseModel):
    HostIp: str
    HostPort: str


class InstanceState(BaseModel):
    actual_status: Optional[str]
    bundle_id: Optional[int]
    bw_nvlink: Optional[float]
    client_run_time: Optional[float]
    compute_cap: Optional[int]
    cpu_arch: Optional[str]
    cpu_cores: Optional[int]
    cpu_cores_effective: Optional[float]
    cpu_name: Optional[str]
    cpu_ram: Optional[int]
    cpu_util: Optional[float]
    credit_balance: Optional[Union[float, None]]
    credit_discount: Optional[Union[float, None]]
    credit_discount_max: Optional[float]
    cuda_max_good: Optional[float]
    cur_state: Optional[str]
    direct_port_count: Optional[int]
    direct_port_end: Optional[int]
    direct_port_start: Optional[int]
    disk_bw: Optional[float]
    disk_name: Optional[str]
    disk_space: Optional[float]
    disk_usage: Optional[float]
    disk_util: Optional[float]
    dlperf: Optional[float]
    dlperf_per_dphtotal: Optional[float]
    dph_base: Optional[float]
    dph_total: Optional[float]
    driver_version: Optional[str]
    duration: Optional[float]
    end_date: Optional[float]
    external: Optional[bool]
    extra_env: Optional[List[List[Union[str, int]]]]
    flops_per_dphtotal: Optional[float]
    geolocation: Optional[str]
    gpu_arch: Optional[str]
    gpu_display_active: Optional[bool]
    gpu_frac: Optional[float]
    gpu_lanes: Optional[int]
    gpu_mem_bw: Optional[float]
    gpu_name: Optional[str]
    gpu_ram: Optional[int]
    gpu_temp: Optional[float]
    gpu_totalram: Optional[int]
    gpu_util: Optional[float]
    has_avx: Optional[int]
    host_id: Optional[int]
    host_run_time: Optional[float]
    hosting_type: Optional[str]
    id: Optional[int]
    image_args: Optional[List[str]]
    image_runtype: Optional[str]
    image_uuid: Optional[str]
    inet_down: Optional[float]
    inet_down_billed: Optional[float]
    inet_down_cost: Optional[float]
    inet_up: Optional[float]
    inet_up_billed: Optional[float]
    inet_up_cost: Optional[float]
    instance: Optional[InstanceDetails]
    intended_status: Optional[str]
    internet_down_cost_per_tb: Optional[float]
    internet_up_cost_per_tb: Optional[float]
    is_bid: Optional[bool]
    jupyter_token: Optional[str]
    label: Optional[str]
    local_ipaddrs: Optional[str]
    logo: Optional[str]
    machine_dir_ssh_port: Optional[int]
    machine_id: Optional[int]
    mem_limit: Optional[float]
    mem_usage: Optional[float]
    min_bid: Optional[float]
    mobo_name: Optional[str]
    next_state: Optional[str]
    num_gpus: Optional[int]
    onstart: Optional[str]
    os_version: Optional[str]
    pci_gen: Optional[float]
    pcie_bw: Optional[float]
    ports: Optional[Dict[str, List[Ports]]]
    public_ipaddr: Optional[str]
    reliability2: Optional[float]
    rentable: Optional[bool]
    score: Optional[float]
    search: Optional[InstanceDetails]
    ssh_host: Optional[str]
    ssh_idx: Optional[str]
    ssh_port: Optional[int]
    start_date: Optional[float]
    static_ip: Optional[bool]
    status_msg: Optional[str]
    storage_cost: Optional[float]
    storage_total_cost: Optional[float]
    template_hash_id: Optional[str]
    template_id: Optional[int]
    time_remaining: Optional[str]
    time_remaining_isbid: Optional[str]
    total_flops: Optional[float]
    uptime_mins: Optional[float]
    verification: Optional[str]
    vmem_usage: Optional[float]
    vram_costperhour: Optional[float]
    webpage: Optional[str]
    template_name: Optional[str] = Field(default=None)

if __name__ == '__main__':
    # Example: Parse JSON to InstanceState
    example_data = {
        "actual_status": "running",
        "bundle_id": 390473367,
        "gpu_name": "RTX 2080 Ti",
        "cpu_cores_effective": 8.0,
        "cpu_ram": 257783,
        "disk_space": 100.0,
        "instance": {
            "gpuCostPerHour": 0.16666666666666666,
            "diskHour": 0.027777777777777776,
            "totalHour": 0.19444444444444442
        },
        "ssh_host": "ssh8.vast.ai",
        "ssh_port": 36748,
        "geolocation": "Minnesota, US"
    }

    # Parse JSON into Pydantic model
    instance = InstanceState(**example_data)
    print(instance.gpu_name)  # Output: RTX 2080 Ti
