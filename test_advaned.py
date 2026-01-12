from docker_manager import DockerManager
import time

def test_advanced():
    dm = DockerManager()
    
    print("--- Test 1: Ephemeral Container (5s timer) ---")
    conf_ephemeral = {
        'name': 'test-ephemeral',
        'port': 4000,
        'type': 'ephemeral',
        'os': 'alpine',
        'desktop': 'xfce',
        'timer': '5s'
    }
    
    try:
        cid = dm.create_container(conf_ephemeral)
        print(f"Created ephemeral: {cid}")
        print("Waiting 3s...")
        time.sleep(3)
        dm.check_prune_expired()
        if any(c.id == cid for c in dm.list_containers()):
            print("OK: Still exists.")
        else:
            print("FAIL: Values removed too early.")
            
        print("Waiting 3s (Total 6s)...")
        time.sleep(3)
        dm.check_prune_expired()
        if any(c.id == cid for c in dm.list_containers()):
            print("FAIL: Should have expired and been removed.")
        else:
            print("PASS: Ephemeral container removed.")
            
    except Exception as e:
        print(f"Ephemeral Test Error: {e}")

    print("\n--- Test 2: Persistent Advanced (Custom User) ---")
    conf_persistent = {
        'name': 'test-persistent',
        'port': 4002,
        'type': 'persistent',
        'os': 'alpine',
        'desktop': 'xfce',
        'volume': 'c:/tmp/vaultconfig',
        'advanced': True,
        'username': 'testuser',
        'homedir': 'c:/tmp/vaulthome'
    }
    
    try:
        # Cleanup mock paths if needed? Docker handles vol creation.
        # This will trigger build.
        print("Building and creating... (this takes time)")
        cid = dm.create_container(conf_persistent)
        print(f"Created persistent: {cid}")
        
        # Verify user exists? 
        cont = dm.client.containers.get(cid)
        print(f"Status: {cont.status}")
        
        print("Cleaning up persistent...")
        dm.delete_container(cid)
        print("PASS: Persistent created and deleted.")
        
    except Exception as e:
        print(f"Persistent Test Error: {e}")

if __name__ == "__main__":
    test_advanced()
