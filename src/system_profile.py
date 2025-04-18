import platform
import subprocess


def print_proc_info(save=False):
    """
    Print CPU information
    """

    num_core, num_logical_core = 0, 0
    max_freq, min_freq = 0.0, 0.0
    l1d, l1i, l2, l3 = 0, 0, 0, 0
    model_name = ""

    system = platform.system()
    match system:
        case "Darwin":
            pass
        case "Linux":
            # for later, add exception and then proc cpu info and also make sure works amd arm
            lscpu = subprocess.run(
                "lscpu | grep  "
                '-e "^CPU(s):" '
                '-e "^Core(s) per socket:" '
                '-e "^CPU ... MHz:" '
                '-e "^L.*cache:" '
                '-e "Model name:"',
                shell=True,
                capture_output=True,
            )

            stdout = lscpu.stdout.decode("utf-8").splitlines()
            model_name = stdout[2].split(":")[1].strip()

            stdout = ["".join(line.split()) for line in stdout]
            num_core = int(stdout[1].split(":")[1])
            num_logical_core = int(stdout[0].split(":")[1])

            max_freq = float(stdout[3].split(":")[1])
            min_freq = float(stdout[4].split(":")[1])
            l1d = int(stdout[5].split(":")[1][:-1])
            l1i = int(stdout[6].split(":")[1][:-1])
            l2 = int(stdout[7].split(":")[1][:-1])
            l3 = int(stdout[8].split(":")[1][:-1])
            simd_version = ""
    cpu_profile = str()
    if num_core:
        cpu_profile += f"Physical Cores: {num_core}\n"
    if num_logical_core:
        cpu_profile += f"Logical Cores: {num_logical_core}\n"
    if model_name:
        cpu_profile += f"Model: {model_name}\n"
    if max_freq:
        cpu_profile += f"Max Freq: {max_freq/1000:.2f} GHz\n"
    if min_freq:
        cpu_profile += f"Min Freq: {min_freq/1000:.2f} GHz\n"
    if l1d:
        cpu_profile += f"L1d: {l1d} KiB\n"
    if l1i:
        cpu_profile += f"L1i: {l1i} KiB\n"
    if l2:
        cpu_profile += f"L2: {l2:,} KiB\n"
    if l3:
        cpu_profile += f"L3: {l3:,} KiB ({int(l3/1024)} MiB)\n"
    print(cpu_profile)
    if save:
        with open("aux/system_profile.txt", "w") as f:
            f.write(cpu_profile)
            f.close()
    return


def print_gcc_info(save=False):
    gcc = subprocess.run("gcc --version", shell=True, capture_output=True)
    gcc_version = gcc.stdout.decode("utf-8").splitlines()[0]
    print(gcc_version)
    if save:
        with open("data/system_profile.txt", "a") as f:
            f.write("\n" + gcc_version)
            f.close()
    return


if __name__ == "__main__":
    print_proc_info(save=True)
    print_gcc_info(save=True)
