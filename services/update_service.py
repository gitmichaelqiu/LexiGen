import requests
import webbrowser
import os
import sys
import shutil
import platform
import tempfile
import zipfile
import threading
import subprocess
from tkinter import messagebox, Toplevel, ttk, Label
import tkinter as tk
from models.config import VERSION, get_assets_path
from models.translations import get_translation

class UpdateService:
    def __init__(self, language="English"):
        self.language = language
        self.latest_version = None
        self.download_url = None
        self.download_progress = 0
        self.progress_window = None
        self.progress_bar = None
        self.progress_label = None
        self.is_downloading = False
        self.downloaded_file = None
        self.root = None

    def check_for_updates(self, show_message=True, auto_update=False):
        """
        Check for updates from the GitHub repository.
        
        Args:
            show_message: Whether to show a message dialog for the result
            auto_update: Whether to show an option to auto-update instead of visiting the website
            
        Returns:
            string: Status of the update check ("new_version", "up_to_date", or "error")
        """
        try:
            response = requests.get("https://api.github.com/repos/gitmichaelqiu/LexiGen/releases/latest")
            if response.status_code == 200:
                release_data = response.json()
                self.latest_version = release_data["tag_name"].lstrip('v')
                
                # Get the download URL for the platform-specific release
                self.download_url = self._get_download_url(release_data)
                
                if self.latest_version > VERSION:
                    if show_message:
                        if auto_update and self.download_url:
                            # Ask user if they want to update automatically
                            if messagebox.askyesno(
                                get_translation(self.language, "update_now_title"),
                                get_translation(self.language, "update_now_msg").format(
                                    version=self.latest_version,
                                    current_version=VERSION
                                )
                            ):
                                self._download_update()
                        else:
                            # Traditional approach - open browser to download page
                            if messagebox.askyesno(
                                get_translation(self.language, "update_available_title"),
                                get_translation(self.language, "update_available_msg").format(
                                    version=self.latest_version,
                                    current_version=VERSION
                                )
                            ):
                                webbrowser.open("https://github.com/gitmichaelqiu/LexiGen/releases/latest")
                    return "new_version"
                else:
                    if show_message:
                        messagebox.showinfo(
                            get_translation(self.language, "no_updates_title"),
                            get_translation(self.language, "no_updates_msg").format(version=VERSION)
                        )
                    return "up_to_date"
            else:
                if show_message:
                    messagebox.showerror(
                        get_translation(self.language, "error_title"),
                        get_translation(self.language, "update_check_error")
                    )
                return "error"
        except Exception as e:
            if show_message:
                messagebox.showerror(
                    get_translation(self.language, "error_title"),
                    get_translation(self.language, "update_error_msg").format(error=str(e))
                )
            return "error"
    
    def _get_download_url(self, release_data):
        """
        Get the appropriate download URL for the current platform.
        
        Args:
            release_data: The release data JSON from GitHub API
            
        Returns:
            string: The download URL for the current platform or None if not found
        """
        if "assets" not in release_data:
            return None
            
        system = platform.system().lower()
        if system == "darwin":
            # macOS - look for .dmg or .zip files
            for asset in release_data["assets"]:
                if asset["name"].endswith((".dmg", ".zip")) and "macos" in asset["name"].lower():
                    return asset["browser_download_url"]
        elif system == "windows":
            # Windows - look for .exe or .zip files
            for asset in release_data["assets"]:
                if asset["name"].endswith((".exe", ".zip")) and "windows" in asset["name"].lower():
                    return asset["browser_download_url"]
        elif system == "linux":
            # Linux - look for .AppImage or .zip files
            for asset in release_data["assets"]:
                if asset["name"].endswith((".AppImage", ".zip")) and "linux" in asset["name"].lower():
                    return asset["browser_download_url"]
                    
        # If no platform-specific download is found, return the ZIP if available
        for asset in release_data["assets"]:
            if asset["name"].endswith(".zip"):
                return asset["browser_download_url"]
                
        # If no suitable asset is found, return the first asset URL or None
        return release_data["assets"][0]["browser_download_url"] if release_data["assets"] else None
    
    def _download_update(self):
        """Start downloading the update in a background thread"""
        if self.is_downloading or not self.download_url:
            return
            
        self.is_downloading = True
        self._create_progress_window()
        
        # Start download in a separate thread to not block the UI
        download_thread = threading.Thread(target=self._download_thread)
        download_thread.daemon = True
        download_thread.start()
    
    def _create_progress_window(self):
        """Create a progress window for the download"""
        self.progress_window = Toplevel()
        self.progress_window.title(get_translation(self.language, "downloading_update"))
        self.progress_window.geometry("400x100")
        self.progress_window.resizable(False, False)
        
        # Make window modal
        self.progress_window.transient(self.root)
        self.progress_window.grab_set()
        
        # Create a frame for the progress elements
        frame = ttk.Frame(self.progress_window, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Add a label for the progress text
        self.progress_label = ttk.Label(
            frame, 
            text=get_translation(self.language, "downloading_progress").format(percent=0)
        )
        self.progress_label.pack(pady=(0, 5))
        
        # Add the progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            frame, 
            variable=self.progress_var,
            maximum=100
        )
        self.progress_bar.pack(fill=tk.X, pady=(5, 10))
    
    def _download_thread(self):
        """Background thread for downloading the update"""
        try:
            # Create a temporary file to download to
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".zip")
            temp_file.close()
            self.downloaded_file = temp_file.name
            
            # Download with progress updates
            response = requests.get(self.download_url, stream=True)
            total_size = int(response.headers.get('content-length', 0))
            block_size = 1024  # 1 Kibibyte
            downloaded = 0
            
            with open(self.downloaded_file, 'wb') as f:
                for data in response.iter_content(block_size):
                    f.write(data)
                    downloaded += len(data)
                    
                    # Update progress
                    if total_size > 0:
                        percent = int(downloaded * 100 / total_size)
                        self._update_progress(percent)
            
            # Download complete
            self._update_progress(100)
            
            # Show success message
            self.progress_window.after(500, self._show_download_complete)
            
        except Exception as e:
            # Show error message
            self.progress_window.after(0, lambda: self._show_download_error(str(e)))
    
    def _update_progress(self, percent):
        """Update the progress UI from the download thread"""
        if not self.progress_window:
            return
            
        # Update the UI from the main thread
        self.progress_window.after(0, lambda: self._update_progress_ui(percent))
    
    def _update_progress_ui(self, percent):
        """Update the progress UI components"""
        if not self.progress_window:
            return
            
        self.progress_var.set(percent)
        self.progress_label.config(
            text=get_translation(self.language, "downloading_progress").format(percent=percent)
        )
        
        # Force update of the UI
        self.progress_window.update_idletasks()
    
    def _show_download_complete(self):
        """Show the download complete message and prepare for update"""
        try:
            if not self.progress_window:
                return
                
            self.progress_window.destroy()
            self.progress_window = None
            
            # Ask to apply the update
            if messagebox.askyesno(
                get_translation(self.language, "update_complete"),
                get_translation(self.language, "update_complete_msg")
            ):
                self._apply_update()
        except Exception as e:
            messagebox.showerror(
                get_translation(self.language, "error_title"),
                get_translation(self.language, "unexpected_error_msg").format(error=str(e))
            )
    
    def _show_download_error(self, error_message):
        """Show an error message for download failures"""
        if self.progress_window:
            self.progress_window.destroy()
            self.progress_window = None
            
        messagebox.showerror(
            get_translation(self.language, "update_error"),
            get_translation(self.language, "update_error_msg").format(error=error_message)
        )
        
        self.is_downloading = False
    
    def _apply_update(self):
        """Apply the downloaded update"""
        if not self.downloaded_file:
            return
            
        try:
            # Extract the update to a temporary directory
            temp_dir = tempfile.mkdtemp()
            
            with zipfile.ZipFile(self.downloaded_file, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
            
            # Determine executable path based on platform
            self._install_update(temp_dir)
            
        except Exception as e:
            messagebox.showerror(
                get_translation(self.language, "update_error"),
                get_translation(self.language, "update_error_msg").format(error=str(e))
            )
            
            # Clean up
            self._cleanup()
    
    def _install_update(self, extracted_path):
        """Install the update based on the platform"""
        system = platform.system().lower()
        
        if system == "darwin":
            # For macOS, handle .app bundle
            self._install_mac_update(extracted_path)
        elif system == "windows":
            # For Windows, handle .exe installer or direct files
            self._install_windows_update(extracted_path)
        else:
            # For Linux or other systems, just copy files
            self._install_generic_update(extracted_path)
    
    def _install_mac_update(self, extracted_path):
        """Install update on macOS"""
        # Look for .app bundle
        app_bundle = None
        for root, dirs, files in os.walk(extracted_path):
            for dir_name in dirs:
                if dir_name.endswith(".app"):
                    app_bundle = os.path.join(root, dir_name)
                    break
            if app_bundle:
                break
        
        if app_bundle:
            # Start a script to replace the app bundle after we quit
            self._run_mac_update_script(app_bundle)
        else:
            # No app bundle found, try generic update
            self._install_generic_update(extracted_path)
    
    def _run_mac_update_script(self, new_app_path):
        """Run a script to replace the app after we quit"""
        # Get current app path
        current_app_path = os.path.dirname(os.path.dirname(sys.executable))
        
        if not current_app_path.endswith(".app"):
            # Not running from an app bundle, use generic update
            self._install_generic_update(os.path.dirname(new_app_path))
            return
        
        # Create update script
        script_content = f"""#!/bin/bash
sleep 2
rm -rf "{current_app_path}"
cp -R "{new_app_path}" "{os.path.dirname(current_app_path)}"
open "{os.path.join(os.path.dirname(current_app_path), os.path.basename(new_app_path))}"
"""
        
        # Write script to temp file
        script_path = os.path.join(tempfile.gettempdir(), "lexigen_update.sh")
        with open(script_path, 'w') as f:
            f.write(script_content)
        
        # Make executable
        os.chmod(script_path, 0o755)
        
        # Run script
        subprocess.Popen(["/bin/bash", script_path])
        
        # Exit the app
        if self.root:
            self.root.after(500, self.root.destroy)
    
    def _install_windows_update(self, extracted_path):
        """Install update on Windows"""
        # Look for installer file
        installer = None
        for root, dirs, files in os.walk(extracted_path):
            for file_name in files:
                if file_name.endswith(".exe") and "setup" in file_name.lower():
                    installer = os.path.join(root, file_name)
                    break
            if installer:
                break
        
        if installer:
            # Run installer
            subprocess.Popen([installer])
            
            # Exit the app
            if self.root:
                self.root.after(500, self.root.destroy)
        else:
            # No installer found, try generic update
            self._install_generic_update(extracted_path)
    
    def _install_generic_update(self, extracted_path):
        """Generic update by copying files to the application directory"""
        # Get the application directory
        if getattr(sys, 'frozen', False):
            # Running as frozen/packaged app
            app_dir = os.path.dirname(sys.executable)
        else:
            # Running as script
            app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # Create a batch file for Windows or script for Unix to copy files after app closes
        if platform.system().lower() == "windows":
            self._create_windows_update_script(extracted_path, app_dir)
        else:
            self._create_unix_update_script(extracted_path, app_dir)
    
    def _create_windows_update_script(self, src_dir, dest_dir):
        """Create a Windows batch file to copy files after app closes"""
        script_content = f"""@echo off
timeout /t 2 /nobreak
xcopy /E /I /Y "{src_dir}\\*" "{dest_dir}"
start "" "{os.path.join(dest_dir, 'LexiGen.exe')}"
"""
        
        # Write script to temp file
        script_path = os.path.join(tempfile.gettempdir(), "lexigen_update.bat")
        with open(script_path, 'w') as f:
            f.write(script_content)
        
        # Run script
        subprocess.Popen(["cmd", "/c", script_path], shell=True)
        
        # Exit the app
        if self.root:
            self.root.after(500, self.root.destroy)
    
    def _create_unix_update_script(self, src_dir, dest_dir):
        """Create a Unix shell script to copy files after app closes"""
        script_content = f"""#!/bin/bash
sleep 2
cp -R "{src_dir}/"* "{dest_dir}/"
cd "{dest_dir}"
./LexiGen
"""
        
        # Write script to temp file
        script_path = os.path.join(tempfile.gettempdir(), "lexigen_update.sh")
        with open(script_path, 'w') as f:
            f.write(script_content)
        
        # Make executable
        os.chmod(script_path, 0o755)
        
        # Run script
        subprocess.Popen(["/bin/bash", script_path])
        
        # Exit the app
        if self.root:
            self.root.after(500, self.root.destroy)
    
    def _cleanup(self):
        """Clean up temporary files"""
        if self.downloaded_file and os.path.exists(self.downloaded_file):
            try:
                os.unlink(self.downloaded_file)
            except:
                pass
        
        self.downloaded_file = None
        self.is_downloading = False
        
    def set_root(self, root):
        """Set the root window for the update service"""
        self.root = root