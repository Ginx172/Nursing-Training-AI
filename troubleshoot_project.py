#!/usr/bin/env python3
"""
=============================================================
  Nursing Training AI - Troubleshooting & Diagnostic Script
  Generated: 2026-03-27
  Purpose: Verificare completa a tuturor componentelor
=============================================================
"""

import os
import sys
import json
import subprocess
import importlib
import re
from pathlib import Path
from datetime import datetime

# ---- CONFIGURARE ----
PROJECT_ROOT = Path(__file__).parent.resolve()
BACKEND_DIR = PROJECT_ROOT / "Nursing_Training_AI_App" / "backend"
FRONTEND_DIR = PROJECT_ROOT / "Nursing_Training_AI_App" / "frontend"
APP_DIR = PROJECT_ROOT / "Nursing_Training_AI_App"
VENV_DIR = PROJECT_ROOT / ".venv"

RESULTS = {
    "timestamp": datetime.now().isoformat(),
    "checks": [],
    "critical": 0,
    "high": 0,
    "medium": 0,
    "low": 0,
    "passed": 0,
}


def log_result(category, name, status, severity="info", details=""):
    """Inregistreaza rezultatul unei verificari"""
    icon = {"PASS": "[OK]", "FAIL": "[FAIL]", "WARN": "[WARN]", "INFO": "[INFO]"}
    color_codes = {
        "PASS": "\033[92m",
        "FAIL": "\033[91m",
        "WARN": "\033[93m",
        "INFO": "\033[94m",
    }
    reset = "\033[0m"
    c = color_codes.get(status, "")

    print(f"  {c}{icon.get(status, '[?]')}{reset} [{category}] {name}")
    if details:
        for line in details.split("\n"):
            print(f"        {line}")

    RESULTS["checks"].append({
        "category": category,
        "name": name,
        "status": status,
        "severity": severity,
        "details": details,
    })

    if status == "PASS":
        RESULTS["passed"] += 1
    elif severity == "critical":
        RESULTS["critical"] += 1
    elif severity == "high":
        RESULTS["high"] += 1
    elif severity == "medium":
        RESULTS["medium"] += 1
    elif severity == "low":
        RESULTS["low"] += 1


def section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


# ============================================================
# 1. VERIFICARI ENVIRONMENT
# ============================================================
def check_environment():
    section("1. ENVIRONMENT CHECK")

    # Python version
    py_ver = sys.version_info
    if py_ver >= (3, 10):
        log_result("ENV", f"Python {py_ver.major}.{py_ver.minor}.{py_ver.micro}", "PASS")
    else:
        log_result("ENV", f"Python {py_ver.major}.{py_ver.minor} - recomandat 3.10+", "WARN", "medium")

    # Node.js
    try:
        node_ver = subprocess.run(["node", "-v"], capture_output=True, text=True, timeout=10)
        if node_ver.returncode == 0:
            log_result("ENV", f"Node.js {node_ver.stdout.strip()}", "PASS")
        else:
            log_result("ENV", "Node.js nu este instalat", "FAIL", "high")
    except FileNotFoundError:
        log_result("ENV", "Node.js nu este instalat", "FAIL", "high")

    # Git
    try:
        git_ver = subprocess.run(["git", "--version"], capture_output=True, text=True, timeout=10)
        if git_ver.returncode == 0:
            log_result("ENV", f"Git {git_ver.stdout.strip()}", "PASS")
    except FileNotFoundError:
        log_result("ENV", "Git nu este instalat", "FAIL", "high")

    # Virtual environment
    if VENV_DIR.exists():
        log_result("ENV", f"Virtual environment gasit: {VENV_DIR}", "PASS")
    else:
        log_result("ENV", "Virtual environment (.venv) lipseste", "FAIL", "high",
                   "Ruleaza: python -m venv .venv && .venv\\Scripts\\activate && pip install -r Nursing_Training_AI_App/backend/requirements.txt")


# ============================================================
# 2. VERIFICARI DEPENDENTE PYTHON
# ============================================================
def check_python_dependencies():
    section("2. PYTHON DEPENDENCIES")

    req_file = BACKEND_DIR / "requirements.txt"
    if not req_file.exists():
        log_result("DEPS", "requirements.txt lipseste!", "FAIL", "critical")
        return

    critical_deps = {
        "fastapi": "fastapi",
        "uvicorn": "uvicorn",
        "sqlalchemy": "sqlalchemy",
        "pydantic": "pydantic",
        "openai": "openai",
        "google-generativeai": "google.generativeai",
        "redis": "redis",
        "stripe": "stripe",
        "PyJWT": "jwt",
        "cryptography": "cryptography",
        "passlib": "passlib",
        "httpx": "httpx",
        "sentry-sdk": "sentry_sdk",
        "psutil": "psutil",
        "numpy": "numpy",
        "alembic": "alembic",
    }

    installed = 0
    missing = 0
    for pkg_name, import_name in critical_deps.items():
        try:
            importlib.import_module(import_name)
            log_result("DEPS", f"{pkg_name}", "PASS")
            installed += 1
        except ImportError:
            log_result("DEPS", f"{pkg_name} - NU este instalat", "FAIL", "high",
                       f"pip install {pkg_name}")
            missing += 1
        except Exception as e:
            log_result("DEPS", f"{pkg_name} - eroare la import: {type(e).__name__}", "FAIL", "high",
                       f"{e}")
            missing += 1

    if missing > 0:
        log_result("DEPS", f"SUMAR: {installed} instalate, {missing} lipsesc", "WARN", "high",
                   f"Ruleaza: pip install -r {req_file}")


# ============================================================
# 3. VERIFICARI SECURITATE
# ============================================================
def check_security():
    section("3. SECURITY CHECKS")

    # --- .env files cu credentiale ---
    env_files = list(PROJECT_ROOT.rglob("*.env")) + list(PROJECT_ROOT.rglob(".env"))
    # Filtram duplicatele si fisierele din .venv/venv
    env_files = [f for f in set(env_files)
                 if ".venv" not in str(f) and "venv" not in str(f) and "env" not in f.parts
                 and "node_modules" not in str(f) and "__pycache__" not in str(f)
                 and "site-packages" not in str(f)]

    for env_file in env_files:
        if "example" in env_file.name.lower():
            log_result("SEC", f".env example: {env_file.relative_to(PROJECT_ROOT)}", "PASS")
            continue

        try:
            content = env_file.read_text(encoding="utf-8", errors="ignore")
            secrets_found = []
            patterns = [
                (r"(?:OPENAI|ANTHROPIC|GEMINI|GOOGLE|META|MISTRAL|GROK|SERP)_API_KEY\s*=\s*\S+", "API Key"),
                (r"(?:SECRET_KEY|ENCRYPTION_MASTER_KEY)\s*=\s*\S+", "Secret Key"),
                (r"DATABASE_URL\s*=\s*postgresql://\S+:\S+@", "DB Password in URL"),
                (r"(?:PASSWORD|PASSWD)\s*=\s*\S+", "Plaintext Password"),
                (r"(?:OANDA|IG)_\w+\s*=\s*\S+", "Trading/Broker Credentials"),
                (r"sk-(?:proj|ant|live)-\S+", "Live API Key Pattern"),
            ]
            for pattern, label in patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    secrets_found.append(label)

            if secrets_found:
                log_result("SEC", f"CREDENTIALE EXPUSE in {env_file.relative_to(PROJECT_ROOT)}", "FAIL", "critical",
                           f"Tipuri gasite: {', '.join(set(secrets_found))}\n"
                           f"ACTIUNE: Roteste TOATE cheile expuse IMEDIAT!")
            else:
                log_result("SEC", f".env fara secrete detectate: {env_file.relative_to(PROJECT_ROOT)}", "INFO")
        except Exception as e:
            log_result("SEC", f"Nu pot citi {env_file}: {e}", "WARN", "low")

    # --- .gitignore verification ---
    gitignore = PROJECT_ROOT / ".gitignore"
    if gitignore.exists():
        content = gitignore.read_text()
        if ".env" in content:
            log_result("SEC", ".gitignore contine regula pentru .env", "PASS")
        else:
            log_result("SEC", ".gitignore NU exclude .env!", "FAIL", "critical")
    else:
        log_result("SEC", ".gitignore lipseste!", "FAIL", "critical")

    # --- Verificare git history pentru secrete ---
    try:
        result = subprocess.run(
            ["git", "log", "--all", "--diff-filter=A", "--name-only", "--format="],
            capture_output=True, text=True, cwd=str(PROJECT_ROOT), timeout=30
        )
        committed_envs = [f for f in result.stdout.split("\n") if ".env" in f and "example" not in f.lower()]
        if committed_envs:
            log_result("SEC", "Fisiere .env gasite in git history!", "FAIL", "critical",
                       f"Fisiere: {', '.join(committed_envs[:5])}\n"
                       "ACTIUNE: Foloseste BFG Repo-Cleaner pentru a sterge din history")
        else:
            log_result("SEC", "Niciun .env gasit in git history", "PASS")
    except Exception:
        log_result("SEC", "Nu pot verifica git history", "WARN", "low")

    # --- CORS check ---
    main_py = BACKEND_DIR / "main.py"
    if main_py.exists():
        content = main_py.read_text(encoding="utf-8", errors="ignore")
        if 'allow_origins=["*"]' in content or "allow_origins=['*']" in content:
            log_result("SEC", "CORS wildcard (*) - permite orice origin", "FAIL", "high",
                       "Restrictionoaza allow_origins la domeniile tale specifice")
        else:
            log_result("SEC", "CORS configurat cu origini specifice", "PASS")

    # --- Hardcoded secrets in K8s ---
    k8s_dir = APP_DIR / "k8s"
    if k8s_dir.exists():
        for f in k8s_dir.rglob("*.yaml"):
            content = f.read_text(encoding="utf-8", errors="ignore")
            if re.search(r"(?:password|secret|key):\s*\S+", content, re.IGNORECASE):
                if "kind: Secret" in content and "base64" not in content.lower():
                    log_result("SEC", f"Secrete hardcoded in {f.relative_to(PROJECT_ROOT)}", "FAIL", "critical")

    # --- Admin endpoints without auth ---
    admin_py = BACKEND_DIR / "api" / "admin.py"
    if admin_py.exists():
        content = admin_py.read_text(encoding="utf-8", errors="ignore")
        todo_auth = content.count("TODO: Add admin auth")
        if todo_auth > 0:
            log_result("SEC", f"Admin endpoints fara autentificare ({todo_auth} TODO-uri)", "FAIL", "critical",
                       "Adauga Depends(get_current_admin_user) pe TOATE endpoint-urile admin")
        else:
            log_result("SEC", "Admin endpoints au autentificare", "PASS")

    # --- Debug/docs exposed ---
    if main_py.exists():
        content = main_py.read_text(encoding="utf-8", errors="ignore")
        if 'docs_url="/docs"' in content or "docs_url='/docs'" in content:
            log_result("SEC", "Swagger docs expuse public (/docs, /redoc)", "WARN", "medium",
                       "Dezactiveaza in productie: docs_url=None, redoc_url=None")


# ============================================================
# 4. VERIFICARI BACKEND
# ============================================================
def check_backend():
    section("4. BACKEND CHECKS")

    # --- Syntax check all Python files ---
    py_files = list(BACKEND_DIR.rglob("*.py"))
    py_files = [f for f in py_files if "__pycache__" not in str(f) and ".venv" not in str(f)
                and "venv" not in f.parts and "env" not in f.parts
                and "node_modules" not in str(f) and "site-packages" not in str(f)]
    syntax_errors = 0
    for py_file in py_files:
        try:
            content = py_file.read_text(encoding="utf-8", errors="ignore")
            compile(content, str(py_file), "exec")
        except SyntaxError as e:
            log_result("BACKEND", f"Syntax error: {py_file.relative_to(PROJECT_ROOT)}", "FAIL", "critical",
                       f"Linia {e.lineno}: {e.msg}")
            syntax_errors += 1

    if syntax_errors == 0:
        log_result("BACKEND", f"Toate {len(py_files)} fisiere Python: syntax OK", "PASS")

    # --- Check for bare except clauses ---
    bare_excepts = []
    for py_file in py_files:
        content = py_file.read_text(encoding="utf-8", errors="ignore")
        for i, line in enumerate(content.split("\n"), 1):
            stripped = line.strip()
            if stripped == "except:" or stripped.startswith("except: "):
                bare_excepts.append(f"{py_file.relative_to(PROJECT_ROOT)}:{i}")

    if bare_excepts:
        log_result("BACKEND", f"{len(bare_excepts)} bare except clauses gasite", "WARN", "medium",
                   "Fisiere: " + ", ".join(bare_excepts[:5]))
    else:
        log_result("BACKEND", "Niciun bare except gasit", "PASS")

    # --- Check for hardcoded secrets in Python code ---
    for py_file in py_files:
        content = py_file.read_text(encoding="utf-8", errors="ignore")
        if re.search(r'(?:api_key|secret|password)\s*=\s*["\'][^"\']{20,}["\']', content, re.IGNORECASE):
            if "example" not in py_file.name.lower() and "test" not in py_file.name.lower():
                log_result("BACKEND", f"Posibil secret hardcoded in {py_file.relative_to(PROJECT_ROOT)}", "WARN", "high")

    # --- Check for SQL injection patterns ---
    for py_file in py_files:
        content = py_file.read_text(encoding="utf-8", errors="ignore")
        # f-string SQL
        if re.search(r'(?:execute|text)\s*\(\s*f["\']', content):
            log_result("BACKEND", f"Potential SQL injection in {py_file.relative_to(PROJECT_ROOT)}", "FAIL", "critical",
                       "Foloseste parametri SQL (bind parameters) in loc de f-strings")

    # --- Check database models ---
    user_model = BACKEND_DIR / "models" / "user.py"
    if user_model.exists():
        content = user_model.read_text(encoding="utf-8", errors="ignore")
        # Check for missing ForeignKey
        if "Column(Integer, nullable=False, index=True)" in content and "ForeignKey" not in content.split("Column(Integer, nullable=False, index=True)")[0][-50:]:
            log_result("BACKEND", "ForeignKey lipseste pe user_id in modele dependente", "FAIL", "high",
                       "Adauga ForeignKey('users.id') pe coloanele user_id")

    # --- Check Alembic migrations ---
    versions_dir = BACKEND_DIR / "alembic" / "versions"
    if versions_dir.exists():
        migrations = list(versions_dir.glob("*.py"))
        if len(migrations) == 0:
            log_result("BACKEND", "Nicio migrare Alembic gasita", "WARN", "medium",
                       "Ruleaza: alembic revision --autogenerate -m 'Initial schema'")
        else:
            log_result("BACKEND", f"{len(migrations)} migrari Alembic gasite", "PASS")
    else:
        log_result("BACKEND", "Director alembic/versions/ lipseste", "WARN", "medium")

    # --- Check blocked_ips initialization ---
    adv_sec = BACKEND_DIR / "core" / "advanced_security.py"
    if adv_sec.exists():
        content = adv_sec.read_text(encoding="utf-8", errors="ignore")
        if "class ThreatDetector" in content and "self.blocked_ips" not in content:
            log_result("BACKEND", "ThreatDetector.blocked_ips nu este initializat!", "FAIL", "high",
                       "Adauga self.blocked_ips = set() in __init__")

    # --- Check database.py for dangerous settings ---
    db_py = BACKEND_DIR / "core" / "database.py"
    if db_py.exists():
        content = db_py.read_text(encoding="utf-8", errors="ignore")
        if "synchronous_commit = OFF" in content:
            log_result("BACKEND", "synchronous_commit = OFF - risc de pierdere date!", "WARN", "high",
                       "Aceasta setare dezactiveaza garantia de durabilitate a tranzactiilor.\n"
                       "Foloseste doar daca accepti pierderea ultimelor tranzactii la crash.")


# ============================================================
# 5. VERIFICARI FRONTEND
# ============================================================
def check_frontend():
    section("5. FRONTEND CHECKS")

    pkg_json = FRONTEND_DIR / "package.json"
    if not pkg_json.exists():
        log_result("FRONTEND", "package.json lipseste!", "FAIL", "critical")
        return

    try:
        pkg = json.loads(pkg_json.read_text(encoding="utf-8"))
        log_result("FRONTEND", f"Proiect: {pkg.get('name', 'unknown')} v{pkg.get('version', '?')}", "INFO")
    except json.JSONDecodeError as e:
        log_result("FRONTEND", f"package.json invalid: {e}", "FAIL", "critical")
        return

    # --- node_modules ---
    nm = FRONTEND_DIR / "node_modules"
    if nm.exists():
        log_result("FRONTEND", "node_modules/ exista", "PASS")
    else:
        log_result("FRONTEND", "node_modules/ lipseste!", "FAIL", "high",
                   "Ruleaza: cd Nursing_Training_AI_App/frontend && npm install")

    # --- Missing dependencies in package.json ---
    deps = pkg.get("dependencies", {})
    needed = {
        "reactflow": "reactflow este importat in KnowledgeGraph.tsx dar nu e in package.json",
        "@tailwindcss/forms": "Requis de tailwind.config.js (linia 70)",
        "@tailwindcss/typography": "Requis de tailwind.config.js (linia 71)",
    }
    for dep, reason in needed.items():
        if dep in deps:
            log_result("FRONTEND", f"Dependenta {dep} prezenta", "PASS")
        else:
            # Check if actually installed even without being in package.json
            if (nm / dep).exists() or (nm / dep.replace("/", os.sep)).exists():
                log_result("FRONTEND", f"{dep} instalat dar nu in package.json", "WARN", "low")
            else:
                log_result("FRONTEND", f"{dep} LIPSESTE", "FAIL", "high", reason)

    # --- Hardcoded API URLs ---
    hardcoded_urls = []
    for tsx_file in FRONTEND_DIR.rglob("*.tsx"):
        if "node_modules" in str(tsx_file):
            continue
        content = tsx_file.read_text(encoding="utf-8", errors="ignore")
        matches = re.findall(r"http://localhost:\d+", content)
        if matches:
            hardcoded_urls.append(f"{tsx_file.relative_to(PROJECT_ROOT)}: {', '.join(set(matches))}")

    if hardcoded_urls:
        log_result("FRONTEND", f"{len(hardcoded_urls)} fisiere cu URL-uri hardcoded", "WARN", "medium",
                   "Foloseste NEXT_PUBLIC_API_URL in loc de localhost\n" +
                   "\n".join(hardcoded_urls[:5]))

    # --- Tailwind content paths ---
    tw_config = FRONTEND_DIR / "tailwind.config.js"
    if tw_config.exists():
        content = tw_config.read_text(encoding="utf-8", errors="ignore")
        if "./src/" in content and not (FRONTEND_DIR / "src").exists():
            log_result("FRONTEND", "tailwind.config.js refera ./src/ dar directorul nu exista", "FAIL", "medium",
                       "Actualizeaza content paths la: './pages/**/*.{...}', './components/**/*.{...}'")

    # --- Port mismatch check ---
    index_html = FRONTEND_DIR / "index.html"
    if index_html.exists():
        content = index_html.read_text(encoding="utf-8", errors="ignore")
        ports = set(re.findall(r"localhost:(\d+)", content))
        if "8002" in ports and "8000" not in ports:
            log_result("FRONTEND", "index.html foloseste port 8002, backend-ul ruleaza pe 8000", "FAIL", "high",
                       "Schimba portul din 8002 in 8000 in index.html")


# ============================================================
# 6. VERIFICARI DATE / JSON
# ============================================================
def check_data_files():
    section("6. DATA FILES CHECK")

    question_banks_dir = BACKEND_DIR / "data" / "question_banks"
    if not question_banks_dir.exists():
        log_result("DATA", "Director question_banks/ lipseste", "WARN", "medium")
        return

    json_files = list(question_banks_dir.glob("*.json"))
    log_result("DATA", f"{len(json_files)} fisiere question bank gasite", "INFO")

    invalid_json = 0
    empty_banks = 0
    sample_checked = 0
    for jf in json_files[:100]:  # Verificam un esantion de 100
        try:
            data = json.loads(jf.read_text(encoding="utf-8"))
            sample_checked += 1
            if isinstance(data, dict):
                questions = data.get("questions", [])
                if len(questions) == 0:
                    empty_banks += 1
        except json.JSONDecodeError:
            invalid_json += 1
            log_result("DATA", f"JSON invalid: {jf.name}", "FAIL", "medium")

    if invalid_json == 0:
        log_result("DATA", f"Esantion de {sample_checked} fisiere JSON: toate valide", "PASS")
    if empty_banks > 0:
        log_result("DATA", f"{empty_banks} question banks goale (fara intrebari)", "WARN", "low")

    # --- Check NHS band expectations ---
    band_exp = BACKEND_DIR / "data" / "nhs_band_expectations.json"
    if band_exp.exists():
        try:
            data = json.loads(band_exp.read_text(encoding="utf-8"))
            log_result("DATA", f"nhs_band_expectations.json: {len(data)} band-uri definite", "PASS")
        except json.JSONDecodeError:
            log_result("DATA", "nhs_band_expectations.json: JSON invalid", "FAIL", "medium")
    else:
        log_result("DATA", "nhs_band_expectations.json lipseste", "WARN", "medium")


# ============================================================
# 7. VERIFICARI DOCKER
# ============================================================
def check_docker():
    section("7. DOCKER & DEPLOYMENT")

    # Docker compose
    dc = APP_DIR / "docker-compose.yml"
    if dc.exists():
        content = dc.read_text(encoding="utf-8", errors="ignore")
        log_result("DOCKER", "docker-compose.yml exista", "PASS")

        # Check for hardcoded passwords
        if re.search(r"(?:POSTGRES_PASSWORD|password):\s*\S+", content, re.IGNORECASE):
            log_result("DOCKER", "Credentiale hardcoded in docker-compose.yml", "WARN", "high",
                       "Foloseste variabile de mediu sau Docker secrets")
    else:
        log_result("DOCKER", "docker-compose.yml lipseste", "INFO")

    # Backend Dockerfile
    be_docker = BACKEND_DIR / "Dockerfile"
    if be_docker.exists():
        content = be_docker.read_text(encoding="utf-8", errors="ignore")
        if "--reload" in content:
            log_result("DOCKER", "Dockerfile backend contine --reload (doar dev!)", "WARN", "medium",
                       "Sterge --reload pentru productie")
        else:
            log_result("DOCKER", "Backend Dockerfile: OK", "PASS")


# ============================================================
# 8. VERIFICARI TESTS
# ============================================================
def check_tests():
    section("8. TESTS CHECK")

    tests_dir = BACKEND_DIR / "tests"
    if not tests_dir.exists():
        log_result("TESTS", "Director tests/ lipseste!", "FAIL", "high")
        return

    test_files = list(tests_dir.rglob("test_*.py"))
    log_result("TESTS", f"{len(test_files)} fisiere de test gasite", "INFO")

    for tf in test_files:
        log_result("TESTS", f"  {tf.name}", "INFO")

    # Try running tests
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pytest", str(tests_dir), "--co", "-q"],
            capture_output=True, text=True, timeout=30, cwd=str(BACKEND_DIR)
        )
        if result.returncode == 0:
            lines = result.stdout.strip().split("\n")
            log_result("TESTS", f"Test discovery OK: {lines[-1] if lines else 'OK'}", "PASS")
        else:
            log_result("TESTS", "Test discovery a esuat", "FAIL", "medium",
                       f"Error: {result.stderr[:200] if result.stderr else result.stdout[:200]}")
    except FileNotFoundError:
        log_result("TESTS", "pytest nu este instalat!", "FAIL", "high",
                   "pip install pytest pytest-asyncio")
    except subprocess.TimeoutExpired:
        log_result("TESTS", "Test discovery timeout", "WARN", "low")


# ============================================================
# 9. VERIFICARI GIT
# ============================================================
def check_git():
    section("9. GIT STATUS")

    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True, text=True, cwd=str(PROJECT_ROOT), timeout=30
        )
        changes = [l for l in result.stdout.strip().split("\n") if l.strip()]
        if len(changes) == 0:
            log_result("GIT", "Working tree curat", "PASS")
        else:
            log_result("GIT", f"{len(changes)} fisiere modificate/untracked", "INFO",
                       details="\n".join(changes[:10]))

        # Check branch
        branch = subprocess.run(
            ["git", "branch", "--show-current"],
            capture_output=True, text=True, cwd=str(PROJECT_ROOT), timeout=10
        )
        log_result("GIT", f"Branch curent: {branch.stdout.strip()}", "INFO")

    except Exception as e:
        log_result("GIT", f"Eroare git: {e}", "WARN", "low")


# ============================================================
# RAPORT FINAL
# ============================================================
def print_report():
    section("RAPORT SUMAR")

    total_issues = RESULTS["critical"] + RESULTS["high"] + RESULTS["medium"] + RESULTS["low"]

    print(f"""
  Verificari trecute:   {RESULTS['passed']}
  Probleme CRITICE:     {RESULTS['critical']}
  Probleme HIGH:        {RESULTS['high']}
  Probleme MEDIUM:      {RESULTS['medium']}
  Probleme LOW:         {RESULTS['low']}
  -------------------------
  TOTAL PROBLEME:       {total_issues}
""")

    if RESULTS["critical"] > 0:
        print("  !!! ATENTIE: Exista probleme CRITICE care necesita actiune IMEDIATA !!!")
        print()
        for check in RESULTS["checks"]:
            if check["severity"] == "critical" and check["status"] == "FAIL":
                print(f"    -> {check['name']}")
                if check["details"]:
                    for line in check["details"].split("\n")[:2]:
                        print(f"       {line}")
        print()

    # Save report to JSON
    report_path = PROJECT_ROOT / "troubleshoot_report.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(RESULTS, f, indent=2, ensure_ascii=False)
    print(f"  Raport detaliat salvat in: {report_path}")


# ============================================================
# MAIN
# ============================================================
def main():
    print("\n" + "=" * 60)
    print("  NURSING TRAINING AI - DIAGNOSTIC COMPLET")
    print(f"  Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    check_environment()
    check_python_dependencies()
    check_security()
    check_backend()
    check_frontend()
    check_data_files()
    check_docker()
    check_tests()
    check_git()
    print_report()

    return 1 if RESULTS["critical"] > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
