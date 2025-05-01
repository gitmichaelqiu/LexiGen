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
                messagebox.showerror(
                    get_translation(self.language, "error_title"),
                    get_translation(self.language, "update_check_error")
                )
                return "error"
        except Exception as e:
            messagebox.showerror(
                get_translation(self.language, "error_title"),
                get_translation(self.language, "update_error_msg")
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
            # macOS - look for .dmg
            for asset in release_data["assets"]:
                if asset["name"].endswith((".dmg", ".zip")):
                    return asset["browser_download_url"]
        elif system == "windows":
            # Windows - look for .exes
            for asset in release_data["assets"]:
                if asset["name"].endswith((".exe", ".zip")):
                    return asset["browser_download_url"]
                    
        messagebox.showerror(
            get_translation(self.language, "error_title"),
            get_translation(self.language, "update_check_error")
        )
        return None
                
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
            # Determine appropriate file extension based on URL
            file_extension = ".zip"  # Default
            if self.download_url:
                if self.download_url.lower().endswith(".dmg"):
                    file_extension = ".dmg"
                elif self.download_url.lower().endswith(".exe"):
                    file_extension = ".exe"
                    
            # Create a temporary file to download to with correct extension
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=file_extension)
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
            get_translation(self.language, "update_error_msg")
        )
        
        self.is_downloading = False
    
    def _apply_update(self):
        """Apply the downloaded update"""
        if not self.downloaded_file:
            return
            
        try:
            # Determine the file type
            file_extension = os.path.splitext(self.downloaded_file)[1].lower()
            
            if file_extension == ".dmg" and platform.system().lower() == "darwin":
                # For macOS DMG files
                self._install_dmg_update()
            elif file_extension == ".exe" and platform.system().lower() == "windows":
                # For Windows installer EXE files
                self._install_exe_update()
            elif file_extension == ".zip":
                # For ZIP files, extract and install
                temp_dir = tempfile.mkdtemp()
                with zipfile.ZipFile(self.downloaded_file, 'r') as zip_ref:
                    zip_ref.extractall(temp_dir)
                self._install_update(temp_dir)
            else:
                # Fallback for unknown file types - try to handle as executable
                self._install_generic_executable()
            
        except Exception as e:
            messagebox.showerror(
                #Debugging
                #get_translation(self.language, "update_error"),
                #get_translation(self.language, "update_error_msg")
                "Update Error",
                "Not even go to install exe update."
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
            # For generic systems, just copy files
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
                # Start a script to replace the app bundle after we quit
                self._run_mac_update_script(app_bundle)
        else:
            # No app bundle found, try generic update
            self._install_generic_update(extracted_path)
    
    def _run_mac_update_script(self, new_app_path, mount_point=None):
        """Run a script to replace the app after we quit"""
        # Get current app path
        current_app_path = None
        if getattr(sys, 'frozen', False):
            # Running as frozen/packaged app
            current_app_path = os.path.dirname(os.path.dirname(sys.executable))
        else:
            # Running as script, assume Python environment
            current_app_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        target_path = None
        if current_app_path.endswith(".app"):
            # Using an app bundle, replace it
            target_path = os.path.dirname(current_app_path)
        else:
            # Not using app bundle, use Applications folder
            target_path = "/Applications"
        
        # Create update script that will:
        # 1. Wait for app to quit
        # 2. Copy the new app to the target location
        # 3. Unmount the DMG (if provided)
        # 4. Launch the new app
        unmount_command = f'hdiutil detach "{mount_point}" -force' if mount_point else ''
        
        script_content = f"""#!/bin/bash
sleep 2
if [ -d "{os.path.join(target_path, os.path.basename(new_app_path))}" ]; then
    rm -rf "{os.path.join(target_path, os.path.basename(new_app_path))}"
fi
cp -R "{new_app_path}" "{target_path}/"
{unmount_command}
open "{os.path.join(target_path, os.path.basename(new_app_path))}"
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

    def _install_dmg_update(self):
        """Handle installation from a DMG file on macOS"""
        # Mount the DMG
        mount_point = tempfile.mkdtemp()
        mount_cmd = ["hdiutil", "attach", self.downloaded_file, "-mountpoint", mount_point, "-nobrowse"]
        
        try:
            # Mount the DMG
            subprocess.run(mount_cmd, check=True)
            
            # Look for .app bundles in the mounted DMG
            app_bundle = None
            for item in os.listdir(mount_point):
                if item.endswith(".app"):
                    app_bundle = os.path.join(mount_point, item)
                    break
            
            if app_bundle:
                # Found an app bundle, create install script
                self._run_mac_update_script(app_bundle, mount_point)
            else:
                # No app bundle found, maybe there's a pkg installer
                pkg_installer = None
                for item in os.listdir(mount_point):
                    if item.endswith(".pkg"):
                        pkg_installer = os.path.join(mount_point, item)
                        break
                
                if pkg_installer:
                    # Run the pkg installer
                    install_cmd = ["open", pkg_installer]
                    subprocess.Popen(install_cmd)
                    
                    # Wait a bit, then exit the app
                    if self.root:
                        self.root.after(2000, self.root.destroy)
                else:
                    # Can't find anything to install
                    raise Exception("No application or installer found in the DMG")
        except Exception as e:
            # Unmount and clean up in case of error
            try:
                subprocess.run(["hdiutil", "detach", mount_point, "-force"], check=False)
            except:
                pass
            
            # Re-raise the exception
            raise e

    def _install_exe_update(self):
        """Handle installation from an EXE file on Windows"""
        try:
            # For portable app, we need to replace the current executable
            current_exe_path = sys.executable if getattr(sys, 'frozen', False) else None
            
            # Write debug info to file
            debug_file = os.path.join(tempfile.gettempdir(), "lexigen_update_debug.log")
            with open(debug_file, 'w') as f:
                f.write(f"Debug: Current executable path: {current_exe_path}\n")
                f.write(f"Debug: Is frozen: {getattr(sys, 'frozen', False)}\n")
            
            if not current_exe_path:
                with open(debug_file, 'a') as f:
                    f.write("Debug: Not running as frozen executable\n")
                    f.write(f"Debug: Running downloaded file: {self.downloaded_file}\n")
                subprocess.Popen([self.downloaded_file])
                if self.root:
                    self.root.after(500, self.root.destroy)
                return
                
            # Create a batch script to:
            # 1. Wait for current process to exit
            # 2. Copy the new exe over the old one
            # 3. Start the new exe
            batch_script = f"""@echo off
echo Debug: Starting update process
echo Debug: Current exe: {current_exe_path}
echo Debug: New exe: {self.downloaded_file}
timeout /t 2 /nobreak
echo Debug: Copying new exe...
copy /Y "{self.downloaded_file}" "{current_exe_path}"
echo Debug: Starting new exe...
start "" "{current_exe_path}"
echo Debug: Cleaning up...
del "%~f0"
"""
            with open(debug_file, 'a') as f:
                f.write(f"Debug: Generated batch script:\n{batch_script}\n")
            
            # Write the batch script to a temporary file
            script_path = os.path.join(tempfile.gettempdir(), "lexigen_update.bat")
            with open(debug_file, 'a') as f:
                f.write(f"Debug: Writing batch script to: {script_path}\n")
            with open(script_path, 'w') as f:
                f.write(batch_script)
            
            # Execute the batch script
            with open(debug_file, 'a') as f:
                f.write("Debug: Executing batch script\n")
            subprocess.Popen(["cmd", "/c", script_path], shell=True)
            
            # Exit the app
            if self.root:
                with open(debug_file, 'a') as f:
                    f.write("Debug: Scheduling app exit\n")
                self.root.after(500, self.root.destroy)
            
        except Exception as e:
            with open(debug_file, 'a') as f:
                f.write(f"Debug: Error during update: {str(e)}\n")
                f.write(f"Debug: Error type: {type(e)}\n")
                import traceback
                f.write(f"Debug: Traceback:\n{traceback.format_exc()}\n")
            messagebox.showerror(
                get_translation(self.language, "update_error"),
                get_translation(self.language, "update_error_msg")
            )
            raise e
    def _install_generic_executable(self):
        """Handle installation of a generic executable file"""
        try:
            if platform.system().lower() == "windows":
                # For Windows, just run the executable
                subprocess.Popen([self.downloaded_file])
            elif platform.system().lower() == "darwin":
                # For macOS, make executable and run
                os.chmod(self.downloaded_file, 0o755)
                subprocess.Popen(["open", self.downloaded_file])
            else:
                # For other platforms, try to make executable and run
                os.chmod(self.downloaded_file, 0o755)
                subprocess.Popen([self.downloaded_file])
                
            # Exit the app
            if self.root:
                self.root.after(500, self.root.destroy)
                
        except Exception as e:
            messagebox.showerror(
                get_translation(self.language, "update_error"),
                get_translation(self.language, "update_error_msg")
            )
            raise e 