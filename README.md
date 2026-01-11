# VaultOS
### A Simple Desktop Container Manager

VaultOS is a terminal-based user interface (TUI) for managing "Desktop" Docker containers. It allows you to effortlessly spin up ephemeral or persistent Linux desktop environments (like Alpine XFCE, Ubuntu KDE, etc.) accessible directly via your web browser.

Built with Python and [Textual](https://textual.textualize.io/).

---

## 🏗️ Features

*   **Dashboards**: Real-time overview of active containers with connection status and resource usage.
*   **Creation Wizard**: Step-by-step wizard to deploy new desktops.
    *   **Multiple Distros**: Alpine, Ubuntu, Fedora, Arch, and more.
    *   **Desktop Environments**: XFCE, KDE, MATE, i3.
*   **Modes**:
    *   **Ephemeral**: Temporary disposable desktops with auto-expiry timers (e.g., "30s", "1h").
    *   **Persistent**: Durable environments with data persistence.
*   **Advanced Configuration**: Custom usernames, home directory mapping, and VNC configuration patching.
*   **Cross-Platform**: Automatic path handling for Windows and Linux.

---

## 💡 Why VaultOS?

VaultOS serves as a lightweight, terminal-centric alternative to robust but complex solutions like **KASM Workspaces**.

*   **vs KASM**: KASM is a full enterprise suite requiring significant setup and resources. **VaultOS** is designed for developers and power users who want *instant*, disposable, or persistent desktops directly from their CLI without managing heavy infrastructure.
*   **Simplicity**: No web admins, no databases—just Python, Docker, and your terminal.

---

## ⚙️ Prerequisites

### 1. Docker
You must have Docker installed and running.

*   **Windows / Mac**: Download [Docker Desktop](https://www.docker.com/products/docker-desktop/).
    *   *Windows Tip*: Ensure "File Sharing" is enabled for your C: drive if mapping volumes.
*   **Linux**:
    ```bash
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    ```

### 2. Python
Requires **Python 3.9** or higher.

---

## 🚀 Installation & Quick Start

### 1. Download & Extract
Clone the repository or download the ZIP file and extract it to a folder (e.g., `vaultos`).

### 2. Setup Environment

**Windows (PowerShell)**:
```powershell
# Navigate to folder
cd vaultos

# Create Virtual Environment
python -m venv venv

# Activate
.\venv\Scripts\activate

# Install Dependencies
pip install textual docker
```

**Linux / Mac**:
```bash
# Navigate to folder
cd vaultos

# Create Virtual Environment
python3 -m venv venv

# Activate
source venv/bin/activate

# Install Dependencies
pip install textual docker
```

---

## 🎮 Usage Guide

Start the application:
```bash
python main.py
```

### The Dashboard
*   **Navigation**: Use arrow keys to select containers.
*   **Keybindings**:
    *   `c`: Create New Container
    *   `r`: Refresh List
    *   `q`: Quit
    *   `?`: About / Developer Info

### Creating a Desktop Container
1.  Press `c` to open the Wizard.
2.  **Basic Config**: Set a name (e.g., `dev-box`) and a local port (e.g., `3001`).
3.  **Choose Mode**:
    *   **Default**: Quick Alpine/XFCE box.
    *   **Ephemeral**: Add a timer (e.g., `2h`) to auto-delete the container.
    *   **Persistent**: Map a local folder to safeguard your data.
4.  **OS Selection**: Choose your flavor (Ubuntu, Arch, etc.).
5.  **Advanced (Persistent Only)**: 
    *   Define a **Custom Username** (replaces the default `abc`).
    *   Map your Home Directory for seamless file access.
    *   *Note: VaultOS automatically patches system scripts to ensure VNC works with your custom user.*

### Accessing the Desktop
Once running, open your browser and go to:
`http://localhost:<PORT>` (e.g., http://localhost:3001)

---

## ⚠️ Important Notes & Warnings

*   **VNC/WebSocket Issues**: If you use a custom username and experience disconnection, ensure you are using the latest version of VaultOS. The application patches internal container scripts (`/etc/cont-init.d`) to match your username.
*   **Volume Permissions**: On Linux, creating persistent volumes might result in files owned by `root` or `1000:1000`. VaultOS attempts to `chown` directories, but user-namespace remapping in standard Docker can vary.
*   **Resource Limits**: To prevent system overload, VaultOS limits all managed containers to **2 CPU Cores** and **1GB RAM** by default.

---

## 🔮 Roadmap

### TUI Enhancements
*   [ ] Live Log Viewer within the TUI.
*   [ ] Direct Shell Access (`exec`) from the dashboard.
*   [ ] Network Configuration (Bridge/Host mode toggles).

### VaultOS Web (Future)
*   [ ] **Web-Based Interface**: A full browser-based dashboard to manage containers remotely without a terminal.
*   [ ] **User Authentication**: Secure login system with role-based access control.
*   [ ] **Session Management**: Persistent user sessions and connection history.
*   [ ] **Advanced Image Management**: 
    *   GUI for pulling/updating images.
    *   Support for **Custom Images** (pre-loaded with specific apps/tools).
    *   "App Store" style browser for available desktop environments.

---

## 👨‍💻 Developer Guide

**Author**: Mohammed Danish Amber  
**Email**: md.danish.amber@live.com  
**Repository**: [github.com/mddanish/vaultos](https://github.com/mddanish/vaultos)

*Built with ❤️ for the open-source community.*

---

## 🏆 Credits & Acknowledgments

*   **[LinuxServer.io](https://www.linuxserver.io/)**: A massive thank you to the LSIO team for their incredible work on [Webtop](https://docs.linuxserver.io/images/docker-webtop) Docker images. VaultOS relies heavily on these high-quality, base images to provide smooth, functional desktop environments.

---

## 📜 License

This project is licensed under the **GNU Affero General Public License v3.0 (AGPL-3.0)**.

You are free to use, modify, and distribute this software, but network use is considered distribution. If you run a modified version of this software over a network, you must make the source code available to users.

See [LICENSE](LICENSE) for more details.
