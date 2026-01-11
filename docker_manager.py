import docker
from docker.errors import DockerException, NotFound

IMAGE_NAME = "lscr.io/linuxserver/webtop:latest"

class DockerManager:
    def __init__(self):
        try:
            self.client = docker.from_env()
        except DockerException as e:
            raise RuntimeError(f"Could not connect to Docker Daemon: {e}")

    def list_containers(self):
        """Returns a list of vaultOS containers."""
        try:
            # Filter strictly for containers managed by this app
            all_containers = self.client.containers.list(all=True)
            vault_containers = []
            for container in all_containers:
                # User rule: "using vaultos label or vaultos from container name filter"
                is_vault = False
                
                # Check Label
                if container.labels.get('app') == 'vaultOS':
                    is_vault = True
                
                # Check Name Prefix
                elif container.name.startswith("vaultos-"):
                    is_vault = True
                    
                if is_vault:
                    vault_containers.append(container)
            return vault_containers
        except Exception as e:
            print(f"Error listing containers: {e}")
            return []

    def create_container(self, config: dict, progress_callback=None) -> str:
        """
        Creates a container based on the config dictionary.
        progress_callback: function(str) -> None, called with status updates during pull.
        """
        try:
            user_name = config.get('name')
            
            # Generate 5-digit hex
            import uuid
            hex_id = uuid.uuid4().hex[:5]
            
            # New Name: vaultos-<5digithex>-<name>
            name = f"vaultos-{hex_id}-{user_name}"
            
            port = int(config.get('port'))
            mode = config.get('type', 'default')
            
            # 1. Determine Image Tag
            image_tag = "latest"
            if mode == 'default':
                image_tag = "latest"
            else:
                os_name = config.get('os', 'alpine')
                desktop = config.get('desktop', 'xfce')
                
                # Architecture Detection
                arch = self._get_architecture()
                
                # Construct tag: e.g. amd64-alpine-i3, arm64v8-arch-kde
                if os_name == 'alpine' and desktop == 'xfce':
                     image_tag = "latest"
                else:
                     image_tag = f"{arch}-{os_name}-{desktop}"
            
            base_image = f"lscr.io/linuxserver/webtop:{image_tag}"

            # 2. Handle Custom Build (Persistent Advanced)
            final_image = base_image
            if mode == 'persistent' and config.get('advanced'):
                username = config.get('username')
                if username:
                    # Build custom image with new user
                    final_image = self.build_custom_image(base_image, username)

            # 3. Pull image if needed
            try:
                self.client.images.get(final_image)
            except NotFound:
                if progress_callback:
                    progress_callback(f"Image {final_image} not found. Starting download...")
                    self._pull_with_progress(final_image, progress_callback)
                else:
                    print(f"Pulling {final_image}...")
                    self.client.images.pull(final_image)

            # 4. Prepare Run Args
            environment = {
                'PUID': '1000',
                'PGID': '1000', 
                'TZ': 'Etc/UTC'
            }
            
            labels = {'app': 'vaultOS'}
            if mode == 'ephemeral':
                if config.get('timer'):
                    import time
                    expiry = self._parse_timer(config.get('timer'))
                    labels['vaultos.expires'] = str(expiry)

            volumes = {}
            if mode == 'persistent':
                vconf = config.get('volume')
                if vconf:
                    volumes[vconf] = {'bind': '/config', 'mode': 'rw'}
                
                # Advanced home mapping
                if config.get('advanced') and config.get('homedir'):
                     username = config.get('username', 'abc') 
                     volumes[config.get('homedir')] = {'bind': f'/home/{username}', 'mode': 'rw'}

            
            container = self.client.containers.run(
                final_image,
                name=name,
                ports={'3000/tcp': port}, # Only map 3000, ignore 3001 (ssl) for now
                labels=labels,
                environment=environment,
                detach=True,
                shm_size="1gb",
                mem_limit="1g",       # Limit RAM to 1GB
                nano_cpus=2000000000, # Limit CPU to 2 Cores
                restart_policy={"Name": "unless-stopped"} if mode != 'ephemeral' else None,
                volumes=volumes
            )
            return container.id

        except Exception as e:
            raise RuntimeError(f"Failed to create container: {e}")

    def _get_architecture(self):
        import platform
        machine = platform.machine().lower()
        # x86-64 -> amd64
        if machine in ['x86_64', 'amd64']:
            return 'amd64'
        # arm64 -> arm64v8 (user requested m64v8 but standard is arm64v8, assuming typo)
        elif machine in ['aarch64', 'arm64']:
            return 'arm64v8'
        else:
            return 'amd64' # Fallback default

    def build_custom_image(self, base_image, username) -> str:
        """
        Builds a custom layer on top of base_image to add a user.
        Returns the new image tag.
        """
        import io
        
        # Check if Alpine (latest or explicit alpine tag)
        is_alpine = "dis-alpine" in base_image # Tag logic we used is os-desktop, so 'alpine' in string?
        # base_image is "lscr.io/linuxserver/webtop:tag"
        # our tag logic: "alpine-xfce", "arch-kde", etc. "latest" is alpine.
        if ":latest" in base_image or "alpine" in base_image:
             # Alpine Logic:
             # - Install sudo, shadow (for chpasswd), bash
             # - adduser -D
             dockerfile = f"""
             FROM {base_image}
             ENV USER={username}
             ENV HOME=/home/{username}
             RUN apk add --no-cache sudo shadow bash && \\
                 usermod -l {username} abc && \\
                 (groupmod -n {username} abc || true) && \\
                 if [ -d "/home/abc" ]; then mv /home/abc /home/{username}; else mkdir -p /home/{username}; fi && \\
                 usermod -d /home/{username} {username} && \\
                 ln -s /home/{username} /home/abc && \\
                 chown -R {username}:{username} /home/{username} && \\
                 chown -R {username}:{username} /config || true && \\
                 (find /etc/cont-init.d /etc/services.d /etc/s6-overlay -type f -exec sed -i 's/abc/{username}/g' {{}} + || true) && \\
                 echo '{username}:{username}' | chpasswd && \\
                 echo '{username} ALL=(ALL) NOPASSWD: ALL' > /etc/sudoers.d/{username} && \\
                 chmod 0440 /etc/sudoers.d/{username}
             """
        else:
             # Standard Linux (Debian/Ubuntu/Fedora/Arch/EL)
             dockerfile = f"""
             FROM {base_image}
             ENV USER={username}
             ENV HOME=/home/{username}
             RUN usermod -l {username} abc && \\
                 (groupmod -n {username} abc || true) && \\
                 if [ -d "/home/abc" ]; then mv /home/abc /home/{username}; else mkdir -p /home/{username}; fi && \\
                 usermod -d /home/{username} {username} && \\
                 ln -s /home/{username} /home/abc && \\
                 chown -R {username}:{username} /home/{username} && \\
                 chown -R {username}:{username} /config || true && \\
                 (find /etc/cont-init.d /etc/services.d /etc/s6-overlay -type f -exec sed -i 's/abc/{username}/g' {{}} + || true) && \\
                 echo '{username}:{username}' | chpasswd && \\
                 echo '{username} ALL=(ALL) NOPASSWD: ALL' > /etc/sudoers.d/{username} && \\
                 chmod 0440 /etc/sudoers.d/{username}
             """
        
        tag_name = f"vaultos-custom-{username}"
        f = io.BytesIO(dockerfile.encode('utf-8'))
        
        logs = []
        try:
             # self.client.images.build returns (image, logs)
             image, logs = self.client.images.build(fileobj=f, tag=tag_name, rm=True)
             return tag_name
        except Exception as e:
             # Print logs for debugging if build fails
             if logs:
                 print("Build Logs:", [l.get('stream', '') for l in logs])
             raise RuntimeError(f"Build failed: {e}")

    def _parse_timer(self, timer_str):
        """Returns unix timestamp for expiry."""
        import time
        import re
        
        now = time.time()
        if not timer_str:
            return now # expires immediately?
            
        # Parse 30s, 1h, 1d
        m = re.match(r"(\d+)([shd])", timer_str)
        if not m:
            return now
            
        val = int(m.group(1))
        unit = m.group(2)
        
        seconds = 0
        if unit == 's': seconds = val
        elif unit == 'h': seconds = val * 3600
        elif unit == 'd': seconds = val * 86400
        
        return now + seconds

    def get_and_prune_containers(self):
        """Checks for expired containers, removes them, and returns the list of active vaultOS containers."""
        import time
        try:
            # We fetch all containers once
            # Optimize: Maybe filters={'label': ['app=vaultOS']}?
            # But we also filter by name prefix for legacy/robustness.
            # Let's stick to python filter for now, but fetching 'all' is expensive.
            # Improvement: Use docker filters if possible.
            # self.client.containers.list(all=True, filters={"label": "app=vaultOS"}) 
            # + another call for names?
            # For now, let's keep Python logic but do it in one pass.
            
            all_containers = self.list_containers()
            active_containers = []
            now = time.time()
            
            for c in all_containers:
                expiry = c.labels.get('vaultos.expires')
                if expiry:
                    if now > float(expiry):
                        print(f"Container {c.name} expired. Removing.")
                        try:
                            c.remove(force=True)
                        except: 
                            pass # Already gone?
                        continue # Don't add to active list
                
                active_containers.append(c)
                
            return active_containers
        except Exception as e:
            print(f"Error checking expired: {e}")
            return []

    def start_container(self, container_id: str):
        try:
            container = self.client.containers.get(container_id)
            container.start()
        except Exception as e:
            raise RuntimeError(f"Failed to start container: {e}")

    def stop_container(self, container_id: str):
        try:
            container = self.client.containers.get(container_id)
            container.stop()
        except Exception as e:
            raise RuntimeError(f"Failed to stop container: {e}")

    def delete_container(self, container_id: str):
        try:
            container = self.client.containers.get(container_id)
            container.remove(force=True) # Force remove to handle running containers if needed, or just remove stopped
        except Exception as e:
            raise RuntimeError(f"Failed to delete container: {e}")

    def _pull_with_progress(self, image_name, callback):
        import json
        try:
             # Parse repo/tag
             if ":" in image_name:
                 repo, tag = image_name.split(":")
             else:
                 repo, tag = image_name, "latest"
                 
             stream = self.client.api.pull(repo, tag=tag, stream=True, decode=True)
             for chunk in stream:
                 # Chunk is a dict like {'status': 'Downloading', 'progressDetail': {'current': 123, 'total': 456}, 'id': '...'}
                 # We simply want to show the current Status + potentially 'id'
                 status = chunk.get('status', '')
                 cid = chunk.get('id', '')
                 progress = chunk.get('progress', '')
                 
                 msg = f"{status}"
                 if cid:
                     msg += f" [{cid}]"
                 if progress:
                     msg += f" {progress}"
                     
                 callback(msg)
        except Exception as e:
            callback(f"Download failed: {e}")
            raise e

    def get_system_info(self):
        """Returns tuple: (engine_version, kv_stats_dict)"""
        try:
            ver = self.client.version()
            engine_ver = ver.get('Version', 'Unknown')
            # client pkg version is hard to get from SDK directly, usually just docker sdk version or API version
            api_ver = ver.get('ApiVersion', 'Unknown')
            
            # Recalculate stats based on ALL containers, not just vaultOS? 
            # User asked for "total(running/stop)". 
            # Assuming this means global docker stats or just vaultOS?
            # "Docker connected... status total" implies global or app-specific. 
            # Let's return counts for vaultOS containers specifically as that looks cleaner for this app.
            
            containers = self.list_containers()
            total = len(containers)
            running = sum(1 for c in containers if c.status == 'running')
            stopped = sum(1 for c in containers if c.status != 'running')
            
            return {
                'engine_version': engine_ver,
                'api_version': api_ver,
                'total': total,
                'running': running,
                'stopped': stopped,
                'connected': True
            }
        except Exception:
            return {
                'engine_version': 'N/A',
                'api_version': 'N/A',
                'total': 0,
                'running': 0,
                'stopped': 0,
                'connected': False
            }

if __name__ == "__main__":
    # fast verification
    try:
        dm = DockerManager()
        print("Docker connected successfully.")
        print("Existing VaultOS Containers:", dm.list_containers())
    except Exception as e:
        print(f"Init failed: {e}")
