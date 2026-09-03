from experiments.experiment_001_selective_activation import fixture_tasks, run_baseline, run_selective, summarize


def test_baseline_and_selective_cover_same_tasks():
    tasks = fixture_tasks()
    baseline = [run_baseline(t) for t in tasks]
    selective = [run_selective(t) for t in tasks]
    assert {r.task_id for r in baseline} == {r.task_id for r in selective}


def test_selector_uses_only_available_mechanisms():
    for task in fixture_tasks():
        result = run_selective(task)
        assert set(result.active_mechanisms) <= task.available_mechanisms


def test_protocol_records_control_overhead_separately():
    task = fixture_tasks()[0]
    result = run_selective(task)
    assert result.control_overhead_units == 1
    assert result.control_overhead_units not in result.active_mechanisms


def test_summary_exposes_reduction_and_errors_without_hiding_them():
    tasks = fixture_tasks()
    runs = [r for task in tasks for r in (run_baseline(task), run_selective(task))]
    report = summarize(runs)
    assert len(report["tasks"]) == len(tasks)
    assert all(row["outcome_delta"] <= 0.0 for row in report["tasks"])
    assert all(row["activation_reduction"] >= 0 for row in report["tasks"])
    assert any(row["correction_delta"] > 0 for row in report["tasks"]) or all(
        row["correction_delta"] == 0 for row in report["tasks"]
    )
