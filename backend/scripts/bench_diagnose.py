from __future__ import annotations

import statistics
import time

import httpx

QUERIES = [
    "E04 motor overload on CX-200",
    "thermal relay tripping on conveyor",
    "compressor pressure drop",
    "gearbox oil leak",
    "pump seal failure on VP-40",
    "vibration alarm after restart",
    "bearing noise at high speed",
    "E08 drive fault",
    "replace OL-E04-R overload relay",
    "belt slippage conveyor",
    "hydraulic pressure low",
    "coupling misalignment symptoms",
    "L11 low oil level alarm",
    "compressor AX-75 shutdown",
    "motor tripped on overload",
    "P24 high discharge pressure",
    "V07 pump vibration warning",
    "thermal overload relay replacement procedure",
    "incident log for CX-200 in last month",
    "maintenance checklist for conveyor drive",
]


def main() -> None:
    base_url = "http://127.0.0.1:8000/api"
    latencies_ms: list[float] = []
    hits = 0

    with httpx.Client(timeout=15.0) as client:
        for q in QUERIES[:3]:  # warmup
            client.post(f"{base_url}/diagnose", data={"query": q})

        for q in QUERIES:
            start = time.perf_counter()
            response = client.post(f"{base_url}/diagnose", data={"query": q})
            elapsed_ms = (time.perf_counter() - start) * 1000
            response.raise_for_status()
            payload = response.json()
            latencies_ms.append(elapsed_ms)
            if payload.get("recommended_steps"):
                hits += 1

    latencies_ms.sort()
    p50 = statistics.median(latencies_ms)
    p95 = latencies_ms[int(0.95 * (len(latencies_ms) - 1))]
    mean = statistics.mean(latencies_ms)

    print(f"queries: {len(latencies_ms)}")
    print(f"hits with evidence: {hits}/{len(latencies_ms)}")
    print(f"p50: {p50:.0f} ms")
    print(f"p95: {p95:.0f} ms")
    print(f"mean: {mean:.0f} ms")
    print(f"min: {min(latencies_ms):.0f} ms")
    print(f"max: {max(latencies_ms):.0f} ms")


if __name__ == "__main__":
    main()
