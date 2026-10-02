"""Back-of-the-envelope capacity model used by every design in this repository.

The goal is not precision. The goal is to make assumptions explicit and repeatable so
that a reviewer can challenge an input (for example "5 uploads per user per day is too
high") and immediately see the effect on QPS, storage and bandwidth.
"""

from __future__ import annotations

from dataclasses import dataclass, field

SECONDS_PER_DAY = 86_400
DAYS_PER_YEAR = 365

_BYTE_UNITS = ["B", "KB", "MB", "GB", "TB", "PB", "EB"]


@dataclass(frozen=True)
class Workload:
    """Inputs for a capacity estimate.

    All sizes are in bytes. ``reads_per_user_per_day`` counts logical read operations
    (for example "open a chat", "load a feed page"), not database queries.
    """

    name: str
    daily_active_users: int
    writes_per_user_per_day: float
    reads_per_user_per_day: float
    avg_write_size_bytes: int
    avg_read_size_bytes: int
    retention_days: int
    replication_factor: int = 3
    peak_to_average: float = 3.0
    notes: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if self.daily_active_users <= 0:
            raise ValueError("daily_active_users must be positive")
        if self.writes_per_user_per_day < 0 or self.reads_per_user_per_day < 0:
            raise ValueError("per-user rates cannot be negative")
        if self.avg_write_size_bytes < 0 or self.avg_read_size_bytes < 0:
            raise ValueError("sizes cannot be negative")
        if self.retention_days <= 0:
            raise ValueError("retention_days must be positive")
        if self.replication_factor < 1:
            raise ValueError("replication_factor must be >= 1")
        if self.peak_to_average < 1:
            raise ValueError("peak_to_average must be >= 1")


@dataclass(frozen=True)
class Estimate:
    workload: Workload
    write_qps_avg: float
    write_qps_peak: float
    read_qps_avg: float
    read_qps_peak: float
    read_write_ratio: float
    new_storage_per_day_bytes: float
    total_storage_bytes: float
    ingress_bytes_per_sec_avg: float
    egress_bytes_per_sec_avg: float
    egress_bytes_per_sec_peak: float


def estimate(w: Workload) -> Estimate:
    writes_per_day = w.daily_active_users * w.writes_per_user_per_day
    reads_per_day = w.daily_active_users * w.reads_per_user_per_day

    write_qps = writes_per_day / SECONDS_PER_DAY
    read_qps = reads_per_day / SECONDS_PER_DAY

    new_storage_per_day = writes_per_day * w.avg_write_size_bytes
    total_storage = new_storage_per_day * w.retention_days * w.replication_factor

    ingress = write_qps * w.avg_write_size_bytes
    egress = read_qps * w.avg_read_size_bytes

    ratio = (reads_per_day / writes_per_day) if writes_per_day else float("inf")

    return Estimate(
        workload=w,
        write_qps_avg=write_qps,
        write_qps_peak=write_qps * w.peak_to_average,
        read_qps_avg=read_qps,
        read_qps_peak=read_qps * w.peak_to_average,
        read_write_ratio=ratio,
        new_storage_per_day_bytes=new_storage_per_day,
        total_storage_bytes=total_storage,
        ingress_bytes_per_sec_avg=ingress,
        egress_bytes_per_sec_avg=egress,
        egress_bytes_per_sec_peak=egress * w.peak_to_average,
    )


def human_bytes(n: float) -> str:
    """Decimal (SI) units, which is what capacity discussions normally use."""
    if n < 0:
        raise ValueError("negative size")
    value = float(n)
    for unit in _BYTE_UNITS:
        if value < 1000 or unit == _BYTE_UNITS[-1]:
            return f"{value:.1f} {unit}" if unit != "B" else f"{value:.0f} B"
        value /= 1000
    raise AssertionError("unreachable")


def human_rate(qps: float) -> str:
    if qps >= 1_000_000:
        return f"{qps / 1_000_000:.1f}M/s"
    if qps >= 1_000:
        return f"{qps / 1_000:.1f}K/s"
    return f"{qps:.0f}/s"


def bits_per_sec(bytes_per_sec: float) -> str:
    bits = bytes_per_sec * 8
    for unit, div in (("Tbps", 1e12), ("Gbps", 1e9), ("Mbps", 1e6), ("Kbps", 1e3)):
        if bits >= div:
            return f"{bits / div:.1f} {unit}"
    return f"{bits:.0f} bps"


def to_markdown(e: Estimate) -> str:
    w = e.workload
    if e.read_write_ratio == float("inf"):
        ratio = "n/a"
    elif e.read_write_ratio >= 1:
        ratio = f"{e.read_write_ratio:.0f}:1"
    else:
        ratio = f"1:{1 / e.read_write_ratio:.0f}"
    rows = [
        ("Daily active users", f"{w.daily_active_users:,}"),
        ("Write QPS (avg / peak)", f"{human_rate(e.write_qps_avg)} / {human_rate(e.write_qps_peak)}"),
        ("Read QPS (avg / peak)", f"{human_rate(e.read_qps_avg)} / {human_rate(e.read_qps_peak)}"),
        ("Read:write ratio", ratio),
        ("New data per day", human_bytes(e.new_storage_per_day_bytes)),
        (
            f"Stored data ({w.retention_days} days, RF={w.replication_factor})",
            human_bytes(e.total_storage_bytes),
        ),
        ("Ingress (avg)", bits_per_sec(e.ingress_bytes_per_sec_avg)),
        (
            "Egress (avg / peak)",
            f"{bits_per_sec(e.egress_bytes_per_sec_avg)} / {bits_per_sec(e.egress_bytes_per_sec_peak)}",
        ),
    ]
    out = ["| Metric | Estimate |", "|---|---|"]
    out += [f"| {k} | {v} |" for k, v in rows]
    return "\n".join(out)
