import os
import subprocess

def create_desktop_shortcut():
    desktop_dir = os.path.join(os.environ["USERPROFILE"], "Desktop")
    shortcut_path = os.path.join(desktop_dir, "경공매데이터 업데이트.lnk")
    target_path = r"c:\Users\llll\Documents\두인경매\바이브코딩\update_data.bat"
    working_dir = r"c:\Users\llll\Documents\두인경매\바이브코딩"
    
    # PowerShell command to create shortcut
    ps_command = f"""
    $WshShell = New-Object -ComObject WScript.Shell
    $Shortcut = $WshShell.CreateShortcut("{shortcut_path}")
    $Shortcut.TargetPath = "{target_path}"
    $Shortcut.WorkingDirectory = "{working_dir}"
    $Shortcut.Save()
    """
    
    print(f"Creating shortcut on Desktop: {shortcut_path}")
    try:
        subprocess.run(["powershell", "-Command", ps_command], check=True)
        print("Shortcut created successfully!")
    except Exception as e:
        print("Failed to create shortcut:", e)

if __name__ == "__main__":
    create_desktop_shortcut()
