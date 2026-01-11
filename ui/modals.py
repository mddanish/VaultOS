from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Button, Label, Input, RadioSet, RadioButton, Select, Checkbox
from textual.screen import ModalScreen
from textual import on
from config import OS_OPTIONS, OS_DESKTOP_MAP, get_desktop_label

class AboutModal(ModalScreen):
    """Modal to show about information."""
    CSS = """
    AboutModal {
        align: center middle;
    }
    #about_dialog {
        width: 50;
        height: auto;
        border: heavy $accent;
        background: $surface;
        padding: 1 2;
    }
    #about_title {
        text-style: bold;
        width: 100%;
        text-align: center;
        margin-bottom: 1;
        background: $primary;
        color: $text;
        padding: 1;
    }
    .about-item {
        width: 100%;
        text-align: center;
        margin-bottom: 1;
    }
    #close_btn {
        width: 100%;
        margin-top: 1;
    }
    """
    def compose(self) -> ComposeResult:
        with Vertical(id="about_dialog"):
            yield Label("VaultOS v1.0.0", id="about_title")
            yield Label("Desktop Container Manager", classes="about-item")
            yield Label("", classes="about-item") # Spacer
            yield Label("Developer: Mohammed Danish Amber", classes="about-item")
            yield Label("Email: md.danish.amber@live.com", classes="about-item")
            yield Label("Repo: github.com/mddanish/vaultos", classes="about-item")
            yield Button("Close", id="close_btn")
    
    @on(Button.Pressed, "#close_btn")
    def on_close(self):
        self.dismiss()

class DownloadProgressModal(ModalScreen):
    """Modal to show download progress."""
    CSS = """
    DownloadProgressModal {
        align: center middle;
    }
    #download_dialog {
        width: 60;
        height: auto;
        border: heavy $accent;
        background: $surface;
        padding: 1 2;
    }
    #dl_title {
        text-style: bold;
        width: 100%;
        text-align: center;
        margin-bottom: 1;
    }
    #dl_status {
        width: 100%;
        text-align: center;
    }
    """
    def compose(self) -> ComposeResult:
        with Vertical(id="download_dialog"):
            yield Label("Downloading Image...", id="dl_title")
            yield Label("Connecting to Docker Hub...", id="dl_status")
    
    def update_status(self, msg: str):
         self.query_one("#dl_status", Label).update(msg)

class CreateContainerModal(ModalScreen):
    """Modal dialog to create a new container with a Wizard flow."""
    CSS = """
    CreateContainerModal {
        align: center middle;
    }
    #dialog {
        width: 70%;
        max-width: 80;
        height: auto;
        max-height: 90%;
        border: heavy $accent;
        background: $surface;
        padding: 0 1; 
    }
    #wizard_title {
        text-style: bold;
        background: $primary-darken-2;
        color: $text;
        width: 100%;
        text-align: center;
        padding: 1;
        margin-bottom: 1;
    }
    .step-container {
        height: 1fr;
        width: 100%;
        padding: 0 1;
        overflow-y: auto; /* Allow scrolling within the step if needed */
    }
    .hidden {
        display: none;
    }
    Label {
        margin-top: 1;
        color: $text-muted;
    }
    Input {
        margin-bottom: 0;
        border: tall $primary; 
        height: 3;
    }
    Select {
        margin-bottom: 1;
    }
    RadioSet {
        margin-bottom: 1;
        border: none;
    }
    #buttons {
        margin-top: 2;
        margin-bottom: 1;
        align: center middle;
        height: auto;
        dock: bottom; /* Ensure it stays at bottom if content grows */
        width: 100%;
    }
    #buttons Button {
        margin: 0 1; 
        height: 1;
        border: none;
        padding: 0;
        width: 14;
        content-align: center middle;
    }
    """

    def compose(self) -> ComposeResult:
        with Vertical(id="dialog"):
            yield Label("Create Container - Step 1/3", id="wizard_title")
            
            # --- STEP 1: BASICS ---
            with Vertical(id="step_1", classes="step-container"):
                yield Label("Container Name")
                yield Input(placeholder="my-vault", id="name")
                
                yield Label("Port (Local)")
                yield Input(placeholder="3001", id="port", type="integer")
                
                yield Label("Mode")
                with RadioSet(id="mode_select"):
                    yield RadioButton("Default", id="mode-default", value=True)
                    yield RadioButton("Persistent", id="mode-persistent")
                    yield RadioButton("Ephemeral", id="mode-ephemeral")

            # --- STEP 2: DETAILS ---
            with Vertical(id="step_2", classes="step-container hidden"):
                yield Label("OS Distribution:")
                yield Select(OS_OPTIONS, prompt="Select OS", id="os_select")
                
                yield Label("Desktop Environment:")
                yield Select([], prompt="Select OS First", id="desktop_select", disabled=True)
                
                # Ephemeral Fields
                with Vertical(id="ephemeral_fields", classes="hidden"):
                    yield Label("Timer (e.g. 30s, 1h):")
                    yield Input(placeholder="30s", id="timer")

                # Persistent Fields
                with Vertical(id="persistent_fields", classes="hidden"):
                    yield Label("Volume Path (Host):")
                    import sys
                    vol_ph = "C:/data/config" if sys.platform == "win32" else "/data/config"
                    yield Input(placeholder=vol_ph, id="volume_path")
                    yield Checkbox("Enable Advanced Options", id="chk_advanced")

            # --- STEP 3: ADVANCED ---
            with Vertical(id="step_3", classes="step-container hidden"):
                yield Label("Advanced Configuration")
                yield Label("Username:")
                yield Input(placeholder="customUser", id="adv_user")
                yield Label("Home Directory Map (Host):")
                home_ph = "C:/data/home" if sys.platform == "win32" else "/data/home"
                yield Input(placeholder=home_ph, id="adv_home")

            # --- BUTTONS ---
            with Horizontal(id="buttons"):
                yield Button("Cancel", variant="error", id="btn_wiz_cancel")
                yield Button("Back", variant="default", id="btn_wiz_back", disabled=True)
                yield Button("Next", variant="primary", id="btn_wiz_next", disabled=True)
                yield Button("Create", variant="success", id="btn_wiz_create", disabled=True)

    def on_mount(self):
        self.current_step = 1
        self.mode = "default"
        # Trigger validation/UI update
        self.refresh_ui()

    @on(Select.Changed, "#os_select")
    def on_os_change(self, event: Select.Changed):
        os_val = event.value
        desktop_select = self.query_one("#desktop_select", Select)
        
        if os_val == Select.BLANK or not os_val:
            desktop_select.set_options([])
            desktop_select.disabled = True
            desktop_select.prompt = "Select OS First"
        else:
            # Populate based on map
            options_keys = OS_DESKTOP_MAP.get(os_val, [])
            # Format options
            options = [(get_desktop_label(k), k) for k in options_keys]
            
            desktop_select.set_options(options)
            desktop_select.disabled = False
            desktop_select.prompt = "Select Desktop"
            
            # Reset value to blank to force user selection
            if options:
                 desktop_select.value = Select.BLANK

    @on(RadioSet.Changed, "#mode_select")
    def on_mode_change(self, event):
        sid = event.pressed.id 
        if "default" in sid: self.mode = "default"
        elif "persistent" in sid: self.mode = "persistent"
        elif "ephemeral" in sid: self.mode = "ephemeral"
        self.refresh_ui()

    @on(Button.Pressed, "#btn_wiz_cancel")
    def on_cancel(self):
        self.dismiss()

    @on(Button.Pressed, "#btn_wiz_back")
    def on_back(self):
        if self.current_step > 1:
            self.current_step -= 1
            self.refresh_ui()

    @on(Button.Pressed, "#btn_wiz_next")
    def on_next(self):
        # Validate before moving next
        if not self.validate_current_step():
            return
            
        if self.current_step < 3:
            self.current_step += 1
            self.refresh_ui()

    @on(Button.Pressed, "#btn_wiz_create")
    def on_create_btn(self):
        # Validate current step before finishing
        if not self.validate_current_step():
            return
        self.finish_creation()

    def validate_current_step(self) -> bool:
        if self.current_step == 1:
            name = self.query_one("#name", Input).value
            port = self.query_one("#port", Input).value
            if not name or not port:
                self.notify("Name and Port are required!", severity="error")
                return False
        
        elif self.current_step == 2:
            os_val = self.query_one("#os_select", Select).value
            desk = self.query_one("#desktop_select", Select).value
            if os_val == Select.BLANK or desk == Select.BLANK:
                 self.notify("OS and Desktop are required!", severity="error")
                 return False
            
            if self.mode == "ephemeral":
                timer = self.query_one("#timer", Input).value
                if not timer:
                     self.notify("Timer is required!", severity="error")
                     return False
            
            if self.mode == "persistent":
                vol = self.query_one("#volume_path", Input).value
                if not vol:
                     self.notify("Volume Path is required!", severity="error")
                     return False

        elif self.current_step == 3:
            user = self.query_one("#adv_user", Input).value
            home = self.query_one("#adv_home", Input).value
            if not user or not home:
                 self.notify("Username and Home Path are required!", severity="error")
                 return False
                 
        return True

    @on(Checkbox.Changed, "#chk_advanced")
    def on_advanced_toggle(self, event: Checkbox.Changed):
        # Just refresh UI to update buttons
        self.refresh_ui()

    def refresh_ui(self):
        # Update Steps Visibility
        for i in range(1, 4):
            step = self.query_one(f"#step_{i}")
            if i == self.current_step:
                step.remove_class("hidden")
            else:
                step.add_class("hidden")
        
        # Update Title
        self.query_one("#wizard_title", Label).update(f"Create Container - Step {self.current_step}/3")
        
        # Button Logic
        btn_back = self.query_one("#btn_wiz_back")
        btn_next = self.query_one("#btn_wiz_next")
        btn_create = self.query_one("#btn_wiz_create")
        
        # Back Button
        btn_back.disabled = (self.current_step == 1)
        btn_back.remove_class("hidden")

        # Next / Create Logic
        if self.current_step == 1:
            if self.mode == "default":
                btn_next.disabled = True
                btn_create.disabled = False
            else: # Ephemeral or Persistent
                btn_next.disabled = False
                btn_create.disabled = True
        
        elif self.current_step == 2:
            if self.mode == "ephemeral":
                btn_next.disabled = True
                btn_create.disabled = False
            elif self.mode == "persistent":
                # Check Advanced Checkbox
                try:
                    is_adv = self.query_one("#chk_advanced", Checkbox).value
                    if is_adv:
                        btn_next.disabled = False
                        btn_create.disabled = True
                    else:
                        btn_next.disabled = True
                        btn_create.disabled = False
                except:
                    # Safegaurd if widget not ready
                    pass
        
        elif self.current_step == 3:
            btn_next.disabled = True
            btn_create.disabled = False

        # Update Step 2 dynamic visibility for fields
        if self.current_step == 2:
            eph = self.query_one("#ephemeral_fields")
            pers = self.query_one("#persistent_fields")
            if self.mode == "ephemeral":
                eph.remove_class("hidden")
                pers.add_class("hidden")
            elif self.mode == "persistent":
                eph.add_class("hidden")
                pers.remove_class("hidden")

    def finish_creation(self):
        # Gather all data
        config = {
            "name": self.query_one("#name", Input).value,
            "port": self.query_one("#port", Input).value,
            "type": self.mode
        }
        
        if self.mode != "default":
            config["os"] = self.query_one("#os_select", Select).value
            config["desktop"] = self.query_one("#desktop_select", Select).value
        
        if self.mode == "ephemeral":
            config["timer"] = self.query_one("#timer", Input).value
            
        if self.mode == "persistent":
            config["volume"] = self.query_one("#volume_path", Input).value
            is_adv = self.query_one("#chk_advanced", Checkbox).value
            config["advanced"] = is_adv
            if is_adv:
                config["username"] = self.query_one("#adv_user", Input).value
                config["homedir"] = self.query_one("#adv_home", Input).value
        
        self.dismiss(config)
