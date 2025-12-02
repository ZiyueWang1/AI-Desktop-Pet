"""
Startup test script
Used to verify environment and dependencies are correct
"""
import sys

def check_python_version():
    """Check Python version"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 10):
        print(f"❌ Python version too low: {version.major}.{version.minor}")
        print("   Requires Python 3.10 or higher")
        return False
    print(f"✅ Python version: {version.major}.{version.minor}.{version.micro}")
    return True

def check_pyqt6():
    """Check if PyQt6 is installed"""
    try:
        import PyQt6
        print(f"✅ PyQt6 installed: {PyQt6.__version__}")
        return True
    except ImportError:
        print("❌ PyQt6 not installed")
        print("   Please run: pip install -r requirements.txt")
        return False

def check_project_structure():
    """Check project structure"""
    import os
    from pathlib import Path
    
    required_files = [
        "src/main.py",
        "src/window.py",
        "src/chat_ui.py",
        "src/config_manager.py",
        "src/personality_setup.py",
        "run.py",
        "requirements.txt"
    ]
    
    missing = []
    for file in required_files:
        if not Path(file).exists():
            missing.append(file)
    
    if missing:
        print(f"❌ Missing files: {', '.join(missing)}")
        return False
    
    print("✅ Project structure complete")
    return True

def main():
    """Main check function"""
    print("=" * 50)
    print("AI Desktop Pet - Startup Environment Check")
    print("=" * 50)
    print()
    
    checks = [
        ("Python Version", check_python_version),
        ("PyQt6 Dependency", check_pyqt6),
        ("Project Structure", check_project_structure),
    ]
    
    results = []
    for name, check_func in checks:
        print(f"Checking {name}...")
        result = check_func()
        results.append(result)
        print()
    
    print("=" * 50)
    if all(results):
        print("✅ All checks passed! You can run the application now")
        print()
        print("Startup command: python run.py")
    else:
        print("❌ Some checks failed, please fix and try again")
    print("=" * 50)

if __name__ == "__main__":
    main()

