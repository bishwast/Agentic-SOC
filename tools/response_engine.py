import subprocess
import logging

logger = logging.getLogger("AgenticSOC.Response")

class ResponseEngine:
    def __init__(self):
        # --- THE CRITICAL INFRASTRUCTURE WHITELIST ---
        # These IPs will NEVER be blocked, regardless of AI confidence.
        self.whitelist = [
            "127.0.0.1",     # Local loopback (Required for host DNS/Routing)
            "127.0.0.53",    # systemd-resolved (Ubuntu DNS)
            "172.17.0.1",    # Docker default bridge gateway
            "0.0.0.0"        # Catch-all
        ]
        # Threshold
        self.AUTO_BLOCK_THRESHOLD = 90
    
    def execute_response(self, ip, confidence, decision_text):
        """
        Determines and executes the appropriate security action based on confidence.
        """
        # 1. THE GOVERNANCE CHECK (Run this FIRST)
        if ip in self.whitelist:
            logger.warning(f"🛡️ GOVERNANCE OVERRIDE: AI attempted to block critical infrastructure ({ip}). Action aborted.")
            return "ABORTED_WHITELIST"

        # 2. NORMAL EXECUTION (Only runs if IP is not whitelisted)
        if "BLOCK" in decision_text.upper() and confidence >= self.AUTO_BLOCK_THRESHOLD:
            return self._block_ip(ip)
        elif confidence >= 70:
            logger.info(f"PENDING: Confidence {confidence}% for {ip}. Requires Human-in-the-Loop.")
            return "PENDING_APPROVAL"
        else:
            logger.info(f"MONITOR: Confidence {confidence}% for {ip} is too low for action.")
            return "MONITOR_ONLY"
        
    def _block_ip(self, ip):
        """
        The actual firewall command. 
        Note: This requires the script to run with sudo privileges.
        """
        try:
            logger.warning(f"ACTUATING: Blocking IP {ip} via iptables.")
            
            # Using iptables for universal compatibility on Linux/DGX
            # -I INPUT 1: Insert at the top of the input chain
            # -s: Source IP
            # -j DROP: Discard packets
            cmd = f"sudo iptables -I INPUT 1 -s {ip} -j DROP"
            
            # Using subprocess.run for deterministic execution tracking
            result = subprocess.run(cmd.split(), capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info(f"SUCCESS: {ip} has been blocked.")
                return "BLOCKED"
            else:
                logger.error(f"FAILURE: Could not block {ip}. Error: {result.stderr}")
                return "ERROR_COMMAND_FAILED"
                
        except Exception as e:
            logger.error(f"CRITICAL: Firewall actuation failed: {str(e)}")
            return "ERROR_EXCEPTION"
        
    def unblock_ip(self, ip):
        """
        Removes ALL instances of a block rule for a specific IP.
        """
        try:
            logger.info(f"REVOKING: Purging all block rules for IP {ip}.")
            removed_at_least_one = False
            
            # Keep deleting until iptables returns an error (meaning no more rules exist)
            while True:
                cmd = f"sudo iptables -D INPUT -s {ip} -j DROP"
                result = subprocess.run(cmd.split(), capture_output=True, text=True)
                
                if result.returncode == 0:
                    removed_at_least_one = True
                else:
                    break # No more matching rules found
            
            if removed_at_least_one:
                logger.info(f"CLEANUP SUCCESS: {ip} has been fully purged from the firewall.")
                return True
            else:
                logger.warning(f"CLEANUP: No active rules found for {ip}.")
                return False
                
        except Exception as e:
            logger.error(f"CRITICAL: Revocation failure: {str(e)}")
            return False