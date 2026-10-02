import math

import pytest
from capacity import SCENARIOS, Workload, bits_per_sec, estimate, human_bytes, human_rate, to_markdown
from capacity.__main__ import main


def make(**overrides):
    base = dict(
        name="t",
        daily_active_users=86_400,
        writes_per_user_per_day=1,
        reads_per_user_per_day=10,
        avg_write_size_bytes=1_000,
        avg_read_size_bytes=2_000,
        retention_days=10,
        replication_factor=3,
        peak_to_average=2.0,
    )
    base.update(overrides)
    return Workload(**base)


def test_qps_is_daily_volume_over_seconds_per_day():
    e = estimate(make())
    assert e.write_qps_avg == pytest.approx(1.0)
    assert e.read_qps_avg == pytest.approx(10.0)
    assert e.write_qps_peak == pytest.approx(2.0)
    assert e.read_qps_peak == pytest.approx(20.0)
    assert e.read_write_ratio == pytest.approx(10.0)


def test_storage_includes_retention_and_replication():
    e = estimate(make())
    assert e.new_storage_per_day_bytes == pytest.approx(86_400 * 1_000)
    assert e.total_storage_bytes == pytest.approx(86_400 * 1_000 * 10 * 3)


def test_write_heavy_ratio_is_expressed_as_one_to_n():
    assert "| Read:write ratio | 1:4 |" in to_markdown(estimate(make(reads_per_user_per_day=0.25)))


def test_bandwidth():
    e = estimate(make())
    assert e.ingress_bytes_per_sec_avg == pytest.approx(1_000)
    assert e.egress_bytes_per_sec_avg == pytest.approx(20_000)
    assert e.egress_bytes_per_sec_peak == pytest.approx(40_000)


def test_read_only_workload_has_infinite_ratio():
    e = estimate(make(writes_per_user_per_day=0))
    assert math.isinf(e.read_write_ratio)
    assert "n/a" in to_markdown(e)


@pytest.mark.parametrize(
    "field,value",
    [
        ("daily_active_users", 0),
        ("writes_per_user_per_day", -1),
        ("avg_write_size_bytes", -5),
        ("retention_days", 0),
        ("replication_factor", 0),
        ("peak_to_average", 0.5),
    ],
)
def test_invalid_inputs_are_rejected(field, value):
    with pytest.raises(ValueError):
        make(**{field: value})


@pytest.mark.parametrize(
    "n,expected",
    [(0, "0 B"), (999, "999 B"), (1_000, "1.0 KB"), (1_500_000, "1.5 MB"), (2.5e15, "2.5 PB")],
)
def test_human_bytes(n, expected):
    assert human_bytes(n) == expected


def test_human_rate_and_bits():
    assert human_rate(12) == "12/s"
    assert human_rate(12_500) == "12.5K/s"
    assert human_rate(3_200_000) == "3.2M/s"
    assert bits_per_sec(125_000_000) == "1.0 Gbps"
    assert bits_per_sec(10) == "80 bps"


def test_every_scenario_produces_a_table():
    assert len(SCENARIOS) == 12
    for w in SCENARIOS.values():
        table = to_markdown(estimate(w))
        assert table.startswith("| Metric | Estimate |")
        assert "Write QPS" in table


def test_cli_lists_and_rejects_unknown(capsys):
    assert main(["--list"]) == 0
    assert "url-shortener" in capsys.readouterr().out
    assert main(["does-not-exist"]) == 2


def test_cli_prints_selected_scenario(capsys):
    assert main(["url-shortener"]) == 0
    out = capsys.readouterr().out
    assert "### URL shortener" in out
    assert "| Read QPS (avg / peak) |" in out
