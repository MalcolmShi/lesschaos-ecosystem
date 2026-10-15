"""本程序拥有核验结果到基础 Markdown 周报的呈现，不新增业务结论或修改输入。"""

import json
import pathlib
import sys


def cell(value):
    return str(value).replace("\\", "\\\\").replace("|", "\\|").replace("\n", " ").replace("\r", " ")


def render(data):
    if data.get("status") not in ("checked", "partial") or not isinstance(data.get("metrics"), list) or not isinstance(data.get("findings"), list):
        raise ValueError("expected checked-data JSON with status, metrics and findings")
    metrics, findings = data["metrics"], data["findings"]
    conclusion = "部分数据待核对" if data["status"] == "partial" or findings else "所列指标已完成结构与数值核验"
    lines = ["# 部门周报", "", "## 结论", "", f"{conclusion}；可用指标 {len(metrics)} 项，待核对 {len(findings)} 项。业务口径与事实依据仍以原始材料为准。", "", "## 指标", "", "| 部门 | 周期 | 指标 | 计划 | 实际 | 差额 | 单位 | 证据 |", "| --- | --- | --- | --- | --- | --- | --- | --- |"]
    for metric in metrics:
        lines.append("| " + " | ".join(cell(metric[key]) for key in ("department", "week", "metric", "planned", "actual", "delta", "unit", "evidence")) + " |")
    lines.extend(["", "## 待核对", ""])
    lines.extend(f"- {cell(item['reason'])}（{cell(item['evidence'])}）" for item in findings)
    if not findings:
        lines.append("本次结构与数值检查未发现待核对项。")
    lines.extend(["", "## 来源", "", cell(data["source"]), ""])
    return "\n".join(lines)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("usage: render_report.py <checked-data.json> <output.md>")
    source, output = map(pathlib.Path, sys.argv[1:])
    if source.resolve() == output.resolve():
        raise SystemExit("input and output must differ")
    report = render(json.loads(source.read_text(encoding="utf-8")))
    output.write_text(report, encoding="utf-8")
    print(f"report written: {output}")
