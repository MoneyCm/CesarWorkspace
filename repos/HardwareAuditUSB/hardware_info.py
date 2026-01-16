import platform
import psutil
import cpuinfo
import GPUtil
import os
import sys

def get_size(bytes, suffix="B"):
    """
    Scale bytes to its proper format
    e.g:
        1253656 => '1.20MB'
        1253656678 => '1.17GB'
    """
    factor = 1024
    for unit in ["", "K", "M", "G", "T", "P"]:
        if bytes < factor:
            return f"{bytes:.2f}{unit}{suffix}"
        bytes /= factor
    return f"{bytes:.2f}Y{suffix}"

def get_system_info():
    info = {}
    
    # OS
    try:
        info['os'] = f"{platform.system()} {platform.release()} ({platform.version()})"
    except:
        info['os'] = "Desconocido"

    # CPU
    try:
        cpu_raw = cpuinfo.get_cpu_info()
        info['cpu_model'] = cpu_raw.get('brand_raw', 'Desconocido')
        info['cpu_cores'] = f"Físicos: {psutil.cpu_count(logical=False)}, Lógicos: {psutil.cpu_count(logical=True)}"
        # Frequency might not be available on all systems/permissions
        try:
            freq = psutil.cpu_freq()
            info['cpu_freq'] = f"{freq.current:.1f}Mhz" if freq else "N/A"
        except:
             info['cpu_freq'] = "N/A"
    except Exception as e:
        info['cpu_model'] = f"Error: {str(e)}"
        info['cpu_cores'] = "N/A"

    # RAM
    try:
        svmem = psutil.virtual_memory()
        info['ram_total'] = get_size(svmem.total)
        info['ram_used'] = get_size(svmem.used)
        info['ram_percent'] = f"{svmem.percent}%"
        info['ram_total_bytes'] = svmem.total # For logic
    except:
        info['ram_total'] = "Error"
        info['ram_total_bytes'] = 0

    # GPU
    try:
        gpus = GPUtil.getGPUs()
        if gpus:
            gpu_list = []
            for gpu in gpus:
                gpu_name = gpu.name
                gpu_mem = f"{gpu.memoryTotal}MB"
                gpu_list.append(f"{gpu_name} ({gpu_mem})")
            info['gpu'] = ", ".join(gpu_list)
        else:
            info['gpu'] = "No se detectó GPU dedicada / Integrada no soportada por GPUtil"
    except:
        info['gpu'] = "Error al detectar GPU"

    # Storage
    try:
        partitions = psutil.disk_partitions()
        disk_info = []
        main_disk_type = "Desconocido"
        
        for partition in partitions:
            try:
                partition_usage = psutil.disk_usage(partition.mountpoint)
                total = get_size(partition_usage.total)
                free = get_size(partition_usage.free)
                disk_info.append(f"{partition.device} ({partition.mountpoint}): {free} libres de {total}")
                
                # Check if C: (Windows) or / (Linux)
                if (platform.system() == 'Windows' and 'C:' in partition.device) or \
                   (platform.system() != 'Windows' and partition.mountpoint == '/'):
                       # Basic SSD detection for Windows
                       if platform.system() == 'Windows':
                           try:
                               # Powershell command to get media type
                               import subprocess
                               cmd = f"Get-PhysicalDisk | Select-Object FriendlyName, MediaType"
                               out = subprocess.check_output(["powershell", "-Command", cmd], shell=True).decode()
                               if "SSD" in out:
                                   main_disk_type = "SSD"
                               elif "HDD" in out:
                                   main_disk_type = "HDD"
                           except:
                               pass
            except PermissionError:
                continue
                
        info['storage'] = "; ".join(disk_info)
        info['main_disk_type'] = main_disk_type
    except:
        info['storage'] = "Error leyendo discos"
        info['main_disk_type'] = "Desconocido"

    return info
