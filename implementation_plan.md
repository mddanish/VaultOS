# VaultOS Implementation Plan

## Project Overview
VaultOS is a Terminal User Interface (TUI) application designed to manage Docker containers with a specific focus on "Desktop" containers (e.g., Linux environments accesible via Webtop/VNC). It leverages the Textual framework for the UI and the Docker SDK for Python for container management.

## Current Status
**Version:** 1.0.0
**Core Framework:** Python, Textual, Docker SDK
**OS Compatibility:** Windows (Dev), Linux (Target)

## Completed Features

### 1. Dashboard & UI
- [x] **Responsive Grid**: Dynamic column sizing based on terminal width with vertical separator lines.
- [x] **Real-time Updates**: Auto-refreshing container list (1s interval) with threaded background polling to prevent UI freezes.
- [x] **Information Display**:
    - Container ID, Name, Status.
    - OS & Desktop Environment Detection (parsed from image tags).
    - Host Port mapping (Standardized to internal port 3000).
    - Expiration Countdown (DD:HH:MM:SS) for ephemeral containers.
- [x] **Styling**: Custom "VaultOS" branding, distinct button styles (Primary, Success, Warning, Error), and standardized sizing.
- [x] **About Modal**: Pop-up with developer and project information.

### 2. Container Management
- [x] **Strict Filtering**: Dashboard only displays containers labeled `app=vaultOS` or matching the `vaultos-` name prefix.
- [x] **Lifecycle Control**: Start, Stop, Delete, and Refresh functionalities.
- [x] **Resource Limits**: Enforced 2 CPU cores and 1GB RAM limits on all new containers.

### 3. Container Creation Wizard
- [x] **Multi-Step Flow**:
    1.  **Basics**: Name, Port, Mode Selection (Default, Persistent, Ephemeral).
    2.  **Details**: OS (Alpine, Ubuntu, Arch, etc.) and Desktop (XFCE, KDE, i3, MATE) selection.
    3.  **Advanced**: (Conditional) Username and Home Directory mapping.
- [x] **Modes**:
    -   **Default**: Standard ephemeral container.
    -   **Ephemeral**: Auto-expiring containers with user-defined timers (e.g., "30s", "1h").
    -   **Persistent**: Volume-mapped containers for data persistence.
- [x] **Advanced Configuration**:
    -   **Custom User Support**: Robust logic to rename the default `abc` user in LSIO images to a custom username.
    -   **Environment Patching**: Automatically patches `/etc/cont-init.d` and other LSIO scripts to ensure VNC/WebSocket services run as the custom user.
    -   **Filesystem Management**: Handles home directory creation/migration and config ownership logic compatible with various distros.

### 4. Code Architecture
- [x] **Modular Structure**:
    -   `main.py`: Core App and UI Logic.
    -   `docker_manager.py`: Docker interaction logic (Tag parsing, build, run, prune).
    -   `ui/modals.py`: Modal definitions (Wizard, Progress, About).
    -   `config.py`: Constants and mappings.
- [x] **Robustness**:
    -   Threaded operations for heavy I/O (Image pulls, Container listing).
    -   Cross-platform path handling (Windows/Linux adaptivity).
    -   Comprehensive error notifications.

## Recent Updates (Session Log)
- **Refinement**: Added vertical grid lines to the dashboard.
- **Optimization**: Moved Docker polling to a background thread.
- **Fix**: Resolved "WebSocket disconnected" issues in custom user mode by aggressively patching LSIO service scripts and explicitly setting `ENV USER`.
- **Refactor**: Split monolithic `main.py` into modules.
- **Branding**: Renamed to "VaultOS" with subtitle "Desktop Container Manager".

## Future Roadmap / Remaining Tasks
- [ ] **Logging View**: Add ability to view live logs of a selected container within the TUI.
- [ ] **Shell Access**: functionality to `exec` into a container directly from the TUI (if possible via Textual).
- [ ] **Network Management**: options for Bridge vs Host networking in the wizard.
- [ ] **Image Caching Strategy**: Better management of downloaded images (Prune unused images option).
- [ ] **Distribution Testing**: Verify custom user logic on Arch, Fedora, and Ubuntu base images (currently validated on Alpine).
