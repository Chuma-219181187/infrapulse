#!/usr/bin/env python3
"""
Astronomer Deployment Helper
Validates files and provides deployment status checks
"""

import os
import json
from pathlib import Path

def check_deployment_readiness():
    """Check if project is ready for Astronomer deployment"""
    
    print("=" * 70)
    print("🚀 Astronomer Deployment Readiness Check")
    print("=" * 70)
    
    checks = {
        "✅ Required Files": [],
        "⚠️  Configuration": [],
        "📦 Dependencies": [],
    }
    
    # 1. Check required files
    required_files = {
        "Dockerfile": "Dockerfile",
        "Astronomer Ignore": ".astronomerignore",
        "DAG File": "airflow/dags/infrapulse_etl_dag.py",
        "ETL Extract": "etl/extract.py",
        "ETL Transform": "etl/transform.py",
        "ETL Load": "etl/load.py",
        "Requirements": "requirements.txt",
        "Environment Prod": ".env.prod",
    }
    
    print("\n📋 File Checks:")
    for name, path in required_files.items():
        exists = os.path.exists(path)
        status = "✅" if exists else "❌"
        print(f"   {status} {name:<25} {path}")
        checks["✅ Required Files"].append({
            "name": name,
            "exists": exists,
            "path": path
        })
    
    # 2. Check configurations
    print("\n⚙️  Configuration Checks:")
    
    config_checks = {
        "Dockerfile": ["FROM", "COPY requirements.txt", "RUN pip install"],
        ".astronomerignore": [".env", ".git", "__pycache__"],
        "requirements.txt": ["airflow", "psycopg2"],
        "airflow/dags/infrapulse_etl_dag.py": ["DAG", "task"],
    }
    
    for filename, keywords in config_checks.items():
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                content = f.read()
                all_found = all(kw in content for kw in keywords)
                status = "✅" if all_found else "⚠️"
                print(f"   {status} {filename:<35} contains required keywords")
        else:
            print(f"   ❌ {filename:<35} not found")
    
    # 3. Check .env.prod has Railway credentials
    print("\n🔐 Environment Variables:")
    required_env_vars = [
        "POSTGRES_HOST",
        "POSTGRES_PORT",
        "POSTGRES_DB",
        "POSTGRES_USER",
        "POSTGRES_PASSWORD",
        "POSTGRES_SSL_MODE",
    ]
    
    env_vars_found = {}
    if os.path.exists('.env.prod'):
        with open('.env.prod', 'r', encoding='utf-8') as f:
            env_content = f.read()
            for var in required_env_vars:
                found = var in env_content
                status = "✅" if found else "❌"
                print(f"   {status} {var:<25} {'(set)' if found else '(missing)'}")
                env_vars_found[var] = found
    else:
        print("   ❌ .env.prod not found!")
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 Deployment Summary")
    print("=" * 70)
    
    all_files_present = all(os.path.exists(f) for f in required_files.values())
    all_env_present = all(env_vars_found.values()) if env_vars_found else False
    
    if all_files_present and all_env_present:
        print("\n✅ PROJECT IS READY FOR ASTRONOMER DEPLOYMENT!")
        print("\nNext Steps:")
        print("1. Go to: https://www.astronomer.io/")
        print("2. Sign up / Login")
        print("3. Create a workspace: 'infrapulse'")
        print("4. Create a deployment: 'infrapulse-prod'")
        print("5. Add environment variables (see ASTRONOMER_SETUP.md)")
        print("6. Deploy your DAGs")
        print("\nSee ASTRONOMER_SETUP.md for detailed instructions")
    else:
        print("\n⚠️  Some items are missing:")
        if not all_files_present:
            print("   • Missing required files")
        if not all_env_present:
            print("   • Missing or incomplete environment variables in .env.prod")
        print("\nFix these issues and try again")
    
    print("\n" + "=" * 70)

def display_environment_variables():
    """Display the environment variables that need to be set in Astronomer"""
    
    print("\n" + "=" * 70)
    print("🔐 Environment Variables to Set in Astronomer")
    print("=" * 70)
    print("\nThese are the variables that need to be set in Astronomer dashboard:")
    print("Deployment Settings → Environment Variables → Add Variable")
    print()
    
    if not os.path.exists('.env.prod'):
        print("⚠️  .env.prod not found - cannot display variables")
        return
    
    with open('.env.prod', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    print("{:<25} {:<50} {:<10}".format("Variable Name", "Value", "Secret"))
    print("-" * 85)
    
    for line in lines:
        if '=' in line and not line.startswith('#'):
            var_name, var_value = line.strip().split('=', 1)
            is_secret = "❌ No" if var_name in [
                "POSTGRES_HOST", "POSTGRES_PORT", "POSTGRES_DB", "POSTGRES_USER"
            ] else "✅ Yes"
            
            # Mask password for display
            if "PASSWORD" in var_name:
                display_value = var_value[:4] + "***hidden***" if len(var_value) > 4 else "***"
            else:
                display_value = var_value[:40]
            
            print(f"{var_name:<25} {display_value:<50} {is_secret:<10}")
    
    print("\n⚠️  Mark POSTGRES_PASSWORD as 'Secret'")
    print("=" * 70)

if __name__ == "__main__":
    check_deployment_readiness()
    display_environment_variables()
