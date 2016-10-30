from autodiscovery import client

# ---------------- CONSTANTS ------------------
MAINTENANCE_PORT_RECV = 50000
SERVER_MAINT_PORT = 40000
MAGIC = "suaZ01713" # to make sure we don't confuse or get confused by other programs


# ---------------- CLIENT PROGRAM ----------------
if __name__ == '__main__':
    host_info = client.start_self_discovery()

    # TODO: start file watchdog
    # TODO: Start taking video!