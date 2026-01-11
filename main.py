from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Header, Footer, DataTable, Button, Static
from textual import on, work
from docker_manager import DockerManager
from ui.modals import DownloadProgressModal, CreateContainerModal, AboutModal
import asyncio

class VaultOSApp(App):
    """A TUI to manage vaultOS containers."""
    TITLE = "VaultOS"
    SUB_TITLE = "Desktop Container Manager"
    CSS = """
    Screen {
        layout: vertical;
    }
    DataTable {
        height: 1fr;
        border: solid cyan;
    }
    #bottom_container {
        height: auto;
        /* dock: bottom; Removed to let it stack naturally above footer */
    }
    #statusbar {
        height: 1;
        background: $surface;
        color: $text;
        content-align: center middle; 
    }
    #toolbar {
        height: 3;
        padding: 1 0; /* 1 top, 1 bottom */
        background: $boost;
        align: center middle; 
    }
    #toolbar Button {
        margin: 0 2; /* Increased margin for better separation */
        height: 1; 
        border: none;
        padding: 0;
        width: 14; /* Standard fixed width */
        content-align: center middle;
    }
    #btn_refresh {
        background: cyan;
        color: black;
    }
    """
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("r", "refresh_list", "Refresh"),
        ("c", "create_container", "Create Container"),
        ("?", "show_about", "About"),
    ]

    def action_show_about(self):
        self.push_screen(AboutModal())

    def on_mount(self):
        self.manager = None
        try:
            self.manager = DockerManager()
        except RuntimeError as e:
            self.notify(str(e), severity="error", timeout=10)
        
        table = self.query_one(DataTable)
        
        # Dynamic Column Sizing based on Terminal Width
        screen_width = self.app.console.size.width
        # Reserve space for borders, scrollbars, and EXTENSIVE column padding.
        # We have 13 columns (7 data + 6 separators). Textual adds padding to EACH column.
        # 13 cols * 2 padding = ~26 chars. Plus scrollbar + borders + separator widths (6).
        # Total deduction needs to be high: ~40-50 chars.
        usable_width = max(50, screen_width - 50)
        
        # Percentages: ID 15%, Name 30%, Status 10%, OS 10%, Desktop 15%, Port 10%, Expires 10%
        # Calculate widths for data columns
        w_id = int(usable_width * 0.15)
        w_name = int(usable_width * 0.30)
        w_status = int(usable_width * 0.10)
        w_os = int(usable_width * 0.10)
        w_desktop = int(usable_width * 0.15)
        w_port = int(usable_width * 0.10)
        w_expires = int(usable_width * 0.10)

        sep = "│"
        
        table.add_column("ID", width=w_id)
        table.add_column(sep, width=1)
        table.add_column("Name", width=w_name)
        table.add_column(sep, width=1)
        table.add_column("Status", width=w_status)
        table.add_column(sep, width=1)
        table.add_column("OS", width=w_os)
        table.add_column(sep, width=1)
        table.add_column("Desktop", width=w_desktop)
        table.add_column(sep, width=1)
        table.add_column("Port", width=w_port)
        table.add_column(sep, width=1)
        table.add_column("Expires", width=w_expires)
        table.cursor_type = "row"
        table.zebra_stripes = True
        
        self.action_refresh_list()
        self.set_interval(1, self.check_expiration) # Update every 1s for countdown

    def check_expiration(self):
        """Called every 1s to trigger refresh (which handles pruning)."""
        self.action_refresh_list()

    def compose(self) -> ComposeResult:
        yield Header()
        yield DataTable()
        with Vertical(id="bottom_container"):
             yield Static(id="statusbar")
             with Horizontal(id="toolbar"):
                yield Button("Create", variant="primary", id="btn_create")
                yield Button("Start", variant="success", id="btn_start")
                yield Button("Stop", variant="warning", id="btn_stop")
                yield Button("Delete", variant="error", id="btn_delete")
                yield Button("Refresh", id="btn_refresh")
        yield Footer()

    def update_status_bar(self):
        status_bar = self.query_one("#statusbar", Static)
        if not self.manager:
             status_bar.update("🔴 Docker Disconnected | Ver: N/A")
             return

        info = self.manager.get_system_info()
        icon = "🟢" if info['connected'] else "🔴"
        ver = f"Docker v{info['engine_version']} (API {info['api_version']})"
        total = info['total']
        running = info['running']
        stopped = info['stopped']
        stats = f"Status Total: {total} ({running}/{stopped})" 
        content = f"{icon} {ver} | {stats}"
        status_bar.update(content)

    @work(exclusive=True)
    async def action_refresh_list(self):
        if not self.manager:
             self.update_status_bar()
             return
        
        try:
            # Run blocking Docker IO in a separate thread to keep UI responsive
            containers = await asyncio.to_thread(self.manager.get_and_prune_containers)
        except Exception as e:
            self.notify(f"Error fetching containers: {e}", severity="error")
            self.query_one("#statusbar", Static).update("🔴 Error fetching data")
            return

        # UI Updates happen on main thread (async method context is main thread)
        try:
            table = self.query_one(DataTable)
        except:
             return

        selected_row = table.cursor_row
        table.clear()
        
        try:
            import time
            now = time.time()

            for c in containers:
                # Extract Port
                ports = c.attrs['NetworkSettings']['Ports']
                host_port = "N/A"
                if ports and '3000/tcp' in ports and ports['3000/tcp']:
                    host_port = ports['3000/tcp'][0]['HostPort']
                
                # Extract OS/Desktop from Image Tag
                image_tag = c.image.tags[0] if c.image.tags else "unknown"
                os_name = "N/A"
                desktop = "N/A"
                tag_suffix = image_tag.split(":")[-1]
                if tag_suffix == "latest":
                    os_name = "Alpine"
                    desktop = "XFCE"
                else:
                    parts = tag_suffix.split("-")
                    if len(parts) >= 3:
                         os_name = parts[1].capitalize()
                         desktop = parts[2].upper()
                    elif len(parts) == 2:
                         os_name = parts[0].capitalize()
                         desktop = parts[1].upper()
                
                # Expiry
                expiry_ts = c.labels.get('vaultos.expires')
                expiry_str = "No Expire"
                if expiry_ts:
                    remaining = float(expiry_ts) - now
                    if remaining > 0:
                        m, s = divmod(int(remaining), 60)
                        h, m = divmod(m, 60)
                        d, h = divmod(h, 24)
                        expiry_str = f"{d:02d}:{h:02d}:{m:02d}:{s:02d}"
                    else:
                        expiry_str = "Expired"

                sep = "│"
                table.add_row(
                    c.short_id, sep,
                    c.name, sep,
                    c.status, sep,
                    os_name, sep,
                    desktop, sep,
                    host_port, sep,
                    expiry_str, 
                    key=c.id
                )
            
            if selected_row is not None and selected_row < len(containers):
                 table.cursor_coordinate = (selected_row, 0)

            self.update_status_bar()
            
        except Exception as e:
            self.notify(f"Error updating UI: {e}", severity="error")

    def get_selected_container_id(self):
        table = self.query_one(DataTable)
        try:
            if table.cursor_row is None:
                 return None
            row_key = table.coordinate_to_cell_key(table.cursor_coordinate).row_key
            return row_key.value # key was passed as string c.id
        except:
             return None

    @on(Button.Pressed, "#btn_create")
    def on_create_btn(self):
        self.action_create_container()

    def action_create_container(self):
        if not self.manager:
             self.notify("Docker not connected.", severity="error")
             return
        
        def handle_create(result):
            if result:
                self.notify(f"Creating container {result['name']}... (Mode: {result['type']})")
                # Run creation in background worker (managed by textual)
                self.create_container_worker(result)

        self.push_screen(CreateContainerModal(), handle_create)

    @work(exclusive=True, thread=True)
    def create_container_worker(self, config):
        dl_modal = DownloadProgressModal()
        is_downloading = False
        
        def progress_handler(msg: str):
             # This runs in worker thread. Schedule update on main thread.
             nonlocal is_downloading
             if not is_downloading:
                 self.app.call_from_thread(self.push_screen, dl_modal)
                 is_downloading = True
             
             self.app.call_from_thread(dl_modal.update_status, msg)

        try:
            # We pass the callback. The manager will invoke it if it downloads.
            cid = self.manager.create_container(config, progress_callback=progress_handler)
            
            if is_downloading:
                self.app.call_from_thread(dl_modal.dismiss)
                
            self.app.call_from_thread(self.notify, f"Container Created: {cid}", severity="success")
            self.app.call_from_thread(self.action_refresh_list)
        except Exception as e:
            if is_downloading:
                self.app.call_from_thread(dl_modal.dismiss)
            self.app.call_from_thread(self.notify, f"Creation failed: {e}", severity="error", timeout=10)

    @on(Button.Pressed, "#btn_start")
    async def on_start_btn(self):
        cid = self.get_selected_container_id()
        if cid and self.manager:
            try:
                self.manager.start_container(cid)
                self.notify(f"Started {cid}")
                self.action_refresh_list()
            except Exception as e:
                self.notify(f"Start failed: {e}", severity="error")

    @on(Button.Pressed, "#btn_stop")
    async def on_stop_btn(self):
        cid = self.get_selected_container_id()
        if cid and self.manager:
            try:
                self.manager.stop_container(cid)
                self.notify(f"Stopped {cid}")
                self.action_refresh_list()
            except Exception as e:
                self.notify(f"Stop failed: {e}", severity="error")

    @on(Button.Pressed, "#btn_delete")
    async def on_delete_btn(self):
        cid = self.get_selected_container_id()
        if cid and self.manager:
             try:
                self.manager.delete_container(cid)
                self.notify(f"Deleted {cid}")
                self.action_refresh_list()
             except Exception as e:
                self.notify(f"Delete failed: {e}", severity="error")

    @on(Button.Pressed, "#btn_refresh")
    def on_refresh_btn(self):
        self.action_refresh_list()

if __name__ == "__main__":
    app = VaultOSApp()
    app.run()
