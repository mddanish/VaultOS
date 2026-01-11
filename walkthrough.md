# VaultOS - Walkthrough

## 1. Introduction
VaultOS is a Python-based Terminal User Interface (TUI) for managing "Desktop" Docker containers (Linux environments with VNC/Webtop access). This walkthrough guides you through setup, running the application, and key workflows.

## 2. Prerequisites
- **Python 3.9+**
- **Docker Desktop** (running and managing Linux containers)
- **OS**: Windows or Linux (MacOS likely compatible but untested)

## 3. Installation & Setup
1.  **Clone/Open Project**: Ensure you are in the project root `c:\Users\mddan\.gemini\antigravity\playground\ghost-void`.
2.  **Virtual Environment**:
    ```powershell
    python -m venv venv
    .\venv\Scripts\activate
    ```
3.  **Install Dependencies**:
    ```powershell
    pip install textual docker
    ```

## 4. Running the Application
Execute the main entry point:
```powershell
python main.py
```
*Note: Ensure Docker Desktop is running before starting the app.*

## 5. Dashboard Overview
Upon launch, you will see the **VaultOS Dashboard**:
- **Grid**: Displays active VaultOS containers with columns for ID, Name, Status, OS, Desktop, Port, and Expiration.
- **Status Bar**: Shows Docker connection status (🟢/🔴), Engine version, and container counts.
- **Toolbar**: Buttons for `Create`, `Start`, `Stop`, `Delete`, and `Refresh` (Keybindings: `c`, `q`, `r`, `?`).

## 6. Creating a Container
Click **Create** or press `c` to open the Wizard.

### Step 1: Basics
- **Name**: Enter a unique name (e.g., `my-work`).
- **Port**: Host port to map (default `3001`). *Internal port is always 3000*.
- **Mode**:
    - **Default**: Quick ephemeral container.
    - **Persistent**: Maps a volume for data saving.
    - **Ephemeral**: Auto-deletes after a set time.

### Step 2: Details
- **OS**: Select distro (Alpine, Ubuntu, Arch, Fedora, etc.).
- **Desktop**: Select environment (XFCE, KDE, i3, MATE).
- *(If Ephemeral)*: Enter duration (e.g., `30s`, `2h`).
- *(If Persistent)*:
    - **Volume Path**: Enter host path (e.g., `C:/data/config`).
    - **Advanced Options**: Check this to enable custom user creation.

### Step 3: Advanced (Persistent Only)
- **Username**: Enter custom username (replaces default `abc`).
- **Home Map**: Host path to map to the user's home directory.

**Click 'Create'** to start.
*The app will automatically pull the image (showing a progress modal) and build the container. New containers are limited to 2 CPUs and 1GB RAM.*

## 7. Managing Containers
- **Select**: Use Up/Down arrows to highlight a container.
- **Start/Stop**: Use toolbar buttons to control lifecycle.
- **Delete**: Removes the container (forcefully).
- **Access**: Open your browser to `http://localhost:<PORT>` to access the Linux Desktop.

## 8. Troubleshooting
- **WebSocket/VNC Disconnects**: If using a custom user, ensure the container was created with the latest version of VaultOS, which patches LSIO scripts correctly.
- **Permission Errors**: Ensure Shared Drives/File Sharing is enabled in Docker Desktop if mapping Windows paths.
- **Logs**: If a creation fails, check the console output (where you ran `python main.py`) for detailed Docker build logs.
