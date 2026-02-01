import psutil
import time

def get_top_processes(limit=5):
    processes = []

    for p in psutil.process_iter(['name', 'cpu_percent', 'memory_percent']):
        try:
            processes.append({
                "name": p.info['name'],
                "cpu_percent": p.info['cpu_percent'] or 0,
                "memory_percent": round(p.info['memory_percent'] or 0, 2)
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    processes.sort(key=lambda x: x["cpu_percent"], reverse=True)
    return processes[:limit]


def get_system_snapshot():
    """Take a snapshot of current OS metrics"""
    return {
        "timestamp": time.time(),
        "cpu_percent": psutil.cpu_percent(interval=1),
        "memory_percent": psutil.virtual_memory().percent,
        "disk_percent": psutil.disk_usage('/').percent,
        "top_processes": get_top_processes()
    }


def clean_processes(processes):
    """Remove idle/system noise from process list"""
    cleaned = []
    for p in processes:
        if p["name"] and "idle" not in p["name"].lower():
            cleaned.append({
                "name": p["name"],
                "cpu_percent": round(p["cpu_percent"], 1),
                "memory_percent": p["memory_percent"]
            })
    return cleaned


def compare_snapshots(old, new):
    """Compare two system snapshots"""
    return {
        "cpu_before": old["cpu_percent"],
        "cpu_now": new["cpu_percent"],
        "cpu_change": round(new["cpu_percent"] - old["cpu_percent"], 2),

        "memory_before": old["memory_percent"],
        "memory_now": new["memory_percent"],
        "memory_change": round(new["memory_percent"] - old["memory_percent"], 2),

        "disk_before": old["disk_percent"],
        "disk_now": new["disk_percent"],
        "disk_change": round(new["disk_percent"] - old["disk_percent"], 2),

        "top_processes": clean_processes(new["top_processes"])
    }
