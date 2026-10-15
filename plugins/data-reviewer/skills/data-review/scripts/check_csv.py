"""本程序拥有标准周报 CSV 的结构、数值核验及行级证据输出，不判断业务真实性。"""

import csv
import json
import pathlib
import sys
from collections import Counter
from decimal import Decimal, InvalidOperation


def check(source):
    with source.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        required = {"department", "week", "metric", "planned", "actual", "unit"}
        if not required.issubset(reader.fieldnames or []):
            raise ValueError("required columns: " + ", ".join(sorted(required)))
        if len(reader.fieldnames) != len(set(reader.fieldnames)):
            raise ValueError("duplicate column names")
        rows, lines = [], []
        for row in reader:
            rows.append(row)
            lines.append(reader.line_num)
        keys = [tuple((row.get(field) or "").strip() for field in ("department", "week", "metric", "unit")) for row in rows]
    counts = Counter(keys)
    metrics, findings = [], []
    for row, key, line in zip(rows, keys, lines):
        evidence = f"{source}:{line}"
        if not all(key):
            findings.append({"evidence": evidence, "reason": "missing department, week, metric or unit"})
            continue
        if counts[key] > 1:
            findings.append({"evidence": evidence, "reason": "duplicate department/week/metric/unit; resolve source rows"})
            continue
        try:
            planned, actual = (Decimal((row.get(field) or "").strip()) for field in ("planned", "actual"))
            if not planned.is_finite() or not actual.is_finite():
                raise InvalidOperation
        except InvalidOperation:
            findings.append({"evidence": evidence, "reason": "planned or actual is not a finite number"})
            continue
        metrics.append(dict(zip(("department", "week", "metric", "unit"), key), planned=str(planned), actual=str(actual), delta=str(actual - planned), evidence=evidence))
    if not rows:
        findings.append({"evidence": str(source), "reason": "no data rows"})
    return {"status": "partial" if findings else "checked", "source": str(source), "rows": len(rows), "metrics": metrics, "findings": findings}


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("usage: check_csv.py <input.csv> <output.json>")
    source, output = map(pathlib.Path, sys.argv[1:])
    if source.resolve() == output.resolve():
        raise SystemExit("input and output must differ")
    result = check(source)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{result['status']}: {len(result['metrics'])} checked metrics, {len(result['findings'])} findings; {output}")
