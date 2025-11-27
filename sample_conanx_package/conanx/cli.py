#!/usr/bin/env python3
 
import json
import subprocess
from pathlib import Path
from typing import Dict, List
import click
import requests
import sys
import os
import shutil
 
 
class ConanClient:
    def __init__(self):
        self.conan_cmd = "conan"

    def run(self, cmd: List[str], capture=True):
        try:
            return subprocess.run([self.conan_cmd] + cmd, capture_output=capture, text=True, check=True)
        except subprocess.CalledProcessError as e:
            click.secho(f"Command failed: {' '.join(cmd)}", fg='red')
            raise

    def profile_exists(self):
        """Check if default conan profile exists"""
        try:
            result = self.run(["profile", "show"], capture=True)
            return True
        except:
            return False

    def ensure_profile(self):
        """Ensure conan profile exists, create if missing"""
        if not self.profile_exists():
            click.secho("Default Conan profile not found!", fg='yellow')
            click.secho("Creating default profile automatically...", fg='cyan')
            try:
                self.run(["profile", "detect", "--force"], capture=False)
                click.secho("Profile created successfully!", fg='green')
                return True
            except Exception as e:
                click.secho(f"Failed to create profile: {str(e)}", fg='red')
                click.secho("\nTROUBLESHOOTING:", fg='yellow', bold=True)
                click.secho("1. Try manually running: conan profile detect", fg='yellow')
                click.secho("2. Or run the setup command: python runConan.py setup", fg='yellow')
                return False
        return True
   
    def create(self, conanfile: str, name: str, version: str, user: str = None, channel: str = None):
        cmd = ["create", conanfile, "--name", name, "--version", version]
        if user: cmd.extend(["--user", user])
        if channel: cmd.extend(["--channel", channel])
        self.run(cmd, capture=False)
   
    def upload(self, ref: str, remote: str):
        # Check if package already exists on remote
        # if self.package_exists_on_remote(ref, remote):
        #     raise ValueError(f"Package {ref} already exists on remote {remote}")
        self.run(["upload", ref, "--remote", remote, "--confirm"], capture=False)
   
    def install(self, conanfile: str, remote: str, output: str, build: str = "missing"):
        self.run(["install", conanfile, "--remote", remote, "--output-folder", output, "--build", build, "--envs-generation=false"], capture=False)
   
    def search(self, pattern: str, remote: str = None):
        cmd = ["search", pattern]
        if remote: cmd.extend(["--remote", remote])
        try:
            result = self.run(cmd)
            print("8888", result, "8888", result.stdout.strip().split('\n')[-1].strip())
            return result.stdout.strip().split('\n')[-1].strip()
        except:
            return ""
   
    def cache_exists(self, ref: str):
        try:
            output = self.run(["list", ref])
            if "ERROR: Recipe" in output.stdout:
                return False
            return True
        except Exception:
            return False
            
    def package_exists_on_remote(self, ref: str, remote: str):
        """Check if package exists on remote"""
        try:
            result = self.search(ref, remote)
            print("*/"*10)
            print(result)
            print(f"{ref in result}")
            if("ERROR: Recipe" in result):
                return False
            return True
        except:
            return False
    
    def remove_from_cache(self, pattern: str):
        """Remove packages from local cache"""
        try:
            self.run(["remove", pattern, "--confirm"], capture=False)
            return True
        except:
            return False
    
    def remove_from_remote(self, package_name: str, version: str, revision_id: str = None, 
                          user: str = "marelli", channel: str = "stable", remote: str = None):
        """Remove package from Artifactory remote based on packageId not revisionId"""
        try:
            # Build the reference
            ref = f"{package_name}/{version}@{user}/{channel}"
            
            if revision_id:
                ref += f"#{revision_id}"
            
            cmd = ["remove", ref]
            if remote:
                cmd.extend(["--remote", remote])
            cmd.append("--confirm")
            
            self.run(cmd, capture=False)
            return True
        except Exception as e:
            click.secho(f"Failed to remove {ref} from remote: {str(e)}", fg='red')
            return False
 
 
def load_config(file: str) -> Dict:
    with open(file, 'r') as f:
        config = json.load(f)
   
    # Handle both single package and multiple packages format
    if isinstance(config, dict) and "packages" in config:
        # Multiple packages format
        packages = config["packages"]
        for pkg in packages:
            required = ["name", "version", "user", "channel", "extensions", "remote"]
            missing = [f for f in required if f not in pkg]
            if missing:
                raise ValueError(f"Missing fields in package {pkg.get('name', 'unknown')}: {missing}")
        return config
    else:
        # Single package format (backward compatibility)
        required = ["name", "version", "user", "channel", "extensions"]
        missing = [f for f in required if f not in config]
        if missing:
            raise ValueError(f"Missing fields: {missing}")
        # Convert to multiple packages format
        return {
            "packages": [config],
            "target_path": config.get("target_path", "./output")
        }
 
def generate_default_upload_conanfile(pkg_config: Dict):
    """Generate conanfile that packages from parent directory"""
    content = f'''from conan import ConanFile
from conan.tools.files import copy
import os
import shutil
 
class {pkg_config["name"].capitalize()}Conan(ConanFile):
    name = "{pkg_config["name"]}"
    version = "{pkg_config["version"]}"

    ##
    settings = "os", "compiler", "build_type", "arch"
    options = {{"shared": [True, False]}}
    default_options = {{"shared": True}}
    ##
    
    # We'll handle source export manually
    
    def export_sources(self):
        # Get the parent directory (one level up from conan folder)
        parent_dir = os.path.abspath(os.path.join(self.recipe_folder, ".."))
        
        # Copy all files from parent directory to export folder, excluding conan folder
        for item in os.listdir(parent_dir):
            if item == "conan":  # Skip the conan folder
                continue
                
            source_path = os.path.join(parent_dir, item)
            dest_path = os.path.join(self.export_sources_folder, item)
            
            try:
                if os.path.isdir(source_path):
                    shutil.copytree(source_path, dest_path)
                else:
                    shutil.copy2(source_path, dest_path)
            except Exception as e:
                self.output.info(f"Warning: Could not copy {{item}}: {{e}}")
   
    def package(self):
        # Package files with specified extensions from the entire source tree
'''
    
    for ext in pkg_config["extensions"]:
        content += f'        copy(self, "*{ext}", self.source_folder, self.package_folder, keep_path=True)\n'
    
    # Add a method to show what was packaged
    content += '''
    def package_info(self):
        # Optional: print what was packaged for debugging
        import os
        packaged_files = []
        for root, dirs, files in os.walk(self.package_folder):
            for file in files:
                rel_path = os.path.relpath(os.path.join(root, file), self.package_folder)
                packaged_files.append(rel_path)
        
        if packaged_files:
            self.output.info(f"Packaged {len(packaged_files)} files:")
            for f in sorted(packaged_files)[:10]:  # Show first 10 files
                self.output.info(f"  - {f}")
            if len(packaged_files) > 10:
                self.output.info(f"  ... and {len(packaged_files) - 10} more files")
'''
   
    with open("conanfile_upload.py", 'w') as f:
        f.write(content)
 
def generate_upload_conanfile_old(pkg_config: Dict):
    """Generate conanfile that packages from parent directory with custom source"""
    content = f'''from conan import ConanFile
from conan.tools.files import copy
import os
import shutil
 
class {pkg_config["name"].capitalize()}Conan(ConanFile):
    name = "{pkg_config["name"]}"
    version = "{pkg_config["version"]}"

    ##
    # settings = "os", "compiler", "build_type", "arch"
    # options = {{"shared": [True, False]}}
    # default_options = {{"shared": True}}
    ##
    
    # We'll handle source export manually
    
    def export_sources(self):
        # Define the path to the source folder (one level up from conan folder)
        source_folder = os.path.abspath(os.path.join(self.recipe_folder, "..", "{pkg_config["source_path"]}"))

        # Check if source folder exists
        if os.path.isdir(source_folder):
            # Copy the entire source folder contents to export_sources_folder
            for item in os.listdir(source_folder):
                source_path = os.path.join(source_folder, item)
                dest_path = os.path.join(self.export_sources_folder, item)

                try:
                    if os.path.isdir(source_path):
                        shutil.copytree(source_path, dest_path)
                    else:
                        shutil.copy2(source_path, dest_path)
                except Exception as e:
                    self.output.info(f"Warning: Could not copy {{item}}: {{e}}")
        else:
            self.output.info("Warning: 'source' folder not found.")
   
    def package(self):
        # Package files with specified extensions from the entire source tree
        package_folder = os.path.join(self.package_folder, "{pkg_config["source_path"]}")
'''
    
    for ext in pkg_config["extensions"]:
        content += f'        copy(self, "*{ext}", self.source_folder, package_folder, keep_path=True)\n'
    
    # Add a method to show what was packaged
    content += '''
    def package_info(self):
        # Optional: print what was packaged for debugging
        import os
        packaged_files = []
        for root, dirs, files in os.walk(self.package_folder):
            for file in files:
                rel_path = os.path.relpath(os.path.join(root, file), self.package_folder)
                packaged_files.append(rel_path)
        
        if packaged_files:
            self.output.info(f"Packaged {len(packaged_files)} files:")
            for f in sorted(packaged_files)[:10]:  # Show first 10 files
                self.output.info(f"  - {f}")
            if len(packaged_files) > 10:
                self.output.info(f"  ... and {len(packaged_files) - 10} more files")
'''
   
    with open("conanfile_upload.py", 'w') as f:
        f.write(content)

def generate_upload_conanfile(pkg_config: Dict):
    """Generate conanfile that packages from parent directory with custom source"""
    content = f'''from conan import ConanFile
from conan.tools.files import copy
import os
import shutil
 
class {pkg_config["name"].capitalize()}Conan(ConanFile):
    name = "{pkg_config["name"]}"
    version = "{pkg_config["version"]}"

    ##
    # settings = "os", "compiler", "build_type", "arch"
    # options = {{"shared": [True, False]}}
    # default_options = {{"shared": True}}
    ##
    
    # We'll handle source export manually
    
    def export_sources(self):
        # Handle both single source path (string) and multiple source paths (list)
        source_paths = {repr(pkg_config["source_path"])}
        if isinstance(source_paths, str):
            source_paths = [source_paths]
        
        for source_path in source_paths:
            # Define the path to the source folder (one level up from conan folder)
            source_folder = os.path.abspath(os.path.join(self.recipe_folder, "..", source_path))

            # Check if source folder exists
            if os.path.isdir(source_folder):
                # Create destination folder in export_sources_folder
                dest_base = os.path.join(self.export_sources_folder, source_path)
                os.makedirs(dest_base, exist_ok=True)
                
                # Copy the entire source folder contents to export_sources_folder
                for item in os.listdir(source_folder):
                    source_item_path = os.path.join(source_folder, item)
                    dest_item_path = os.path.join(dest_base, item)

                    try:
                        if os.path.isdir(source_item_path):
                            shutil.copytree(source_item_path, dest_item_path)
                        else:
                            shutil.copy2(source_item_path, dest_item_path)
                    except Exception as e:
                        self.output.info(f"Warning: Could not copy {{item}} from {{source_path}}: {{e}}")
            else:
                self.output.info(f"Warning: '{{source_path}}' folder not found.")
   
    def package(self):
        # Handle both single source path (string) and multiple source paths (list)
        source_paths = {repr(pkg_config["source_path"])}
        if isinstance(source_paths, str):
            source_paths = [source_paths]
        
        # Package files with specified extensions from all source trees
        for source_path in source_paths:
            source_folder = os.path.join(self.source_folder, source_path)
            package_folder = os.path.join(self.package_folder, source_path)
'''
    
    for ext in pkg_config["extensions"]:
        content += f'            copy(self, "*{ext}", source_folder, package_folder, keep_path=True)\n'
    
    # Add a method to show what was packaged
    content += '''
    def package_info(self):
        # Optional: print what was packaged for debugging
        import os
        packaged_files = []
        for root, dirs, files in os.walk(self.package_folder):
            for file in files:
                rel_path = os.path.relpath(os.path.join(root, file), self.package_folder)
                packaged_files.append(rel_path)
        
        if packaged_files:
            self.output.info(f"Packaged {len(packaged_files)} files:")
            for f in sorted(packaged_files)[:10]:  # Show first 10 files
                self.output.info(f"  - {f}")
            if len(packaged_files) > 10:
                self.output.info(f"  ... and {len(packaged_files) - 10} more files")
'''
   
    with open("conanfile_upload.py", 'w') as f:
        f.write(content)

def generate_download_conanfile(packages: List[Dict], output_file: str = "conanfile_download.py"):
    """Generate conanfile for downloading multiple packages"""
    content = '''from conan import ConanFile
from conan.tools.files import copy
 
class ConsumerConan(ConanFile):
    def requirements(self):
'''
   
    # Add all package requirements
    for pkg in packages:
        ref = f"{pkg['name']}/{pkg['version']}@{pkg['user']}/{pkg['channel']}"
        content += f'        self.requires("{ref}")\n'
   
    content += '''
    def generate(self):
        for dep in self.dependencies.values():
'''
   
    # Add copy commands for all extensions from all packages
    all_extensions = set()
    for pkg in packages:
        all_extensions.update(pkg["extensions"])
   
    for ext in all_extensions:
        content += f'            copy(self, "*{ext}", dep.package_folder, self.folders.generators, keep_path=True)\n'
   
    with open(output_file, 'w') as f:
        f.write(content)
 
 
def generate_individual_download_conanfiles(packages: List[Dict]):
    """Generate separate conanfiles for each package"""
    conanfiles = []
   
    for i, pkg in enumerate(packages):
        filename = f"conanfile_download_{i+1}.py"
        ref = f"{pkg['name']}/{pkg['version']}@{pkg['user']}/{pkg['channel']}"
       
        content = f'''from conan import ConanFile
from conan.tools.files import copy
 
class Consumer{pkg["name"].capitalize()}Conan(ConanFile):
    def requirements(self):
        self.requires("{ref}")
   
    def generate(self):
        for dep in self.dependencies.values():
'''
       
        for ext in pkg["extensions"]:
            content += f'            copy(self, "*{ext}", dep.package_folder, self.folders.generators, keep_path=True)\n'
       
        with open(filename, 'w') as f:
            f.write(content)
       
        conanfiles.append({
            "filename": filename,
            "package": pkg,
            "ref": ref
        })
   
    return conanfiles
 
 
@click.group()
def cli():
    """Conan 2.0 Package CLI - Packages from parent directory"""
    pass
 
 
@cli.command()
@click.option('-c', '--config', default='config.json')
@click.option('-r', '--remote')
@click.option('-s', '--skip-upload', is_flag=True)
def create(config, remote, skip_upload):
    """Create and upload package from parent directory"""

    # Ensure we're in the conan folder
    if not os.path.exists('runConan.py'):
        click.secho("Error: This command should be run from the conan folder!", fg='red')
        sys.exit(1)

    # Check if parent directory exists
    parent_dir = Path("..").resolve()
    if not parent_dir.exists():
        click.secho("Error: Parent directory not found!", fg='red')
        sys.exit(1)

    cfg = load_config(config)
    client = ConanClient()

    # Ensure Conan profile exists before proceeding
    click.secho("\nChecking Conan profile...", fg='cyan')
    if not client.ensure_profile():
        raise click.ClickException("Cannot proceed without a valid Conan profile")
   
    # Handle single package (first package in list)
    pkg = cfg["packages"][0]
    ref = f"{pkg['name']}/{pkg['version']}@{pkg['user']}/{pkg['channel']}"
    pkg_remote = remote or pkg.get("remote")
   
    if pkg_remote:
        results = client.search(ref, pkg_remote)
        if ref == results:
            click.secho(f"Package {ref} exists in {pkg_remote}!", fg='yellow')
    
    # Handle both single source path (string) and multiple source paths (list)
    source_paths = pkg["source_path"]
    if isinstance(source_paths, str):
        source_paths = [source_paths]
    
    # Show what will be packaged
    click.secho(f"Packaging from parent directory: {parent_dir}", fg='cyan')
    click.secho(f"Source paths: {', '.join(source_paths)}", fg='cyan')
    click.secho(f"Extensions to include: {', '.join(pkg['extensions'])}", fg='cyan')
    
    # Count files that will be packaged
    total_files = 0
    for source_path in source_paths:
        if source_path == '*':
            source_dir = parent_dir
            exclude_conan = True
        else:
            source_dir = parent_dir / source_path
            exclude_conan = False
            
        if not source_dir.exists():
            click.secho(f"Warning: Source path {source_path} not found!", fg='yellow')
            continue
            
        click.secho(f"Checking source path: {source_path}", fg='blue')
        
        for ext in pkg['extensions']:
            files = list(source_dir.rglob(f"*{ext}"))
            # Exclude files in conan subfolder only for '*' path
            if exclude_conan:
                files = [f for f in files if not str(f.relative_to(parent_dir)).startswith('conan')]
            total_files += len(files)
            if files:
                click.secho(f"  Found {len(files)} {ext} files", fg='green')
    
    click.secho(f"Total files to package: {total_files}", fg='blue')
    
    if total_files == 0:
        click.secho("Warning: No files found with specified extensions!", fg='yellow')
        if not click.confirm("Continue anyway?"):
            return
    
    click.secho("Using export_sources method...", fg='cyan')
    
    if isinstance(pkg["source_path"], list) or pkg["source_path"] != '*':
        generate_upload_conanfile(pkg)
    else:
        generate_default_upload_conanfile(pkg)
    
    try:
        client.create("conanfile_upload.py", pkg["name"], pkg["version"],
                     pkg["user"], pkg["channel"])
        click.secho("Package created successfully!", fg='green')
    except subprocess.CalledProcessError as e:
        click.secho("\nPackage creation failed!", fg='red', bold=True)
        click.secho(f"Error: {str(e)}", fg='red')
        click.secho("\nTROUBLESHOOTING SUGGESTIONS:", fg='yellow', bold=True)
        click.secho("1. Profile Issue: Run 'python runConan.py setup' to configure Conan", fg='yellow')
        click.secho("2. Network Issue: Check if you can reach the remote repository", fg='yellow')
        click.secho("3. Authentication: Verify your .netrc/_netrc file has correct credentials", fg='yellow')
        click.secho("4. Source Files: Verify source files exist using 'python runConan.py preview'", fg='yellow')
        raise click.ClickException(f"Failed to create package: {str(e)}")
    except Exception as e:
        click.secho("\nUnexpected error during package creation!", fg='red', bold=True)
        click.secho(f"Error: {str(e)}", fg='red')
        raise click.ClickException(f"Failed to create package: {str(e)}")
   
    if pkg_remote and not skip_upload:
        try:
            client.upload(ref, pkg_remote)
            click.secho("Uploaded successfully!", fg='green')
        except ValueError as e:
            raise click.ClickException(str(e))
        except Exception as e:
            raise click.ClickException(f"Upload failed: {str(e)}")
 
 
@cli.command()
@click.option('-c', '--config', default='config.json')
@click.option('-t', '--together', is_flag=True, help='Install all packages together using First JSON target path')
def install(config, together):
    """Install packages with individual target paths support"""
    cfg = load_config(config)
    client = ConanClient()

    # Ensure Conan profile exists before proceeding
    click.secho("Checking Conan profile...", fg='cyan')
    if not client.ensure_profile():
        raise click.ClickException("Cannot proceed without a valid Conan profile")

    packages = cfg["packages"]

    # global_target = output or cfg.get("target_path", "./output")
    global_target = packages[0]["target_path"] # "./output"

    successful_downloads = []
    failed_downloads = []
   
    build = "missing"
   
    if together:
        # Install all packages together - use global target path
        click.secho(f"Installing {len(packages)} packages together to {global_target}...", fg='cyan')
        Path(global_target).mkdir(parents=True, exist_ok=True)
       
        # Check cache for all packages
        for pkg in packages:
            ref = f"{pkg['name']}/{pkg['version']}@{pkg['user']}/{pkg['channel']}"
            remote = pkg["remote"]
            in_cache = client.cache_exists(ref)
            status = "✓" if in_cache else "✗"
            click.secho(f"  {pkg['name']}: {status} {'(cached)' if in_cache else '(download)'}", fg='green' if in_cache else 'yellow')
       
        try:
            generate_download_conanfile(packages)
            # Use the first remote for combined installation
            remote = packages[0]["remote"] if packages else None
            client.install("conanfile_download.py", remote, global_target, build)
           
            # Count total files
            all_extensions = set()
            for pkg in packages:
                all_extensions.update(pkg["extensions"])
           
            total = sum(len(list(Path(global_target).rglob(f"*{ext}"))) for ext in all_extensions)
            click.secho(f"✓ Installed {total} files to {global_target}", fg='green')
            successful_downloads = [f"All packages -> {global_target}"]
        except Exception as e:
            click.secho(f"✗ Combined installation failed: {str(e)}", fg='red')
            failed_downloads = [f"Combined installation: {str(e)}"]
    
    else:
        # Install each package separately with individual target paths
        click.secho(f"Installing {len(packages)} packages separately...", fg='cyan')
        conanfiles = generate_individual_download_conanfiles(packages)
       
        for cf in conanfiles:
            pkg = cf["package"]
            # Use package-specific target path if available, otherwise use global
            target = pkg.get("target_path", global_target)
            Path(target).mkdir(parents=True, exist_ok=True)
           
            click.secho(f"Installing {cf['ref']} to {target}...", fg='blue')
           
            # Check cache
            in_cache = client.cache_exists(cf["ref"])
            if in_cache:
                click.secho(f"  ✓ Using cached package", fg='green')
            elif in_cache:
                click.secho(f"  ✓ Cache found, force downloading", fg='yellow')
            else:
                click.secho(f"  ✗ Not in cache, downloading", fg='yellow')
           
            # Install with remote-specific settings if needed
            try:
                client.install(cf["filename"], pkg["remote"], target, build)
               
                # Count files for this package
                total = sum(len(list(Path(target).rglob(f"*{ext}"))) for ext in pkg["extensions"])
                click.secho(f"  ✓ Installed {total} files from {pkg['name']} to {target}", fg='green')
                successful_downloads.append(f"{pkg['name']} -> {target}")
               
            except Exception as e:
                click.secho(f"  ✗ Failed to install {pkg['name']}: {str(e)}", fg='red')
                failed_downloads.append(f"{pkg['name']}: {str(e)}")
   
    # Summary report
    click.echo("\n" + "="*50)
    click.secho("INSTALLATION SUMMARY", fg='cyan', bold=True)
    click.echo("="*50)
    
    if successful_downloads:
        click.secho(f"✓ SUCCESSFUL ({len(successful_downloads)}):", fg='green', bold=True)
        for success in successful_downloads:
            click.secho(f"  • {success}", fg='green')
    
    if failed_downloads:
        click.secho(f"\n✗ FAILED ({len(failed_downloads)}):", fg='red', bold=True)
        for failure in failed_downloads:
            click.secho(f"  • {failure}", fg='red')
            
    if failed_downloads:
        sys.exit(1)
 
 
@cli.command()
@click.option('-c', '--config', default='config.json')
def check(config):
    """Check package existence based on JSON"""
    cfg = load_config(config)
    client = ConanClient()
    packages = cfg["packages"]
   
    click.secho(f"Checking {len(packages)} package(s):", fg='cyan')
   
    for pkg in packages:
        ref = f"{pkg['name']}/{pkg['version']}@{pkg['user']}/{pkg['channel']}"
        remote = pkg.get("remote")
        target = pkg.get("target_path", cfg.get("target_path", "./output"))
       
        click.echo(f"\nPackage: {pkg['name']}")
        click.echo(f"  Target path: {target}")
       
        # Local check
        local = "✓" if client.cache_exists(ref) else "✗"
        click.echo(f"  Local cache: {local}")
       
        # Remote check
        if remote:
            remote_exists = client.search(ref, remote)
            remote_status = "✓" if ref == remote_exists else "✗"
            click.echo(f"  Remote {remote}: {remote_status}")


@cli.command()
def preview():
    """Preview what files will be packaged from parent directory"""
    
    # Ensure we're in the conan folder
    if not os.path.exists('runConan.py'):
        click.secho("Error: This command should be run from the conan folder!", fg='red')
        sys.exit(1)
    
    # Check config exists
    if not os.path.exists('config.json'):
        click.secho("Error: config.json not found! Run 'python runConan.py init' first.", fg='red')
        sys.exit(1)
    
    cfg = load_config('config.json')
    pkg = cfg["packages"][0]
    
    # Handle both single source path (string) and multiple source paths (list)
    source_paths = pkg["source_path"]
    if isinstance(source_paths, str):
        source_paths = [source_paths]

    parent_dir = Path("..").resolve()
    
    click.secho(f"Preview for package: {pkg['name']}", fg='cyan', bold=True)
    click.secho(f"Source paths: {', '.join(source_paths)}", fg='blue')
    click.secho(f"Extensions: {', '.join(pkg['extensions'])}", fg='blue')
    click.echo()
    
    total_files = 0
    for source_path in source_paths:
        if source_path == '*':
            source_dir = parent_dir
            exclude_conan = True
            click.secho(f"Source directory (all parent): {source_dir}", fg='blue')
        else:
            source_dir = parent_dir / source_path
            exclude_conan = False
            click.secho(f"Source directory ({source_path}): {source_dir}", fg='blue')
            
        if not source_dir.exists():
            click.secho(f"⚠️  Source path {source_path} not found!", fg='red')
            continue
        
        for ext in pkg['extensions']:
            files = list(source_dir.rglob(f"*{ext}"))
            # Exclude files in conan subfolder only for '*' path
            if exclude_conan:
                files = [f for f in files if not str(f.relative_to(parent_dir)).startswith('conan')]
            
            if files:
                click.secho(f"Files with extension {ext} in {source_path}:", fg='green', bold=True)
                for file in sorted(files):
                    if source_path == '*':
                        rel_path = file.relative_to(parent_dir)
                    else:
                        rel_path = file.relative_to(source_dir)
                    click.echo(f"  -> {rel_path}")
                total_files += len(files)
                click.echo()
    
    click.secho(f"Total files to be packaged: {total_files}", fg='yellow', bold=True)
    
    if total_files == 0:
        click.secho("⚠️  No files found with specified extensions!", fg='red')

 

##########################CLEAN WORKS
@cli.command()
@click.option('-p', '--pattern', default='*')
@click.option('-f', '--force', is_flag=True)
@click.option('-r', '--remote', help='Also remove from remote')
@click.option('-co', '--cache-only', is_flag=True, help='Only clean local cache')
@click.option('-ro', '--remote-only', is_flag=True, help='Only clean remote')
def clean(pattern, force, remote, cache_only, remote_only):
    """Clean packages from cache and/or remote"""
    client = ConanClient()
    
    if not force and not click.confirm(f"Remove pattern '{pattern}' from {'cache and remote' if remote and not cache_only and not remote_only else 'cache only' if cache_only else 'remote only' if remote_only else 'cache'}?"):
        return
    
    success_count = 0
    error_count = 0
    
    # Clean from local cache
    if not remote_only:
        try:
            click.secho(f"Cleaning local cache pattern: {pattern}", fg='yellow')
            client.run(["remove", pattern, "--confirm"], capture=False)
            click.secho("✓ Local cache cleaned successfully", fg='green')
            success_count += 1
        except Exception as e:
            click.secho(f"✗ Failed to clean local cache: {str(e)}", fg='red')
            error_count += 1
    
    # Clean from remote
    if remote and not cache_only:
        try:
            click.secho(f"Cleaning remote {remote} pattern: {pattern}", fg='yellow')
            client.run(["remove", pattern, "--remote", remote, "--confirm"], capture=False)
            click.secho(f"✓ Remote {remote} cleaned successfully", fg='green')
            success_count += 1
        except Exception as e:
            click.secho(f"✗ Failed to clean remote {remote}: {str(e)}", fg='red')
            error_count += 1
    
    # Summary
    click.echo(f"\nCleaning completed: {success_count} successful, {error_count} failed")


@cli.command()
@click.argument('package_name')
@click.argument('version')
@click.option('-p', '--revision-id', help='Recipe Revision (outer revision)')
@click.option('-u', '--user', default='marelli', help='User (default: marelli)')
@click.option('-ch', '--channel', default='stable', help='Channel (default: stable)')
@click.option('-r', '--remote', required=True, help='Remote repository name')
@click.option('-f', '--force', is_flag=True)
def remove_remote(package_name, version, revision_id, user, channel, remote, force):
    """Remove package from Artifactory remote based on Recipe Revision Id not Package Id"""
    
    ref = f"{package_name}/{version}@{user}/{channel}"
    if revision_id:
        ref += f"#{revision_id}"
    
    if not force and not click.confirm(f"Remove package {ref} from remote {remote}?"):
        return
    
    client = ConanClient()
    
    try:
        click.secho(f"Removing {ref} from remote {remote}...", fg='yellow')
        success = client.remove_from_remote(package_name, version, revision_id, user, channel, remote)
        
        if success:
            click.secho(f"✓ Successfully removed {ref} from {remote}", fg='green')
        else:
            click.secho(f"✗ Failed to remove {ref} from {remote}", fg='red')
            sys.exit(1)
            
    except Exception as e:
        click.secho(f"✗ Error removing package: {str(e)}", fg='red')
        sys.exit(1)
 
##########################INIT WORKS
@cli.command()
@click.argument('name', default='sample')
@click.argument('version', default='1.0')
@click.argument('source', default='*')
@click.option('-u', '--user', default='marelli')
@click.option('-ch', '--channel', default='stable')
@click.option('-r', '--remote', default='conancenter', help='Remote repository name')
@click.option('-e', '--ext', default='.c,.h', help='Comma-separated list(without any whitespace) of extension names to add: like .c,.h')
@click.option('-t', '--target', default='./output')
@click.option('-m', '--multiple', is_flag=True, help='Create config for multiple packages')
@click.option('-mp', '--multi-paths', help='Comma-separated list of source paths for single package: like path1,path2,path3')
def init(name, version, source, user, channel, remote, ext, target, multiple, multi_paths):
    """Create config.json with support for individual target paths and multiple source paths"""
    
    ext_names = []
    if ext:
        ext_names = [name.strip() for name in ext.split(',') if name.strip()]
    
    # Handle multiple source paths for single package
    if multi_paths:
        source_path_list = [path.strip() for path in multi_paths.split(',') if path.strip()]
    elif source != '*':
        source_path_list = source
    else:
        source_path_list = '*'
    
    if multiple:
        # Create template for multiple packages with individual target paths
        config = {
            "packages": [
                {
                    "name": name,
                    "version": version,
                    "user": user,
                    "channel": channel,
                    "remote": remote,
                    "source_path": source_path_list,
                    "extensions": ext_names,
                    "target_path": f"./{name}_output"
                },
                {
                    "name": "example2",
                    "version": "1.0",
                    "user": user,
                    "channel": channel,
                    "remote": remote,
                    "source_path": ["example2_path1", "example2_path2"],  # Example of multiple paths
                    "extensions": [".cpp", ".hpp"],
                    "target_path": "./example2_output"
                }
            ]
        }
        click.secho("Created config template for multiple packages with individual target paths", fg='blue')
    else:
        # Single package format
        config = {
            "packages": [
                {
                    "name": name,
                    "version": version,
                    "user": user,
                    "channel": channel,
                    "remote": remote,
                    "source_path": source_path_list,
                    "extensions": ext_names,
                    "target_path": target 
                }
            ]
        }
   
    with open('config.json', 'w') as f:
        json.dump(config, f, indent=2)
    
    if multi_paths:
        click.secho(f"Config created with multiple source paths: {', '.join(source_path_list)}", fg='green')
    else:
        click.secho("Config created with target path support!", fg='green')


# DO NOT TOUCH ANYTHING AFTER THIS LINE!!!
##########################SETUP WORKS
# Base URL for all Conan remotes
CONAN_BASE_URL = "https://preprodartifactory.marelli.com/artifactory/api/conan"
 
def build_remote_url(repo_name):
    """Build remote URL by appending repo name to base URL"""
    return f"{CONAN_BASE_URL}/{repo_name}"
 
def read_netrc_credentials(hostname):
    """Read credentials from .netrc file (Linux/Mac) or _netrc file (Windows)"""
    import netrc
    import os
    import platform
   
    # Choose netrc filename based on OS
    if platform.system() == "Windows":
        netrc_filename = "_netrc"
    else:
        netrc_filename = ".netrc"
   
    netrc_path = os.path.expanduser(f"~/{netrc_filename}")
    print(f"################ Looking for {netrc_path}")
   
    if not os.path.exists(netrc_path):
        click.secho(f"  {netrc_filename} file not found at {netrc_path}", fg='yellow')
        return None, None
   
    try:
        netrc_file = netrc.netrc(netrc_path)
        auth = netrc_file.authenticators(hostname)
        print("*" * 10)
        print(f"Auth for {hostname}: {auth}")
        if auth:
            username = auth[0]  # login
            password = auth[2]  # password
            click.secho(f"  Found credentials for {hostname} (user: {username})", fg='blue')
            return username, password
        else:
            click.secho(f"  No credentials found for {hostname} in {netrc_filename}", fg='yellow')
            return None, None
    except netrc.NetrcParseError as e:
        click.secho(f"  Error parsing {netrc_filename} file: {str(e)}", fg='red')
        return None, None
    except Exception as e:
        click.secho(f"  Error reading {netrc_filename} file: {str(e)}", fg='red')
        return None, None
 
def extract_hostname_from_url(url):
    """Extract hostname from URL for .netrc lookup"""
    from urllib.parse import urlparse
    parsed = urlparse(url)
    return parsed.netloc
 
@cli.command()
@click.option('-r', '--remote', help='Comma-separated list(without any whitespace) of repo names to add')
@click.option('-cr', '--custom-remote', multiple=True, help='Custom remote in format name=url')
def setup(remote, custom_remote):
    """Setup Conan for first time use"""
    client = ConanClient()
   
    click.secho("Setting up Conan environment...", fg='cyan')
   
    # Run conan profile detect
    click.secho("Auto-detecting system configuration...", fg='blue')
    try:
        client.run(["profile", "detect", "--force"], capture=False)
        click.secho("Profile detected and created", fg='green')
    except Exception as e:
        click.secho(f"Profile detection failed: {str(e)}", fg='red')
        return
   
    # Setup remotes
    click.secho("Setting up remotes...", fg='blue')
    
    # Parse comma-separated remotes
    repo_names = []
    if remote:
        repo_names = [name.strip() for name in remote.split(',') if name.strip()]
    else:
        # Default repo if none specified
        repo_names = ['conan_test']
    
    remotes_added = []
    
    # Add predefined remotes
    for repo_name in repo_names:
        remote_url = build_remote_url(repo_name)
        
        try:
            # Remove if exists
            try:
                client.run(["remote", "remove", repo_name], capture=True)
            except:
                pass
            
            # Add remote
            client.run(["remote", "add", repo_name, remote_url], capture=False)
            click.secho(f"Added remote: {repo_name}", fg='green')
            
            # SSL False
            client.run(["remote", "update", "--url", remote_url, "--insecure", repo_name], capture=False)
            
            remotes_added.append((repo_name, remote_url))
            
        except Exception as e:
            click.secho(f"Failed to add remote {repo_name}: {str(e)}", fg='red')
    
    # Add custom remotes
    for custom in custom_remote:
        if '=' not in custom:
            click.secho(f"Invalid custom remote format: {custom} (use name=url)", fg='red')
            continue
            
        remote_name, remote_url = custom.split('=', 1)
        try:
            # Remove if exists
            try:
                client.run(["remote", "remove", remote_name], capture=True)
            except:
                pass
            
            # Add remote
            client.run(["remote", "add", remote_name, remote_url], capture=False)
            click.secho(f"Added custom remote: {remote_name}", fg='green')
            remotes_added.append((remote_name, remote_url))
            
        except Exception as e:
            click.secho(f"Failed to add custom remote {remote_name}: {str(e)}", fg='red')
    
    # Authentication step
    if remotes_added:
        click.secho("Authenticating with remotes using netrc credentials...", fg='blue')
        
        for remote_name, remote_url in remotes_added:
            hostname = extract_hostname_from_url(remote_url)
            print("//" * 10)
            print(f"Hostname: {hostname}")
            username, password = read_netrc_credentials(hostname)
            print(f"Hoaaaaaastname: {username, password}")
            
            if username and password:
                try:
                    client.run(["remote", "login", "-p", password, remote_name, username], capture=False)
                    click.secho(f"Authenticated with {remote_name} as {username}", fg='green')
                except Exception as e:
                    click.secho(f"Authentication failed for {remote_name}: {str(e)}", fg='red')
            else:
                click.secho(f"No credentials found in netrc for {hostname} ({remote_name})", fg='yellow')

    # Show final status
    click.secho("\nConan setup completed!", fg='cyan')
    click.secho("Current configuration:", fg='blue')
   
    try:
        click.secho(f"\nDefault profile:", fg='yellow')
        client.run(["profile", "show"], capture=False)
       
        click.secho(f"\nConfigured remotes:", fg='yellow')
        client.run(["remote", "list"], capture=False)
       
    except Exception as e:
        click.secho(f"Could not display configuration: {str(e)}", fg='red')
   
    # Show info
    click.secho(f"\nBase URL: {CONAN_BASE_URL}", fg='blue')
    click.echo("Repo names will be appended to create full URLs")
   
    click.secho(f"\nAuthentication info:", fg='blue')
    click.echo("Add credentials to netrc file (.netrc on Linux/Mac, _netrc on Windows):")
    click.echo("machine preprodartifactory.marelli.com")
    click.echo("login <username>")
    click.echo("password <password>")
   
    click.secho(f"\nNext steps:", fg='green')
    click.echo("1. Create a config.json file: python runConan.py init")
    click.echo("2. Create your first package: python runConan.py create")
    click.echo("3. Install packages: python runConan.py install")
##########################

# EXPERIMENTAL AFTER THIS LINE!!!
##########################
import click
import json
import subprocess
import sys
from typing import Dict, Set, Tuple
from datetime import datetime

def run_conan_list(pattern: str, remote: str = None) -> Dict:
    """Run conan list command and return parsed JSON."""
    cmd = ["conan", "list", pattern, "--format=json"]
    if remote:
        cmd.extend(["-r", remote])
    else:
        cmd.append("-c")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return json.loads(result.stdout)
    except subprocess.CalledProcessError as e:
        click.echo(f"Error running conan command: {e.stderr}", err=True)
        sys.exit(1)
    except json.JSONDecodeError:
        click.echo("Error parsing JSON output from conan", err=True)
        sys.exit(1)

def extract_packages(data: Dict) -> Set[Tuple[str, str, str]]:
    """Extract package names and versions from conan list output."""
    packages = set()
    
    for repo_name, repo_data in data.items():
        for pkg_ref, pkg_data in repo_data.items():
            try:
                # Parse package reference (e.g., "sample/1.0@ab/stable" or "zlib/1.3.1")
                if '@' in pkg_ref:
                    # Old format: name/version@user/channel
                    name_version, user_channel = pkg_ref.split('@', 1)
                    if '/' in name_version:
                        name, version = name_version.split('/', 1)
                    else:
                        name, version = name_version, "unknown"
                    packages.add((name, version, user_channel))
                elif '/' in pkg_ref:
                    # New format: name/version
                    name, version = pkg_ref.split('/', 1)
                    packages.add((name, version, ''))
                else:
                    # Single name without version
                    packages.add((pkg_ref, "unknown", ''))
            except Exception as e:
                click.echo(f"Warning: Could not parse package reference '{pkg_ref}': {e}", err=True)
                continue
    
    return packages

def get_package_details(data: Dict) -> Dict:
    """Extract detailed package information including IDs and revisions."""
    details = {}
    
    for repo_name, repo_data in data.items():
        for pkg_ref, pkg_data in repo_data.items():
            revisions = pkg_data.get('revisions', {})
            pkg_details = []
            
            for rev_id, rev_data in revisions.items():
                rev_timestamp = rev_data.get('timestamp', 0)
                rev_time = datetime.fromtimestamp(rev_timestamp).strftime('%Y-%m-%d %H:%M:%S') if rev_timestamp else 'Unknown'
                
                packages = rev_data.get('packages', {})
                for pkg_id, pkg_info in packages.items():
                    pkg_revisions = pkg_info.get('revisions', {})
                    for pkg_rev_id, pkg_rev_data in pkg_revisions.items():
                        pkg_timestamp = pkg_rev_data.get('timestamp', 0)
                        pkg_time = datetime.fromtimestamp(pkg_timestamp).strftime('%Y-%m-%d %H:%M:%S') if pkg_timestamp else 'Unknown'
                        
                        settings = pkg_info.get('info', {}).get('settings', {})
                        options = pkg_info.get('info', {}).get('options', {})
                        
                        pkg_details.append({
                            'recipe_revision': rev_id,
                            'recipe_time': rev_time,
                            'package_id': pkg_id,
                            'package_revision': pkg_rev_id,
                            'package_time': pkg_time,
                            'settings': settings,
                            'options': options
                        })
                
                # If no packages, still show recipe info
                if not packages:
                    pkg_details.append({
                        'recipe_revision': rev_id,
                        'recipe_time': rev_time,
                        'package_id': 'N/A',
                        'package_revision': 'N/A',
                        'package_time': 'N/A',
                        'settings': {},
                        'options': {}
                    })
            
            details[pkg_ref] = pkg_details
    
    return details

def format_package(pkg_tuple: Tuple[str, str, str]) -> str:
    """Format package tuple back to string representation."""
    name, version, user_channel = pkg_tuple
    if user_channel:
        return f"{name}/{version}@{user_channel}"
    return f"{name}/{version}"

@cli.command()
@click.argument('pattern', default='*#*:*#*')
@click.option('-r', '--remote', help='Remote repository name')
def check_package(pattern: str, remote: str):
    """
    Check consistency between local cache and remote Conan packages.
    
    PATTERN: Package pattern (default: *#*:*#*)
    Examples:
    - *#*:*#* (all packages)
    - zlib/1.3.1#*:*#*
    - sample/1.0@ab/stable#*:*#*
    """
    if not remote:
        click.echo("Error: Remote repository name is required (-r/--remote)", err=True)
        sys.exit(1)
    
    click.echo(f"Checking consistency for pattern: {pattern}")
    click.echo(f"Remote repository: {remote}")
    click.echo("-" * 50)
    
    # Get local cache packages
    click.echo("Fetching local cache packages...")
    local_data = run_conan_list(pattern)
    local_packages = extract_packages(local_data)
    
    # Get remote packages
    click.echo("Fetching remote packages...")
    remote_data = run_conan_list(pattern, remote)
    remote_packages = extract_packages(remote_data)
    
    # Compare packages
    only_local = local_packages - remote_packages
    only_remote = remote_packages - local_packages
    common = local_packages & remote_packages
    
    # Display results
    click.echo(f"\n-> Summary:")
    click.echo(f"  Local packages: {len(local_packages)}")
    click.echo(f"  Remote packages: {len(remote_packages)}")
    click.echo(f"  Common packages: {len(common)}")
    
    if only_local:
        click.echo(f"\n-> Only in local cache ({len(only_local)}):")
        for pkg in sorted(only_local):
            click.echo(f"  - {format_package(pkg)}")
    
    if only_remote:
        click.echo(f"\n-> Only in remote ({len(only_remote)}):")
        for pkg in sorted(only_remote):
            click.echo(f"  - {format_package(pkg)}")
    
    if common:
        click.echo(f"\n-> Common packages ({len(common)}):")
        for pkg in sorted(common):
            click.echo(f"  - {format_package(pkg)}")
    
    # Consistency status
    is_consistent = not only_local and not only_remote
    status = "- CONSISTENT" if is_consistent else "- INCONSISTENT"
    click.echo(f"\n-> Status: {status}")
    
    if not is_consistent:
        sys.exit(1)

@cli.command()
@click.argument('pattern', default='*#*:*#*')
@click.option('-r', '--remote', help='Remote repository name (if not specified, shows local cache)')
@click.option('-s', '--settings', is_flag=True, help='Show package settings and options')
def details(pattern: str, remote: str, settings: bool):
    """
    Show detailed package information including IDs, revisions, and timestamps.
    
    PATTERN: Package pattern (default: *#*:*#*)
    """
    source_type = "remote" if remote else "local cache"
    click.echo(f"Package details for pattern: {pattern}")
    click.echo(f"Source: {source_type}" + (f" ({remote})" if remote else ""))
    click.echo("-" * 60)
    
    # Get package data
    data = run_conan_list(pattern, remote)
    details_data = get_package_details(data)
    
    if not details_data:
        click.echo("No packages found matching the pattern.")
        return
    
    for pkg_ref, pkg_list in details_data.items():
        click.echo(f"\n-> {pkg_ref}")
        click.echo("=" * (len(pkg_ref) + 4))
        
        for i, pkg_detail in enumerate(pkg_list, 1):
            click.echo(f"\n  [{i}] Recipe Revision: {pkg_detail['recipe_revision']}")
            click.echo(f"      Recipe Time: {pkg_detail['recipe_time']}")
            click.echo(f"      Package ID: {pkg_detail['package_id']}")
            click.echo(f"      Package Revision: {pkg_detail['package_revision']}")
            click.echo(f"      Package Time: {pkg_detail['package_time']}")
            
            if settings and (pkg_detail['settings'] or pkg_detail['options']):
                if pkg_detail['settings']:
                    click.echo("      Settings:")
                    for key, value in pkg_detail['settings'].items():
                        click.echo(f"        {key}: {value}")
                
                if pkg_detail['options']:
                    click.echo("      Options:")
                    for key, value in pkg_detail['options'].items():
                        click.echo(f"        {key}: {value}")
##########################


def main():
    """Entry point for the CLI."""
    cli()

if __name__ == '__main__':
    main()