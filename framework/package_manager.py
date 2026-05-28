# Package Manager & Provider System for Larapak

import os
import json
import importlib
import sys

class PackageManager:
    def __init__(self, vm=None):
        self.vm = vm
        self.packages_dir = "packages"
        os.makedirs(self.packages_dir, exist_ok=True)
        # Ensure the packages directory's parent is in sys.path so we can import packages.*
        root_dir = os.path.abspath(os.path.join(self.packages_dir, ".."))
        if root_dir not in sys.path:
            sys.path.append(root_dir)

    def discover_packages(self):
        """Scan packages/ directory and return list of package manifests."""
        packages = []
        if not os.path.exists(self.packages_dir):
            return packages
            
        for name in os.listdir(self.packages_dir):
            pkg_path = os.path.join(self.packages_dir, name)
            if os.path.isdir(pkg_path):
                manifest_path = os.path.join(pkg_path, "manifest.json")
                if os.path.exists(manifest_path):
                    try:
                        with open(manifest_path, "r", encoding="utf-8") as f:
                            manifest = json.load(f)
                            manifest["_path"] = pkg_path
                            packages.append(manifest)
                    except Exception as e:
                        print(f"[Package Manager] Gagal membaca manifest untuk {name}: {str(e)}")
        return packages

    def boot_packages(self):
        """Instantiate and boot service providers of discovered packages."""
        if not self.vm:
            return
            
        packages = self.discover_packages()
        for pkg in packages:
            providers = pkg.get("providers", [])
            for provider_path in providers:
                try:
                    # provider_path is like: "packages.auth_helper.providers.AuthHelperServiceProvider"
                    module_name, class_name = provider_path.rsplit(".", 1)
                    
                    # Ensure the module is imported
                    module = importlib.import_module(module_name)
                    provider_class = getattr(module, class_name)
                    
                    # Instantiate
                    provider = provider_class(self.vm)
                    
                    # Register
                    for register_method in ("ndaftar", "register"):
                        if hasattr(provider, register_method):
                            getattr(provider, register_method)()
                            break
                            
                    # Boot
                    for boot_method in ("uripna", "boot"):
                        if hasattr(provider, boot_method):
                            getattr(provider, boot_method)()
                            break
                            
                    print(f"[Package Manager] Berhasil me-load provider: {class_name}")
                except Exception as e:
                    print(f"[Package Manager] Gagal me-load provider '{provider_path}': {str(e)}")
                    import traceback
                    traceback.print_exc()

    def install_package(self, package_name):
        """Simulate package installation by writing a package structure in packages/."""
        print(f"Mengunduh paket '{package_name}' dari registry...")
        
        # Convert package-name (e.g. auth-helper) to a python-safe module folder name
        pkg_module_name = package_name.replace("-", "_").lower()
        pkg_dir = os.path.join(self.packages_dir, pkg_module_name)
        os.makedirs(pkg_dir, exist_ok=True)
        
        # Create manifest.json
        class_name = "".join(x.capitalize() for x in pkg_module_name.split("_")) + "ServiceProvider"
        provider_path = f"packages.{pkg_module_name}.providers.{class_name}.{class_name}"
        
        manifest = {
            "name": package_name,
            "version": "1.0.0",
            "providers": [provider_path]
        }
        
        with open(os.path.join(pkg_dir, "manifest.json"), "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=4)
            
        # Create provider file structure
        providers_dir = os.path.join(pkg_dir, "providers")
        os.makedirs(providers_dir, exist_ok=True)
        
        # Touch __init__.py files
        with open(os.path.join(pkg_dir, "__init__.py"), "w") as f:
            pass
        with open(os.path.join(providers_dir, "__init__.py"), "w") as f:
            pass
            
        # Write provider code
        provider_code = f"""# Service Provider untuk paket {package_name}

class {class_name}:
    def __init__(self, vm):
        self.vm = vm

    def ndaftar(self):
        # Register bindings or globals in the VM
        print("[{package_name}] Mendaftarkan fitur package ke VM")
        self.vm.globals["{pkg_module_name}_versi"] = "1.0.0"

    def uripna(self):
        # Perform booting tasks
        print("[{package_name}] Mengaktifkan package")
"""
        with open(os.path.join(providers_dir, f"{class_name}.py"), "w", encoding="utf-8") as f:
            f.write(provider_code)
            
        print(f"Berhasil menginstal paket '{package_name}' di '{pkg_dir}'")
