import subprocess
import sys
import os
import argparse

# ============================================================
# 여기를 바꾸면 전략이 교체됩니다!
# 사용 가능: "nul_lim_mok" (눌림목), "spring" (스프링)
# ============================================================
ACTIVE_STRATEGY = "spring"

def run_workflow(force_refresh=False):
    scripts = [
        ("execution/fetch_market_data.py", ["--force-refresh"] if force_refresh else []),
        ("execution/strategy_processor.py", ["--strategy", ACTIVE_STRATEGY]),
        ("execution/generate_charts.py", []),
        ("execution/search_news.py", []),
        ("execution/gmail_sender.py", [])
    ]

    # Make sure we are in the right directory
    base_dir = os.path.dirname(os.path.abspath(__file__))

    for script_rel_path, extra_args in scripts:
        script_full_path = os.path.join(base_dir, script_rel_path)
        print(f"\n>>> Starting: {script_rel_path}")

        # Run the script with a timeout (e.g., 30 minutes max per script)
        cmd = [sys.executable, script_full_path] + extra_args
        
        try:
            # Adding a 1800 second (30 minutes) timeout max for any single step
            result = subprocess.run(cmd, cwd=base_dir, timeout=1800)
            
            if result.returncode != 0:
                print(f"\n[!] Error occurred in {script_rel_path}. Stopping workflow.")
                sys.exit(1)
        except subprocess.TimeoutExpired:
            print(f"\n[!] ERROR: {script_rel_path} exceeded maximum execution time (30 minutes) and blocked the process. Forcefully terminating workflow.")
            sys.exit(1)

    print(f"\n>>> All steps completed successfully! Strategy: {ACTIVE_STRATEGY}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the entire stock mailing workflow.")
    parser.add_argument("--force-refresh", action="store_true", help="Force refresh market data even if it was already fetched today.")
    args = parser.parse_args()

    run_workflow(force_refresh=args.force_refresh)
