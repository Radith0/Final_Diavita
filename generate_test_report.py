#!/usr/bin/env python3
"""Generate a styled HTML test report for the Diabetes Prediction App."""

import subprocess
import re
import json
import os
import sys
from datetime import datetime
from pathlib import Path

ROOT_DIR = Path(__file__).parent
REPORT_PATH = ROOT_DIR / "test_report.html"


def run_pytest():
    """Run backend pytest and parse results."""
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/", "-v", "--tb=no"],
        capture_output=True, text=True, cwd=ROOT_DIR / "backend"
    )
    output = result.stdout + result.stderr
    tests = []

    for line in output.splitlines():
        match = re.match(
            r"(tests/\S+\.py)::(\S+)::(\S+)\s+(PASSED|FAILED|ERROR|SKIPPED)",
            line.strip()
        )
        if match:
            file_path, class_name, test_name, status = match.groups()
            class_file = file_path.replace("tests/", "tests.").replace(".py", "").replace("/", ".") + "." + class_name
            tests.append({
                "status": status.lower(),
                "suite": "Backend",
                "class_file": class_file,
                "test_name": test_name,
                "time": 0.0,
            })

    # Re-run with durations to get per-test times
    result2 = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/", "-v", "--tb=no", "--durations=0"],
        capture_output=True, text=True, cwd=ROOT_DIR / "backend"
    )
    duration_output = result2.stdout + result2.stderr

    # Parse individual test durations from --durations output
    duration_map = {}
    for line in duration_output.splitlines():
        dur_match = re.match(r"\s*([\d.]+)s\s+(call|setup|teardown)\s+(\S+)", line.strip())
        if dur_match and dur_match.group(2) == "call":
            secs = float(dur_match.group(1))
            test_id = dur_match.group(3)
            parts = test_id.split("::")
            if len(parts) >= 3:
                test_fn = parts[-1]
                duration_map[test_fn] = secs

    for t in tests:
        if t["test_name"] in duration_map:
            t["time"] = duration_map[t["test_name"]]

    # Parse total time from summary line
    time_match = re.search(r"in\s+([\d.]+)s", duration_output)
    backend_time = float(time_match.group(1)) if time_match else sum(t["time"] for t in tests)

    return tests, backend_time


def run_vitest():
    """Run frontend vitest and parse results."""
    result = subprocess.run(
        ["npx", "vitest", "run", "--reporter=json"],
        capture_output=True, text=True, cwd=ROOT_DIR / "frontend"
    )

    # vitest JSON goes to stdout
    json_str = result.stdout
    # Find JSON object boundaries
    start = json_str.find("{")
    end = json_str.rfind("}") + 1
    if start == -1 or end == 0:
        return [], 0.0

    data = json.loads(json_str[start:end])
    tests = []
    total_time = 0.0

    for test_file in data.get("testResults", []):
        file_name = test_file.get("name", "")
        # Extract relative path
        rel = file_name.split("src/")[-1] if "src/" in file_name else os.path.basename(file_name)
        suite_time = test_file.get("endTime", 0) - test_file.get("startTime", 0)
        total_time += suite_time

        for assertion in test_file.get("assertionResults", []):
            ancestors = assertion.get("ancestorTitles", [])
            test_title = assertion.get("title", "")
            full_title = " > ".join(ancestors + [test_title]) if ancestors else test_title
            status_map = {"passed": "passed", "failed": "failed", "pending": "skipped"}
            status = status_map.get(assertion.get("status", ""), "failed")
            duration_ms = assertion.get("duration", 0) or 0

            tests.append({
                "status": status,
                "suite": "Frontend",
                "class_file": "src/test/" + rel.split("/")[-1],
                "test_name": full_title,
                "time": round(duration_ms / 1000, 3),
            })

    return tests, round(total_time / 1000, 2)


def generate_html(backend_tests, backend_time, frontend_tests, frontend_time):
    """Generate the styled HTML report."""
    all_tests = backend_tests + frontend_tests
    total = len(all_tests)
    passed = sum(1 for t in all_tests if t["status"] == "passed")
    failed = sum(1 for t in all_tests if t["status"] == "failed")
    errors = sum(1 for t in all_tests if t["status"] == "error")
    skipped = sum(1 for t in all_tests if t["status"] == "skipped")
    total_time = round(backend_time + frontend_time, 2)
    pass_rate = round((passed / total * 100), 1) if total > 0 else 0.0
    overall_status = "PASSED" if failed == 0 and errors == 0 else "FAILED"
    status_color = "#27ae60" if overall_status == "PASSED" else "#e74c3c"

    now = datetime.now()
    generated_date = now.strftime("%B %d, %Y at %I:%M %p")

    b_passed = sum(1 for t in backend_tests if t["status"] == "passed")
    b_failed = sum(1 for t in backend_tests if t["status"] == "failed")
    b_errors = sum(1 for t in backend_tests if t["status"] == "error")
    b_skipped = sum(1 for t in backend_tests if t["status"] == "skipped")
    f_passed = sum(1 for t in frontend_tests if t["status"] == "passed")
    f_failed = sum(1 for t in frontend_tests if t["status"] == "failed")
    f_errors = sum(1 for t in frontend_tests if t["status"] == "error")
    f_skipped = sum(1 for t in frontend_tests if t["status"] == "skipped")

    def progress_bar(p, f, e, s, tot):
        if tot == 0:
            return ""
        pw = p / tot * 100
        fw = f / tot * 100
        ew = e / tot * 100
        sw = s / tot * 100
        return f"""<div class="progress-bar">
            <div class="progress-passed" style="width:{pw:.1f}%"></div>
            <div class="progress-failed" style="width:{fw:.1f}%"></div>
            <div class="progress-error" style="width:{ew:.1f}%"></div>
            <div class="progress-skipped" style="width:{sw:.1f}%"></div>
        </div>"""

    test_rows = ""
    for t in all_tests:
        badge_class = "badge-passed" if t["status"] == "passed" else \
                      "badge-failed" if t["status"] == "failed" else \
                      "badge-error" if t["status"] == "error" else "badge-skipped"
        label = t["status"].upper()
        time_str = f'{t["time"]:.3f}s'
        test_rows += f"""<tr>
            <td><span class="badge {badge_class}">{label}</span></td>
            <td class="suite-cell"><strong>{t["suite"]}</strong></td>
            <td class="class-cell">{t["class_file"]}</td>
            <td class="name-cell">{t["test_name"]}</td>
            <td class="time-cell">{time_str}</td>
        </tr>\n"""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Diabetes Prediction App — Test Report</title>
<style>
  * {{
    margin: 0;
    padding: 0;
    box-sizing: border-box;
  }}
  body {{
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
    background: #f0f2f5;
    color: #2c3e50;
    line-height: 1.6;
    padding: 40px 20px;
  }}
  .container {{
    max-width: 1100px;
    margin: 0 auto;
    background: #fff;
    border-radius: 16px;
    box-shadow: 0 2px 20px rgba(0,0,0,0.06);
    padding: 40px 48px;
  }}

  /* Header */
  .header {{
    margin-bottom: 32px;
  }}
  .header h1 {{
    font-size: 24px;
    font-weight: 700;
    color: #1a1a2e;
    margin-bottom: 6px;
  }}
  .header h1 .icon {{
    margin-right: 8px;
  }}
  .header .meta {{
    display: flex;
    align-items: center;
    gap: 14px;
    color: #7f8c8d;
    font-size: 14px;
  }}
  .overall-badge {{
    display: inline-block;
    padding: 4px 18px;
    border-radius: 20px;
    color: #fff;
    font-weight: 700;
    font-size: 13px;
    letter-spacing: 0.5px;
    background: {status_color};
  }}

  /* Summary Cards */
  .summary-cards {{
    display: flex;
    gap: 14px;
    flex-wrap: wrap;
    margin-bottom: 14px;
  }}
  .card {{
    flex: 1;
    min-width: 120px;
    background: #f8f9fb;
    border-radius: 12px;
    padding: 20px 16px;
    text-align: center;
    border: 1px solid #eef0f4;
  }}
  .card .value {{
    font-size: 36px;
    font-weight: 800;
    line-height: 1.1;
    margin-bottom: 4px;
  }}
  .card .label {{
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1px;
    color: #95a5a6;
  }}
  .val-total {{ color: #2c3e50; }}
  .val-passed {{ color: #27ae60; }}
  .val-failed {{ color: #e74c3c; }}
  .val-errors {{ color: #e67e22; }}
  .val-skipped {{ color: #95a5a6; }}
  .val-rate {{ color: {("#27ae60" if pass_rate >= 80 else "#e67e22" if pass_rate >= 50 else "#e74c3c")}; }}

  .duration-card {{
    display: inline-block;
    background: #f8f9fb;
    border-radius: 12px;
    padding: 18px 28px;
    text-align: center;
    border: 1px solid #eef0f4;
    margin-bottom: 32px;
  }}
  .duration-card .value {{
    font-size: 30px;
    font-weight: 800;
    color: #2c3e50;
    line-height: 1.1;
    margin-bottom: 2px;
  }}
  .duration-card .label {{
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1px;
    color: #95a5a6;
  }}

  /* Suite Summary */
  .section-title {{
    font-size: 18px;
    font-weight: 700;
    color: #1a1a2e;
    margin-bottom: 16px;
    padding-bottom: 10px;
    border-bottom: 2px solid #f0f2f5;
  }}
  .suite-table {{
    width: 100%;
    border-collapse: collapse;
    margin-bottom: 36px;
  }}
  .suite-table th {{
    text-align: left;
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    color: #95a5a6;
    padding: 10px 14px;
    border-bottom: 2px solid #eef0f4;
  }}
  .suite-table td {{
    padding: 14px 14px;
    font-size: 14px;
    border-bottom: 1px solid #f4f5f7;
    vertical-align: middle;
  }}
  .suite-table tr:last-child td {{
    border-bottom: none;
  }}
  .suite-table .suite-name {{
    font-weight: 600;
    color: #2c3e50;
  }}
  .suite-table .num-passed {{ color: #27ae60; font-weight: 700; }}
  .suite-table .num-failed {{ color: #e74c3c; font-weight: 700; }}
  .suite-table .num-errors {{ color: #e67e22; font-weight: 700; }}
  .suite-table .num-skipped {{ color: #95a5a6; font-weight: 700; }}
  .suite-table .num-time {{ color: #7f8c8d; }}

  .progress-bar {{
    display: flex;
    width: 100%;
    min-width: 140px;
    height: 18px;
    border-radius: 10px;
    overflow: hidden;
    background: #eef0f4;
  }}
  .progress-passed {{ background: #27ae60; }}
  .progress-failed {{ background: #e74c3c; }}
  .progress-error {{ background: #e67e22; }}
  .progress-skipped {{ background: #95a5a6; }}

  /* All Test Results */
  .results-table {{
    width: 100%;
    border-collapse: collapse;
  }}
  .results-table th {{
    text-align: left;
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    color: #95a5a6;
    padding: 10px 12px;
    border-bottom: 2px solid #eef0f4;
  }}
  .results-table th:last-child {{
    text-align: right;
  }}
  .results-table td {{
    padding: 10px 12px;
    font-size: 13.5px;
    border-bottom: 1px solid #f4f5f7;
    vertical-align: middle;
  }}
  .results-table tr:hover {{
    background: #fafbfc;
  }}
  .suite-cell {{
    font-size: 13.5px;
    color: #2c3e50;
  }}
  .class-cell {{
    color: #7f8c8d;
    font-size: 13px;
  }}
  .name-cell {{
    color: #34495e;
    font-weight: 500;
  }}
  .time-cell {{
    text-align: right;
    color: #95a5a6;
    font-size: 13px;
    font-variant-numeric: tabular-nums;
    white-space: nowrap;
  }}

  /* Badges */
  .badge {{
    display: inline-block;
    padding: 3px 12px;
    border-radius: 6px;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.5px;
    text-transform: uppercase;
    min-width: 64px;
    text-align: center;
  }}
  .badge-passed {{
    background: #d4edda;
    color: #155724;
  }}
  .badge-failed {{
    background: #f8d7da;
    color: #721c24;
  }}
  .badge-error {{
    background: #fff3cd;
    color: #856404;
  }}
  .badge-skipped {{
    background: #e2e8f0;
    color: #4a5568;
  }}

  .results-header {{
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    margin-bottom: 16px;
    padding-bottom: 10px;
    border-bottom: 2px solid #f0f2f5;
  }}
  .results-header h2 {{
    font-size: 18px;
    font-weight: 700;
    color: #1a1a2e;
  }}
  .results-count {{
    font-size: 15px;
    color: #95a5a6;
    font-weight: 600;
  }}
</style>
</head>
<body>
<div class="container">
  <!-- Header -->
  <div class="header">
    <h1><span class="icon">🧪</span>Diabetes Prediction App &mdash; Test Report</h1>
    <div class="meta">
      Generated on {generated_date}
      &nbsp;&nbsp;|&nbsp;&nbsp;
      <span class="overall-badge">{overall_status}</span>
    </div>
  </div>

  <!-- Summary Cards -->
  <div class="summary-cards">
    <div class="card">
      <div class="value val-total">{total}</div>
      <div class="label">Total Tests</div>
    </div>
    <div class="card">
      <div class="value val-passed">{passed}</div>
      <div class="label">Passed</div>
    </div>
    <div class="card">
      <div class="value val-failed">{failed}</div>
      <div class="label">Failed</div>
    </div>
    <div class="card">
      <div class="value val-errors">{errors}</div>
      <div class="label">Errors</div>
    </div>
    <div class="card">
      <div class="value val-skipped">{skipped}</div>
      <div class="label">Skipped</div>
    </div>
    <div class="card">
      <div class="value val-rate">{pass_rate}%</div>
      <div class="label">Pass Rate</div>
    </div>
  </div>

  <div class="duration-card">
    <div class="value">{total_time}s</div>
    <div class="label">Duration</div>
  </div>

  <!-- Suite Summary -->
  <div class="section-title">Suite Summary</div>
  <table class="suite-table">
    <thead>
      <tr>
        <th>Suite</th>
        <th>Passed</th>
        <th>Failed</th>
        <th>Errors</th>
        <th>Skipped</th>
        <th>Time</th>
        <th>Progress</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td class="suite-name">Backend (pytest)</td>
        <td class="num-passed">{b_passed}</td>
        <td class="num-failed">{b_failed}</td>
        <td class="num-errors">{b_errors}</td>
        <td class="num-skipped">{b_skipped}</td>
        <td class="num-time">{backend_time}s</td>
        <td>{progress_bar(b_passed, b_failed, b_errors, b_skipped, len(backend_tests))}</td>
      </tr>
      <tr>
        <td class="suite-name">Frontend (vitest)</td>
        <td class="num-passed">{f_passed}</td>
        <td class="num-failed">{f_failed}</td>
        <td class="num-errors">{f_errors}</td>
        <td class="num-skipped">{f_skipped}</td>
        <td class="num-time">{frontend_time}s</td>
        <td>{progress_bar(f_passed, f_failed, f_errors, f_skipped, len(frontend_tests))}</td>
      </tr>
    </tbody>
  </table>

  <!-- All Test Results -->
  <div class="results-header">
    <h2>All Test Results ({total})</h2>
  </div>
  <table class="results-table">
    <thead>
      <tr>
        <th>Status</th>
        <th>Suite</th>
        <th>Class / File</th>
        <th>Test Name</th>
        <th style="text-align:right">Time</th>
      </tr>
    </thead>
    <tbody>
      {test_rows}
    </tbody>
  </table>
</div>
</body>
</html>"""
    return html


def main():
    print("🧪 Running Backend tests (pytest)...")
    backend_tests, backend_time = run_pytest()
    print(f"   ✅ {len(backend_tests)} tests collected in {backend_time}s")

    print("🧪 Running Frontend tests (vitest)...")
    frontend_tests, frontend_time = run_vitest()
    print(f"   ✅ {len(frontend_tests)} tests collected in {frontend_time}s")

    print("📝 Generating HTML report...")
    html = generate_html(backend_tests, backend_time, frontend_tests, frontend_time)
    REPORT_PATH.write_text(html)

    total = len(backend_tests) + len(frontend_tests)
    passed = sum(1 for t in backend_tests + frontend_tests if t["status"] == "passed")
    failed = total - passed
    print(f"\n{'='*50}")
    print(f"  Total: {total}  |  Passed: {passed}  |  Failed: {failed}")
    print(f"  Report saved to: {REPORT_PATH}")
    print(f"{'='*50}")


if __name__ == "__main__":
    main()
