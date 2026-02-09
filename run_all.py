import subprocess
import sys
import os

scripts = [
    "execution/fetch_market_data.py",
    "execution/strategy_processor.py",
    "execution/generate_charts.py",
    "execution/search_news.py",
    "execution/gmail_sender.py"
]

def run_workflow():
    # Make sure we are in the right directory
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    for script_rel_path in scripts:
        script_full_path = os.path.join(base_dir, script_rel_path)
        print(f"\n>>> Starting: {script_rel_path}")
        
        # Run the script
        result = subprocess.run([sys.executable, script_full_path], cwd=base_dir)
        
        if result.returncode != 0:
            print(f"\n[!] Error occurred in {script_rel_path}. Stopping workflow.")
            sys.exit(1)
            
    print("\n>>> All steps completed successfully! Check your email.")

if __name__ == "__main__":
    run_workflow()
