import logging
import sys

logger = logging.getLogger('peerProcess')

def setup_logging(peer_id):
    logger.propagate = False
    
    # set the logging level
    logger.setLevel(logging.INFO)
    
    # writes logs to file 'log_peer_[peerID].log' 
    log_file = f'log_peer_{peer_id}.log'
    file_handler = logging.FileHandler(log_file, mode='w')
    
    formatter = logging.Formatter('%(asctime)s: %(message)s',datefmt='%Y-%m-%d %H:%M:%S')
    file_handler.setFormatter(formatter)
    
    if not logger.hasHandlers(): 
        logger.addHandler(file_handler)
    
    logger.info(f"--- Logger for Peer {peer_id} initialized. ---")
