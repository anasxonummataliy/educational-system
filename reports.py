import csv
from pathlib import Path
from typing import Tuple


def _ensure_reports_dir(base: Path = None) -> Path:
    base = Path(base or Path.cwd()) / "data" / "reports"
    base.mkdir(parents=True, exist_ok=True)
    return base


def generate_student_report(student, base: Path | None = None) -> Tuple[Path, Path]:
  
    base_dir = _ensure_reports_dir(base)
    safe_name = student.username.replace(" ", "_")
    txt_path = base_dir / f"{safe_name}_report.txt"
    csv_path = base_dir / f"{safe_name}_report.csv"

    # TXT
    lines = [
        f"Talaba hisobot: {student.username}",
        f"O'rtacha: {student.average:.2f}",
        f"Baholar: {', '.join(str(g) for g in student.grades) or 'yo\'q'}",
        f"Davomat yozuvlari: {len(student.attendance)}",
        f"Akademik xavf: {'HA' if student.at_risk() else 'YO\'Q'}",
    ]
    txt_path.write_text("\n".join(lines), encoding="utf-8")

    # CSV - simple key,value rows
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["maydon", "qiymat"])
        writer.writerow(["foydalanuvchi", student.username])
        writer.writerow(["ortacha", f"{student.average:.2f}"])
        writer.writerow(["baholar", ";".join(str(g) for g in student.grades)])
        writer.writerow(["davomat_soni", str(len(student.attendance))])
        writer.writerow(["xavf", str(student.at_risk())])

    return txt_path, csv_path


def generate_all_reports(storage, base: Path | None = None):
    base_dir = _ensure_reports_dir(base)
    users = storage.list_users()
    paths = []
    for u in users.values():
        if getattr(u, "role", lambda: "")() == "student":
            p = generate_student_report(u, base=base_dir)
            paths.append(p)
    return paths
