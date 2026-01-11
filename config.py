OS_DESKTOP_MAP = {
    "alpine": ["i3", "kde", "mate", "xfce"], 
    "arch": ["i3", "kde", "mate", "xfce"],
    "debian": ["i3", "kde", "mate", "xfce"],
    "el": ["i3", "mate", "xfce"],
    "fedora": ["i3", "kde", "mate", "xfce"],
    "ubuntu": ["i3", "kde", "mate", "xfce"],
}

OS_OPTIONS = [
    ("Alpine", "alpine"),
    ("Arch", "arch"),
    ("Debian", "debian"),
    ("Enterprise Linux", "el"),
    ("Fedora", "fedora"),
    ("Ubuntu", "ubuntu"),
]

def get_desktop_label(key):
    return key.upper() if len(key) <= 3 else key.capitalize()
