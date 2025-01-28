import subprocess

def install_cuda_version():
    print("Detected CPU-only PyTorch version.")
    print("Installing the CUDA version...")
    cuda_version = "cu118"
    torch_version = "2.2.1"
    torchvision_version = "0.17.1"
    index_url = "https://download.pytorch.org/whl/cu118"
    subprocess.check_call([
        "pip",
        "install",
        f"torch=={torch_version}+{cuda_version}",
        f"torchvision=={torchvision_version}+{cuda_version}",
        "--index-url",
        index_url
    ])

if __name__ == "__main__":
    install_cuda_version()
