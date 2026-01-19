import psutil
import cpuinfo
import GPUtil
import platform
import subprocess

def test_detection():
    print("--- Test de Detección ---")
    try:
        cpu = cpuinfo.get_cpu_info().get('brand_raw', "Unknown")
        print(f"CPU: {cpu}")
    except Exception as e:
        print(f"Error CPU: {e}")

    try:
        ram = round(psutil.virtual_memory().total / (1024**3), 2)
        print(f"RAM: {ram} GB")
    except Exception as e:
        print(f"Error RAM: {e}")

    try:
        gpus = GPUtil.getGPUs()
        gpu = gpus[0].name if gpus else "None"
        print(f"GPU: {gpu}")
    except Exception as e:
        print(f"Error GPU: {e}")

    try:
        cmd = 'wmic diskdrive get model,size,mediatype /format:list'
        output = subprocess.check_output(cmd, shell=True).decode('utf-8')
        print(f"Storage:\n{output}")
    except Exception as e:
        print(f"Error Storage: {e}")

if __name__ == "__main__":
    test_detection()
