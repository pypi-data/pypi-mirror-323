import subprocess

def get_vpn_status():
    # cloudflare warp
    try:
        warp_output = subprocess.check_output(['warp-cli', 'status'], stderr=subprocess.STDOUT, text=True).strip()
        if "Connected" in warp_output:
            return "WARP: Connected"
        elif "Disconnected" in warp_output:
            return "WARP: Disconnected"
    except (FileNotFoundError, subprocess.CalledProcessError):
        pass

    # proton vpn old cli
    try:
        proton_output = subprocess.check_output(['protonvpn-cli', 's'], stderr=subprocess.STDOUT, text=True).strip()
        if "Connected" in proton_output:
            return "ProtonVPN: Connected"
        elif "Disconnected" in proton_output:
            return "ProtonVPN: Disconnected"
    except (FileNotFoundError, subprocess.CalledProcessError):
        pass

    # proton vpn new cli
    try:
        proton_output = subprocess.check_output(['protonvpn', 's'], stderr=subprocess.STDOUT,
                                                    text=True).strip()
        if "Connected" in proton_output:
            return "ProtonVPN: Connected"
        elif "Disconnected" in proton_output:
            return "ProtonVPN: Disconnected"
    except (FileNotFoundError, subprocess.CalledProcessError):
        pass

    # TODO: add more vpns

    return "No VPN"

# Example usage
if __name__ == "__main__":
    print(get_vpn_status())
