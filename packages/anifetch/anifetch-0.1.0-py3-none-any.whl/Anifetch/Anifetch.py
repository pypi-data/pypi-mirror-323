
import os
import platform
import re
import subprocess
import random
from rich.console import Console
from rich.columns import Columns
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.style import Style
from Anifetch.ascii_arts import ascii_art_list

console = Console()

ascii_art = random.choice(ascii_art_list)

# Define themes
themes = {
    "dracula": {
        "title_style": "#bd93f9",
        "ascii_style": "#A94A4A", # change this for better visibility (not dracula)
        "info_style" : "#f8f8f2",
    },
    "monokai": {
        "title_style": "#f92672",
        "ascii_style": "#FAFFC5", # change this for better visibility (not monokai)
        "info_style" : "#f8f8f2"
    },
    "gruvbox": {
      "title_style": "#d3869b",
      "ascii_style": "#DF9755", # change this for better visibility (not gruvbox)
      "info_style": "#fbf1c7"
    }
}

# Randomly choose a theme
selected_theme = random.choice(list(themes.values()))

def get_os_info():
    os_name = platform.system()
    os_version = platform.release()
    os_arch = platform.machine()
    return f"{os_name} {os_version} {os_arch}"


def get_host_info():
    return platform.node()

def get_kernel_info():
    try:
        with open("/proc/version", "r") as f:
            kernel_info = f.read().strip()
        match = re.search(r"Linux ([\d\.]+)", kernel_info)
        if match:
          return f"Linux {match.group(1)}-generic"
        return "Unknown"
    except FileNotFoundError:
        return "Unknown"
def get_uptime():
  try:
    with open("/proc/uptime", "r") as f:
      uptime_seconds = float(f.readline().split()[0])
      uptime_minutes = int(uptime_seconds / 60)
      uptime_hours = uptime_minutes // 60
      uptime_minutes %= 60
      return f"{uptime_hours} hours, {uptime_minutes} mins"
  except FileNotFoundError:
    return "Unknown"

def get_package_info():
    dpkg_count = 0
    snap_count = 0

    try:
        dpkg_output = subprocess.check_output(["dpkg", "-l"], text=True, stderr=subprocess.DEVNULL)
        dpkg_count = len([line for line in dpkg_output.splitlines() if line.startswith("ii ")])

        snap_output = subprocess.check_output(["snap", "list"], text=True, stderr=subprocess.DEVNULL)
        snap_count = len(snap_output.splitlines()) - 1 # first line is table headers
    except FileNotFoundError:
        return "Unknown (dpkg), Unknown (snap)"
    return f"{dpkg_count} (dpkg), {snap_count} (snap)"

def get_shell_info():
    return os.environ.get("SHELL", "Unknown").split('/')[-1] + " " + os.environ.get("BASH_VERSION", "Unknown")[:6]


def get_display_info():
    try:
        xrandr_output = subprocess.check_output(["xrandr"], text=True, stderr=subprocess.DEVNULL)
    except FileNotFoundError:
        return ["Unknown", "Unknown"]

    display_info = []
    display_lines = xrandr_output.splitlines()
    connected_displays = []

    for line in display_lines:
      if " connected " in line:
        connected_displays.append(line.split()[0])


    for display in connected_displays:
      for line in display_lines:
        if line.strip().startswith(display + " connected "):
          res_match = re.search(r"(\d+x\d+)@([\d\.]+)", line)
          if res_match:
            resolution = res_match.group(1)
            refresh_rate = res_match.group(2)
            if "primary" in line:
              display_info.append(f"Display ({display}): {resolution} @ {refresh_rate} Hz in Unknown [Built-in] *")
            else:
               display_info.append(f"Display ({display}): {resolution} @ {refresh_rate} Hz in Unknown [External]")
          else:
            display_info.append(f"Display ({display}): Unknown")
    return display_info

def get_wm_info():
    try:
        wm_info = os.environ.get("DESKTOP_SESSION", "Unknown")
        if wm_info == "i3":
          return f"i3 (X11)"
        return f"{wm_info} (X11)"
    except FileNotFoundError:
        return "Unknown"

def get_theme_info():
    try:
      # Attempt to read GTK theme settings using gsettings
      theme_output = subprocess.check_output(["gsettings", "get", "org.gnome.desktop.interface", "gtk-theme"], text=True, stderr=subprocess.DEVNULL).strip().strip("'")
      return f"{theme_output} [GTK3]"
    except:
      return "Unknown"

def get_icons_info():
  try:
      # Attempt to read GTK theme settings using gsettings
    icon_output = subprocess.check_output(["gsettings", "get", "org.gnome.desktop.interface", "icon-theme"], text=True, stderr=subprocess.DEVNULL).strip().strip("'")
    return f"{icon_output} [GTK3]"
  except:
      return "Unknown"

def get_cursor_info():
    try:
        cursor_output = subprocess.check_output(["gsettings", "get", "org.gnome.desktop.interface", "cursor-theme"], text=True, stderr=subprocess.DEVNULL).strip().strip("'")
        return cursor_output
    except:
        return "Unknown"

def get_terminal_info():
    try:
        terminal_info = os.environ.get("TERM_PROGRAM", "Unknown")
        if terminal_info == "xterm-256color":
            return "x-terminal-emulator"
        return terminal_info
    except FileNotFoundError:
        return "Unknown"


def get_cpu_info():
    try:
      with open("/proc/cpuinfo", "r") as f:
        cpu_info = f.read()
      match = re.search(r"model name\s*:\s*(.+)", cpu_info)
      if match:
        model_name = match.group(1)
        core_count = os.cpu_count()
        clock_speed_match = re.search(r"@\s*([\d\.]+)\s*GHz", model_name)
        clock_speed = clock_speed_match.group(1) if clock_speed_match else "Unknown"
        return f"{model_name} ({core_count}) @ {clock_speed} GHz"
      return "Unknown"

    except FileNotFoundError:
      return "Unknown"


def get_gpu_info():
    try:
      lspci_output = subprocess.check_output(["lspci", "-v"], text=True, stderr=subprocess.DEVNULL)
    except:
      return "Unknown"

    gpu_info_lines = []
    for line in lspci_output.splitlines():
      if "VGA compatible controller" in line:
        gpu_info_lines.append(line)

    gpu_info_formatted = []
    for line in gpu_info_lines:
        match = re.search(r"VGA compatible controller:\s*(.+)", line)
        if match:
           gpu_name = match.group(1).strip()
           clock_speed = "Unknown" # TODO : find how to get gpu clock speed
           gpu_info_formatted.append(f"{gpu_name} @ {clock_speed} [Integrated]")
    return ", ".join(gpu_info_formatted) if gpu_info_formatted else "Unknown"


def get_memory_info():
    try:
      meminfo_output = subprocess.check_output(["free", "-m"], text=True, stderr=subprocess.DEVNULL).splitlines()
    except FileNotFoundError:
      return "Unknown"
    
    mem_line = meminfo_output[1].split()
    total_mem = int(mem_line[1])
    used_mem = int(mem_line[2])

    swap_line = meminfo_output[2].split()
    total_swap = int(swap_line[1])
    used_swap = int(swap_line[2])


    mem_percent = int((used_mem / total_mem) * 100)
    swap_percent = int((used_swap / total_swap) * 100)
    
    return (f"{used_mem / 1024:.2f} GiB / {total_mem / 1024:.2f} GiB ({mem_percent}%)",f"{used_swap / 1024:.2f} GiB / {total_swap / 1024:.2f} GiB ({swap_percent}%)" )



def get_disk_info():
    try:
        df_output = subprocess.check_output(["df", "-h"], text=True, stderr=subprocess.DEVNULL).splitlines()
    except FileNotFoundError:
        return ["Unknown"],[]
    disks_info = ""

    for line in df_output:
        if "/dev/" in line and "loop" not in line:
          parts = line.split()
          disk_name, total_space, used_space, _, mount_point = parts[0], parts[1], parts[2], parts[3], parts[5]
          if mount_point == "/":
            total_size = float(total_space.replace("G",""))
            used_size = float(used_space.replace("G",""))
            percent = int((used_size / total_size)*100)
            fs_type =  subprocess.check_output(["lsblk","-o","FSTYPE", disk_name],text=True,stderr=subprocess.DEVNULL).splitlines()[1].strip()
            disks_info = f"{used_space} / {total_space} ({percent}%) - {fs_type}"
    return disks_info


def get_local_ip_info():
    try:
        ip_output = subprocess.check_output(["ip", "addr"], text=True, stderr=subprocess.DEVNULL)
    except FileNotFoundError:
      return "Unknown"

    ip_lines = ip_output.splitlines()
    for line in ip_lines:
      if "inet " in line and "wlp" in line:
        match = re.search(r"inet\s+(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}/\d+)", line)
        if match:
          return f"{match.group(1)}"
    return "Unknown"

def get_battery_info():
  try:
    with open("/sys/class/power_supply/BAT0/capacity", "r") as f:
      capacity = f.readline().strip()

    with open("/sys/class/power_supply/BAT0/status", "r") as f:
      status = f.readline().strip()
    ac_connected = "[AC Connected]" if status == "Charging" or status == "Full" else ""
    
    return f"100% {ac_connected}" if capacity =="100" else f"{capacity}% {ac_connected}"

  except FileNotFoundError:
     return "Unknown"


def get_locale_info():
  return os.environ.get("LANG", "Unknown")

def getUser():
    command = ["whoami"]

    result = subprocess.run(command, capture_output=True, text=True)
    return result.stdout.strip()


def main():

  # Apply the selected theme styles to the text
  system_info_content = [
      Text(f"OS: ", style=Style(bold=True, color=selected_theme["title_style"])) + Text(get_os_info(), style=selected_theme["info_style"]),
      Text(f"Host: ", style=Style(bold=True, color=selected_theme["title_style"])) + Text(get_host_info(), style=selected_theme["info_style"]),
      Text(f"Uptime: ", style=Style(bold=True, color=selected_theme["title_style"])) + Text(get_uptime(), style=selected_theme["info_style"]),
      Text(f"Packages: ", style=Style(bold=True, color=selected_theme["title_style"])) + Text(get_package_info(), style=selected_theme["info_style"]),
  ]

  system_info_content.extend([
      Text(f"WM: ", style=Style(bold=True, color=selected_theme["title_style"])) + Text(get_wm_info(), style=selected_theme["info_style"]),
      Text(f"CPU: ", style=Style(bold=True, color=selected_theme["title_style"])) + Text(get_cpu_info(), style=selected_theme["info_style"]),
      Text(f"GPU: ", style=Style(bold=True, color=selected_theme["title_style"])) + Text(get_gpu_info(), style=selected_theme["info_style"]),
  ])

  memory_info, swap_info = get_memory_info()

  system_info_content.extend([
      Text(f"Memory: ", style=Style(bold=True, color=selected_theme["title_style"])) + Text(memory_info, style=selected_theme["info_style"]),
      Text(f"Swap: ", style=Style(bold=True, color=selected_theme["title_style"])) + Text(swap_info, style=selected_theme["info_style"]),
  ])

  disk_info = get_disk_info()

  system_info_content.extend([
    Text("Disk (/): ", style=Style(bold=True, color=selected_theme["title_style"])) + Text(disk_info, style=selected_theme["info_style"])
  ])

  system_info_content.extend([
      Text(f"Local IP (wlp3s0): ", style=Style(bold=True, color=selected_theme["title_style"])) + Text(get_local_ip_info(), style=selected_theme["info_style"]),
      Text(f"Battery (ASUS Battery): ", style=Style(bold=True, color=selected_theme["title_style"])) + Text(get_battery_info(), style=selected_theme["info_style"]),
      Text(f"Locale: ", style=Style(bold=True, color=selected_theme["title_style"])) + Text(get_locale_info(), style=selected_theme["info_style"])
  ])

  system_info_panel = Panel(
      Text("\n").join(system_info_content),
      title=Text(f"{getUser()}@{getUser()}-{get_host_info()}", style=Style(bold=True, color="white")),
  )

  table = Table.grid(padding=(0, 2))  # Add some padding to the table
  table.add_column(ratio=1)
  table.add_column(ratio=2)
  table.add_row(Text(ascii_art, style=selected_theme["ascii_style"]), system_info_panel)

  console.print(table)

if __name__ == "__main__":
  main()