"""Workload assumptions for each reference design.

These are *illustrative* assumptions chosen to make the design trade-offs visible.
They are not measurements of any real product.
"""

from __future__ import annotations

from .model import Workload

KB = 1_000
MB = 1_000_000
GB = 1_000_000_000

SCENARIOS: dict[str, Workload] = {
    "video-sharing": Workload(
        name="Video sharing platform (uploads)",
        daily_active_users=50_000_000,
        writes_per_user_per_day=0.01,  # 1 in 100 DAU uploads a video per day
        reads_per_user_per_day=10,  # video views
        avg_write_size_bytes=300 * MB,  # source + all transcoded renditions
        avg_read_size_bytes=50 * MB,  # partial watch of an adaptive stream
        retention_days=5 * 365,
        replication_factor=3,
        notes=("egress is served mostly by the CDN, not origin",),
    ),
    "messaging": Workload(
        name="Real-time messaging",
        daily_active_users=100_000_000,
        writes_per_user_per_day=40,  # messages sent
        reads_per_user_per_day=40,  # each message is read roughly once per recipient
        avg_write_size_bytes=200,  # text payload + envelope, media stored separately
        avg_read_size_bytes=200,
        retention_days=30,  # server keeps undelivered/recent messages only
        replication_factor=3,
    ),
    "professional-network": Workload(
        name="Professional network (feed + posts)",
        daily_active_users=30_000_000,
        writes_per_user_per_day=0.5,  # posts, comments, reactions
        reads_per_user_per_day=20,  # feed page loads
        avg_write_size_bytes=2 * KB,
        avg_read_size_bytes=30 * KB,  # one feed page of hydrated items, no media
        retention_days=10 * 365,
    ),
    "photo-sharing": Workload(
        name="Photo sharing social app",
        daily_active_users=200_000_000,
        writes_per_user_per_day=0.1,
        reads_per_user_per_day=50,
        avg_write_size_bytes=2 * MB,  # original + 3 resized variants
        avg_read_size_bytes=200 * KB,
        retention_days=10 * 365,
    ),
    "job-portal": Workload(
        name="Job portal",
        daily_active_users=5_000_000,
        writes_per_user_per_day=0.3,  # applications, saved searches, profile edits
        reads_per_user_per_day=15,  # searches and job detail views
        avg_write_size_bytes=5 * KB,  # resume binaries live in object storage
        avg_read_size_bytes=20 * KB,
        retention_days=7 * 365,
    ),
    "notification": Workload(
        name="Notification system",
        daily_active_users=50_000_000,
        writes_per_user_per_day=10,  # notifications generated per user
        reads_per_user_per_day=5,  # inbox opens
        avg_write_size_bytes=1 * KB,
        avg_read_size_bytes=5 * KB,
        retention_days=90,
        peak_to_average=5.0,  # campaign bursts
    ),
    "url-shortener": Workload(
        name="URL shortener",
        daily_active_users=10_000_000,
        writes_per_user_per_day=0.1,
        reads_per_user_per_day=10,  # redirects
        avg_write_size_bytes=500,
        avg_read_size_bytes=500,
        retention_days=5 * 365,
    ),
    "file-storage": Workload(
        name="File storage and sync",
        daily_active_users=20_000_000,
        writes_per_user_per_day=2,
        reads_per_user_per_day=5,
        avg_write_size_bytes=1 * MB,
        avg_read_size_bytes=1 * MB,
        retention_days=5 * 365,
        replication_factor=1,  # durability via erasure coding, accounted separately
        notes=("erasure coding overhead ~1.5x applied in the design doc",),
    ),
    "monitoring": Workload(
        name="Real-time monitoring (telemetry)",
        daily_active_users=1_000_000,  # monitored devices/hosts, not humans
        writes_per_user_per_day=8_640,  # one sample every 10 s
        reads_per_user_per_day=50,
        avg_write_size_bytes=200,
        avg_read_size_bytes=20 * KB,
        retention_days=30,  # raw; downsampled rollups kept longer
        replication_factor=2,
        peak_to_average=1.5,  # telemetry is steady, not diurnal
    ),
    "e-commerce": Workload(
        name="E-commerce",
        daily_active_users=20_000_000,
        writes_per_user_per_day=0.2,  # orders, carts, reviews
        reads_per_user_per_day=30,
        avg_write_size_bytes=5 * KB,
        avg_read_size_bytes=50 * KB,
        retention_days=7 * 365,
        peak_to_average=10.0,  # flash sales
    ),
    "multi-tenant-saas": Workload(
        name="Multi-tenant enterprise SaaS",
        daily_active_users=500_000,
        writes_per_user_per_day=50,
        reads_per_user_per_day=300,
        avg_write_size_bytes=2 * KB,
        avg_read_size_bytes=10 * KB,
        retention_days=7 * 365,
        peak_to_average=4.0,  # business-hours concentration
    ),
    "enterprise-ai": Workload(
        name="Enterprise AI platform (assistant queries)",
        daily_active_users=100_000,
        writes_per_user_per_day=20,  # prompts; each produces a stored trace
        reads_per_user_per_day=20,
        avg_write_size_bytes=20 * KB,  # prompt + retrieved context + response + trace
        avg_read_size_bytes=4 * KB,
        retention_days=365,
        peak_to_average=4.0,
    ),
}
