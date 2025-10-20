import configparser

# Parse Common.cfg and PeerInfo.cfg configuration files

def parse_common_config(filename="Common.cfg"):
    settings = {}
    try:
        with open(filename, 'r') as f:
            for line in f:
                if not line.strip():
                    continue
                key, value = line.strip().split()
                settings[key] = value if not value.isdigit() else int(value)
        return settings
    except FileNotFoundError:
        print(f"Error: {filename} not found.")
        return None
    except Exception as e:
        print(f"Error parsing {filename}: {e}")
        return None

def parse_peer_info(filename="PeerInfo.cfg"):
    peers = []
    try:
        with open(filename, 'r') as f:
            for line in f:
                if not line.strip():
                    continue
                
                parts = line.split()
                if len(parts) != 4:
                    print(f"Warning: Skipping malformed line: {line}")
                    continue
                
                peer_info = {
                    'peer_id': parts[0],
                    'host_name': parts[1],
                    'port': int(parts[2]),
                    'has_file': int(parts[3])
                }
                peers.append(peer_info)
        
        return peers
        
    except FileNotFoundError:
        print(f"Error: {filename} not found.")
        return None
    except Exception as e:
        print(f"Error parsing {filename}: {e}")
        return None