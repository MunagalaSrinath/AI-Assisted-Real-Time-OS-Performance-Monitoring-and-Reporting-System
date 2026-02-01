from system_monitor import get_system_snapshot, compare_snapshots

previous_snapshot = None

def get_live_changes():
    global previous_snapshot

    try:
        current_snapshot = get_system_snapshot()

        # First request → just store snapshot
        if previous_snapshot is None:
            previous_snapshot = current_snapshot
            return {
                "status": "initialized",
                "message": "Initial snapshot captured. Refresh to see live changes."
            }

        # Compare snapshots
        changes = compare_snapshots(previous_snapshot, current_snapshot)

        # Update previous snapshot
        previous_snapshot = current_snapshot

        return changes

    except Exception as e:
        # NEVER crash the server
        return {
            "status": "error",
            "message": str(e)
        }
