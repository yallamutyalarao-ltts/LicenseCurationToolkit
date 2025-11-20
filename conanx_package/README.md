# Conan 2.0 Package CLI

A comprehensive command-line interface tool for automating Conan 2.0 package creation, upload, download, and management operations with integrated Marelli Artifactory support. This tool simplifies the process of managing multiple packages with configurable file extensions and enterprise authentication.

## Features

- **Initial Setup**: Auto-configure Conan with profile detection and remote setup
- **Package Creation**: Automatically generate conanfiles and create packages
- **Upload Management**: Upload packages to specified remotes with confirmation
- **Package Installation**: Download and install packages individually or in batches
- **Cache Management**: Check package existence in local cache and remotes
- **Configuration Generation**: Initialize configuration files with templates
- **Multi-Package Support**: Handle both single and multiple package configurations
- **Enterprise Authentication**: Integrated netrc-based authentication for Marelli Artifactory
- **Cross-Platform**: Works on Windows, Linux

## Installation

### From PyPI (Recommended)

```bash
pip install conanx
```

### From Source

```bash
git clone https://github.com/yourusername/conanx.git
cd conanx
pip install -e .
```

### Requirements

- Python 3.10 or higher (Python 3.12.0 Recommended)
- The package automatically installs required dependencies:
  - `conan>=2.0.0`
  - `click>=8.0.0`
  - `requests>=2.25.0`

This CLI was developed and tested with `conan==2.19.1` and `click==8.1.8`.

## Quick Start

1. **Initial Setup** (first-time only):
```bash
conanx setup --remote conan_test,conan_prod
```

2. **Create Configuration JSON**:
```bash
conanx init mypackage 1.0.0 ainv --remote conan_test
```

3. **Create and Upload Package**:
```bash
conanx create
```

4. **Install Packages**:
```bash
conanx install
```

## Configuration

The tool uses a JSON configuration file (default: `config.json`) to define package specifications.

### Configuration Format

- Single component format:
  - To create and upload package.
  - To install a single package.

```json
{
  "packages": [
    {
      "name": "ab",
      "version": "1.0",
      "user": "marelli",
      "channel": "stable",
      "remote": "conancenter",
      "source_path": "ainv_d_prj",
      "extensions": [
        ".c",
        ".h"
      ],
      "target_path": "./output"
    }
  ]
}
```
- Multiple component format:
  - To install multiple packages.

```json
{
  "packages": [
    {
      "name": "ab",
      "version": "1.0",
      "user": "marelli",
      "channel": "stable",
      "remote": "conancenter",
      "source_path": "ainv_d_prj",
      "extensions": [
        ".c",
        ".h"
      ],
      "target_path": "./ab_output"
    },
    {
      "name": "example2",
      "version": "1.0",
      "user": "marelli",
      "channel": "stable",
      "remote": "conancenter",
      "source_path": "example2_path",
      "extensions": [
        ".cpp",
        ".hpp"
      ],
      "target_path": "./example2_output"
    }
  ]
}
```

**N.B.:**

- Use `"source_path": "*",` to take all files in the parent folder except the `conan CLI folder` to export in time of creating the package.

- Use `"extensions": ["*"],` to include every single file. It will add the `conaninfo.txt` and `conanmanifest.txt` in the target install folder in time of installation.

### Configuration Fields

- **name**: Package name (required)
- **version**: Package version (required)
- **user**: Conan user namespace (required)
- **channel**: Conan channel (required)
- **extensions**: List of file extensions to include in the package (required)
- **remote**: Conan remote repository name (required for upload)
- **source_path:**: Source directory to export in time of creating the package
- **target_path**: Output directory for downloaded packages (optional, default: "./output")

## Authentication Setup

The tool uses netrc files for authentication with Marelli Artifactory.

### Creating Netrc File

- **On Windows**: Create `_netrc` file in your home directory

- **On Linux/Mac**: Create `.netrc` file in your home directory

```bash
machine artifactory.marelli.com
login <your_username>
password <your_password>
```

**File Permissions** (Linux/Mac only):
```bash
chmod 600 ~/.netrc
```

---
## Commands Reference

- **`setup`, `init`, `create`, `install`, `clean` - can be used for automated pipeline scripts without any input prompts.**
- **`check`, `check-package`, `details`, `preview`, `remove-remote` - can be used for direct use as a wrapper CLI functions.**

### `setup` - Initial Conan Configuration

Configure Conan for first-time use with profile detection and remote setup.

```bash
conanx setup [OPTIONS]
```

**Options:**
- `-r, --remote`: Comma-separated list of repo names (no whitespace)
- `-cr, --custom-remote`: Custom remote in format name=url (can be used multiple times)

**Examples:**

```bash
# Basic setup with default conan_test repo
conanx setup

# Add multiple repositories
conanx setup --remote conan_test,conan_prod,conan_dev

# Add custom repository
conanx setup --custom-remote external=https://external.repo.com
```

**What it does:**
1. Runs `conan profile detect --force` to auto-configure system profile
2. Adds specified repositories with base URL + repo name
3. Configures SSL settings (`--insecure` flag for enterprise environments)
4. Authenticates with repositories using netrc credentials
5. Shows final configuration status
6. Can be verified maually by `conan remote list`

### Remote Repository Configuration

The tool automatically constructs repository URLs using:

**Base URL /`{base_url}`**: 
`https://artifactory.marelli.com/artifactory/api/conan`
or, `https://preprodartifactory.marelli.com/artifactory/api/conan`

**Repository URL Format**: `{base_url}/{repo_name}`

### Example Repository URLs:
- `conan_test` → `https://artifactory.marelli.com/artifactory/api/conan/conan_test`
- `conan_prod` → `https://artifactory.marelli.com/artifactory/api/conan/conan_prod`

### `init` - Create Configuration

Generate a configuration file template with specified parameters.

```bash
conanx init [OPTIONS] [NAME] [VERSION] [SOURCE]
```

**Arguments:**
- `NAME`: Package name (default: `sample`)
- `VERSION`: Package version (default: `1.0`)
- `SOURCE`: Package Source Folder. Example: ainv_d_prj (default: `*` for taking every file/folder from the parent directory of `conan CLI folder` except that folder itself)

**Options:**
- `-u, --user`: User namespace (default: `marelli`)
- `-ch, --channel`: Channel name (default: `stable`)
- `-r, --remote`: Remote repository name (default: `conancenter`)
- `-e, --ext`: Comma-separated File extensions list(without any whitespace) of extension names to add: like .c,.h
- `-t, --target`: Target output directory (default: `./output`)
- `-m, --multiple`: Create config template for multiple packages
- `-mp, --multi-paths`: Comma-separated list (without any whitespace) of source paths for single package: like path1,path2,path3
  - `-mp` will overwrite `[SOURCE]` argument source path.

**Examples:**

```bash
# Create basic config
conanx init

# Create config for specific package
conanx init mypackage 2.0 ainv_d_prj -u company -ch testing -r conan_prod

# Create config with custom extensions
conanx init -e .hpp,.cpp,.h -r conan_test

# Create multiple packages template
conanx init --multiple

# Create package with multiple source paths
conanx init sample 1.0 -mp ainv_d_prj,binv_d_prj
```

### `create` - Create and Upload Package

Create a package using configuration and optionally upload it to a remote.

```bash
conanx create [OPTIONS]
```

**Options:**
- `-c, --config`: Configuration file path (default: `config.json`)
- `-r, --remote`: Override remote from config
- `-s, --skip-upload`: Create package but skip upload step

**Examples:**

```bash
# Basic package creation
conanx create

# Use custom config file
conanx create -c myconfig.json

# Create without uploading - For testing from Cache
conanx create --skip-upload
```

### `install` - Install Packages

Download and install packages from remotes to a local directory.

```bash
conanx install [OPTIONS]
```

**Options:**
- `-c, --config`: Configuration file path (default: `config.json`)
- `-t, --together`: Install all packages together using First JSON target path

**Examples:**

```bash
# Install packages separately with detailed feedback from default config.json
conanx install

# Install all packages together
conanx install --together

# Install with custom config.json
conanx install -c /path/to/custom/config.json
```

---
---

### Minimal `conanfile.py` Structure Examples

#### conanfile_upload.py

- Direct use:
  - `conan create conanfile_upload.py`
  - `conan upload "*" --remote=<remote_conan_repo> --confirm`

```python
from conan import ConanFile
from conan.tools.files import copy
 
class ExampleConan(ConanFile):
    name = "example"
    version = "1.0"
    exports_sources = "**"
   
    def package(self):
        copy(self, "*.cpp", self.source_folder, self.package_folder)
        copy(self, "*.hpp", self.source_folder, self.package_folder)

```
#### conanfile_download.py

- Direct use:
  - `conan install conanfile_download.py -r <remote_conan_repo> --output-folder=<target_build_folder> --envs-generation=false --build=missing`

```python
from conan import ConanFile
from conan.tools.files import copy
 
class ConsumerConan(ConanFile):
    def requirements(self):
        self.requires("example/2.0@marelli/stable")
        self.requires("sample/1.0@marelli/stable")

    def generate(self):
        for dep in self.dependencies.values():
            copy(self, "*.cpp", dep.package_folder, self.folders.generators)
            copy(self, "*.h", dep.package_folder, self.folders.generators)
            copy(self, "*.c", dep.package_folder, self.folders.generators)
```
**N.B.:** To get rid of the folder structure i.e. to only download/upload the files without the folders, modify the `copy` function by adding the parameter `keep_path = False` as by default it is set to True:
```python
(function) def copy(
    conanfile: Any,
    pattern: Any,
    src: Any,
    dst: Any,
    keep_path: bool = True,
    excludes: Any | None = None,
    ignore_case: bool = True,
    overwrite_equal: bool = False
) -> list
```

**N.B.: `conanfile_upload.py` is modified for our current use cases.**

- **Default Case:** *( generate_default_upload_conanfile(pkg_config: Dict))*
  - To get the parent directory (one level up from conan folder)
  - To copy all files from parent directory to export folder, excluding conan folder

```python
from conan import ConanFile
from conan.tools.files import copy
import os
import shutil
 
class SampleConan(ConanFile):
    name = "sample"
    version = "1.0"

    ## These parameters can be introduced later
    # settings = "os", "compiler", "build_type", "arch"
    # options = {"shared": [True, False]}
    # default_options = {"shared": True}
    ##
    
    # Handle source export manually
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
                self.output.info(f"Warning: Could not copy {item}: {e}")
   
    def package(self):
        # Package files with specified extensions from the entire source tree
        copy(self, "*.c", self.source_folder, self.package_folder, keep_path=True)
        copy(self, "*.h", self.source_folder, self.package_folder, keep_path=True)

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


```

- **Specific Source Case 1: Single Source** *( generate_upload_conanfile(pkg_config: Dict))*

  - To get the specific source folder from parent directory (one level up from conan folder)

```python
from conan import ConanFile
from conan.tools.files import copy
import os
import shutil
 
class SpecificConan(ConanFile):
    name = "ab"
    version = "1.0"

    ## These parameters can be introduced later
    # settings = "os", "compiler", "build_type", "arch"
    # options = {"shared": [True, False]}
    # default_options = {"shared": True}
    ##
    
    # Handle source export manually
    
    def export_sources(self):
        # Define the path to the source folder (one level up from conan folder)
        source_folder = os.path.abspath(os.path.join(self.recipe_folder, "..", "ainv_d_prj"))

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
                    self.output.info(f"Warning: Could not copy {item}: {e}")
        else:
            self.output.info("Warning: 'source' folder not found.")
   
    def package(self):
        # Package files with specified extensions from the entire source tree
        copy(self, "*.c", self.source_folder, self.package_folder, keep_path=True)
        copy(self, "*.h", self.source_folder, self.package_folder, keep_path=True)

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

```
- **Specific Source Case 2: Single and Multiple Source** *( generate_upload_conanfile(pkg_config: Dict))*

  - To get the specific source folder(s) from **source_path** list from parent directory (one level up from conan folder)

```python
from conan import ConanFile
from conan.tools.files import copy
import os
import shutil
 
class ArkConan(ConanFile):
    name = "ark"
    version = "1.0"

    # Handle source export manually
    def export_sources(self):
        # Handle both single source path (string) and multiple source paths (list)
        source_paths = ['ainv_d_prj', 'binv_d_prj']
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
                        self.output.info(f"Warning: Could not copy {item} from {source_path}: {e}")
            else:
                self.output.info(f"Warning: '{source_path}' folder not found.")
   
    def package(self):
        # Handle both single source path (string) and multiple source paths (list)
        source_paths = ['ainv_d_prj', 'binv_d_prj']
        if isinstance(source_paths, str):
            source_paths = [source_paths]
        
        # Package files with specified extensions from all source trees
        for source_path in source_paths:
            source_folder = os.path.join(self.source_folder, source_path)
            package_folder = os.path.join(self.package_folder, source_path)
            copy(self, "*.c", source_folder, package_folder, keep_path=True)
            copy(self, "*.h", source_folder, package_folder, keep_path=True)

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

```

---
---

### `check` - Check Package Existence

Verify if packages from JSON exist in local cache and remote repositories.

```bash
conanx check [OPTIONS]
```

**Options:**
- `-c, --config`: Configuration file path (default: `config.json`)

**Example Output:**
```
Checking 2 package(s):

Package: mylib
  Local cache: ✓
  Remote conan_test: ✓

Package: otherlib
  Local cache: ✗
  Remote conan_prod: ✗
```

### `clean` - Clean Cache

Remove packages from the local Conan cache.

```bash
conanx clean [OPTIONS]
```

**Options:**
- `-p, --pattern`: Pattern to match packages (default: `*` for all)
- `-f, --force`: Skip confirmation prompt
- `-r, --remote`: Also remove from remote
- `-co, --cache-only`: Only clean local cache
- `-ro, --remote-only`: Only clean remote

**Examples:**

```bash
# Remove all packages (with confirmation)
conanx clean

# Remove specific pattern without confirmation
conanx clean -p "mylib/*" --force

# Remove specific version
conanx clean -p "mylib/1.0.0*"
```


### `preview` - Preview what files will be packaged from parent directory

Based on the config JSON data, it will review what files will be packaged from parent directory (Excluding the conan folder itself).

```bash
conanx preview [OPTIONS]
```

**Options:**
- `N/A`: Currently it will only take default `config.json` as argument

**Examples:**

```bash
# Preview what files will be packaged from parent directory
conanx preview
```

**Sample Output:**
```bash
Preview for package: sample
Source directory: C:\full\path\to\parent-directory
Extensions: .c, .h

Files with extension .c:
  -> parent-directory\folder1\a.c

Files with extension .h:
  -> parent-directory\folder2\b.h
```

### `remove-remote` - Remove package from Artifactory remote based on Recipe Revision Id not Package Id

Remove package from Artifactory remote based on Recipe Revision Id not Package Id.

```bash
conanx remove-remote [OPTIONS] PACKAGE_NAME VERSION
```

**Options:**

- `-p, --revision-id`: Recipe Revision (outer revision).
- `-u, --user`: User (default: marelli).
- `-ch, --channel`: Channel (default: stable).
- `-r, --remote`: Remote repository name  [required].
- `-f, --force`: Direct removal without prompt.

**Examples:**

```bash
# Preview what files will be packaged from parent directory
conanx remove-remote sample 1.0 -p {Recipe Revision ID from artifactory} -r conan_test
```

---
---
### Package Details:

- `conan list "*"` will show the pacakge list.
- The advanced version of this command can be used like the following way,
  -  `conan list "*#*:*#*" --format=json/html` (`-c, --cache` is by default considered to search in the local cache) to search in local cache.
  -   `conan list "*#*:*#*" -r "conan_test"/"*" --format=json/html --out-file={output filename}` to search in remotes.
  - Here pattern `"*#*:*#*"` is in the form `package_name/version@user/channel#recipe_revision:package_id#package_revision` (Recipe reference is `package_name/version@user/channel`)

```bash
conan list "*#*:*#*"
--------------------
# Sample Output for a single package in cache
Local Cache
  sample
    sample/1.0@marelli/stable
      revisions # Recipe Revision (RREV)
        609bd8a4f9a78ef3e3538f7d8e448fe1 (2025-08-28 03:53:25 UTC)
          packages # Package ID (PID)
            f69a5bcb55de7f8572a7ce385a38d55f76d9288d
              revisions # Package Revision (PREV)
                c9ac60e3eb1a1e9d58074b5ee673b3f4 (2025-08-28 03:53:25 UTC)
              info
                settings
                  arch: x86_64
                  build_type: Release
                  compiler: gcc
                  compiler.cppstd: gnu14
                  compiler.libcxx: libstdc++11
                  compiler.version: 6
                  os: Windows
                options
                  shared: True
```

### Brief Explanation: 

In Conan 2, A Conan package identity looks like:
`<name>/<version>@<user>/<channel>#<RREV>:<PackageID>#<PREV>`

This means:
`<name>/<version>@<user>/<channel>` recipe at revision `<RREV>`, Built with settings/options that hash into build configuration identity package ID `<PackageID>`, Resulting actual binary build at revision `<PREV>`


There are 3 different revision levels:

1. **Recipe Revision (RREV):** identifies a specific revision of the recipe (conanfile.py / conanfile.txt and its exported sources). It changes if you modify the recipe or its exported files.
So, sample/2.0@marelli/stable#RREV... uniquely identifies the recipe state.

2. **Package ID (PID):** derived from the recipe’s settings and options.
Example: arch=x86_64, compiler=gcc, build_type=Release, shared=True → results in a hash (da39a3...). If you change settings (e.g., build Debug instead of Release), Conan generates a different package ID.

3. **Package Revision (PREV):** a unique hash of the binary package contents built from that recipe + settings. If you rebuild the same package (same PID) but with different code or compiler flags, Conan generates a new PREV. 
So sample/2.0@marelli/stable#effc8d...:da39a3...#b42f50... fully identifies one concrete binary package.

---
---

### `check-package` - Check consistency between local cache and remote Conan packages.

Check consistency between local cache and remote Conan packages based on the provided package pattern
    
*PATTERN: Package pattern (default: *#*:*#*)*
Examples:
- `*#*:*#*` (all packages)
- zlib/1.3.1#*:*#*
- sample/1.0@ab/stable#*:*#*

```bash
conanx check-package [OPTIONS] [PATTERN]
```

**Options:**

- `-r, --remote`: Remote repository name.

**Examples:**

```bash
# Check consistency for Package pattern (default: *#*:*#*)
conanx check-package -r conan_test
```

### `details` - Show detailed package information including IDs, revisions, and timestamps.

Show detailed package information including IDs, revisions, timestamps, settings and options.
    
*PATTERN: Package pattern (default: *#*:*#*)*
Examples:
- `*#*:*#*` (all packages)
- zlib/1.3.1#*:*#*
- sample/1.0@ab/stable#*:*#*

```bash
conanx details [OPTIONS] [PATTERN]
```

**Options:**

- `-r, --remote`: Remote repository name (if not specified, shows local cache).
- `-s, --settings`: Show package settings and options.

**Examples:**

```bash
# Details for Package pattern (default: *#*:*#*)
conanx details

# Details for Package pattern from remote conan repo (default: *#*:*#*)
conanx details -r conan_test
```

**Sample Output:**

```bash
# Details for Package pattern (default: *#*:*#*)
Package details for pattern: *#*:*#*
Source: local cache
------------------------------------------------------------

-> ab/1.0@marelli/stable
=========================

  [1] Recipe Revision: 609bd8a4f9a78ef3e3538f7d8e448fe1
      Recipe Time: 2025-08-28 09:23:25
      Package ID: f69a5bcb55de7f8572a7ce385a38d55f76d9288d
      Package Revision: c9ac60e3eb1a1e9d58074b5ee673b3f4
      Package Time: 2025-08-28 09:23:25

  [2] Recipe Revision: 67d376e919eff92ccd2cb72d38b4a431
      Recipe Time: 2025-08-28 09:23:55
      Package ID: f69a5bcb55de7f8572a7ce385a38d55f76d9288d
      Package Revision: 45ae1151e291492e8302e8013de6f846
      Package Time: 2025-08-28 09:23:55

```

---

## Workflow Examples

### Complete First-Time Setup

```bash
# 1. Initial Conan setup
conanx setup --remote conan_test,conan_prod

# 2. Initialize project configuration
conanx init mylib 1.0.0 -u marelli -r conan_test -e .h,.cpp -r conan_test

# See what files will be packed # For Manual Use
conanx preview
# Check current status # For Manual Use
conanx check

# 3. Create and upload package
conanx create
```

Run the scripts from the conan repo directory not from root directory of the workspace (Package Folder).

### Development Workflow

```bash
# Check what's available
conanx check

# Install dependencies
conanx install 

# Create new version
conanx init mylib 1.1.0 -r conan_test

# Build and upload
conanx create
```

### Package Management

```bash
# Clean old versions
conanx clean -p "mylib/1.0.*"

# Reinstall specific packages from remote
conanx install -c production.json
```

## Additional Features

### SSL Configuration
- All remotes are automatically configured with `--insecure` flag for enterprise environments
- This bypasses SSL certificate verification for internal Artifactory instances

### Separate Installation Mode
When NOT using `--together` in time of `Install()`:
- Creates individual conanfiles for each package
- Provides detailed per-package feedback
- Shows cache status and file counts
- Continues with other packages if one fails

### Cross-Platform Authentication
- Automatically detects OS and uses appropriate netrc file
- Windows: `_netrc` in home directory
- Linux/Mac: `.netrc` in home directory

### Error Handling
- Comprehensive validation of configuration files
- Handling of network and authentication errors and detailed error messages with suggested solutions

## File Structure

### Initial Stage
```
project/
├── conan/                     # Conan Repo
│   └── runConan.py            # CLI script
│
├── other_files...
│
└── workspace/                 # Package Reference Directory/Cloned Repo
    ├── package1_files/
    └── package2_files/
```

### Generated Files inside "Conan Folder"

```
conan/
├── runConan.py                   # CLI script
├── config.json                   # Main configuration
├── conanfile_upload.py           # Generated for package creation
├── conanfile_download.py         # Generated for batch installation
├── conanfile_download_*.py       # Generated for separate installation
└── output/                       # Default install target directory
    ├── package1_files/
    └── package2_files/
```


## Core Components of the CLI Code:

### ConanClient Class

Wrapper class for Conan CLI operations:

- `create()`: Create packages from conanfiles
- `upload()`: Upload packages to remotes
- `install()`: Install packages locally
- `search()`: Search for packages in remotes
- `cache_exists()`: Check if package exists in local cache
- `run()`: Execute Conan commands with error handling

### Configuration Management

- `load_config()`: Load and validate JSON configuration
- Automatic conversion from legacy single to multiple package format
- Comprehensive field validation with detailed error messages

### Conanfile Generation

- `generate_upload_conanfile()`: Creates conanfiles for package upload
- `generate_download_conanfile()`: Creates consumer conanfiles for multiple packages
- `generate_individual_download_conanfiles()`: Creates separate conanfiles per package


## Troubleshooting

### Common Issues

**Profile Not Found Error:**
```
ERROR: The default build profile 'C:\Users\...\..conan2\profiles\default' doesn't exist.
```
**Solutions:**
1. **Automatic Fix**: The tool now automatically detects and creates the profile when running `create` or `install` commands
2. **Manual Fix**: Run `conanx setup` to configure Conan properly
3. **Direct Conan Command**: Run `conan profile detect --force` to create the default profile
4. **Verification**: Check if profile exists with `conan profile show`

**Authentication Failed:**
- Verify netrc file exists and has correct permissions (600 on Linux/Mac)
- Check hostname in netrc matches: `artifactory.marelli.com` or `preprodartifactory.marelli.com`
- Ensure credentials are correct
- On Windows: File should be named `_netrc` in your home directory
- On Linux/Mac: File should be named `.netrc` in your home directory

**Package Not Found:**
- Use normal `conan list "*"` to see the packages in the cache
- Use `check` command to verify package availability
- Check remote configuration with `conan remote list`
- Verify repository name is correct

**Network/Remote Connection Issues:**
```
ERROR: HTTPSConnectionPool(host='...', port=443): Max retries exceeded...
```
**Solutions:**
1. Check your network connectivity and VPN connection
2. Verify the remote URL is correct: `conan remote list`
3. Test with `--no-remote` flag: `conan create ... --no-remote`
4. Disable problematic remote: `conan remote disable <remote_name>`

**SSL Errors:**
- Tool automatically uses `--insecure` flag for enterprise environments
- If still failing, contact IT for SSL certificate configuration

**Installation Failures:**
- Use default separate mode instead of `--together` mode to isolate failing packages
- Check network connectivity to Artifactory
- Verify package exists on remote: `conanx check`

**Source Files Not Found:**
- Run `conanx preview` to see what files will be packaged
- Verify the `source_path` in your config.json is correct
- Ensure file extensions in config.json match your source files

### Debug Information

The tool provides extensive debug output including:
- Netrc file location and parsing status
- Hostname extraction from URLs
- Authentication attempts and results
- Detailed error messages for each operation

## Security Considerations

- Store netrc files with restricted permissions (600 on Linux/Mac)
- Use service accounts for CI/CD environments
- Consider using token-based authentication for production systems

## Enterprise Integration

This tool is specifically designed for Marelli's Artifactory infrastructure:
- Pre-configured base URLs for Marelli Artifactory
- SSL configuration for enterprise environments
- Standard naming conventions for repositories
- Integration with existing authentication systems

## Requirements

- Python 3.10+
- Conan 2.0
- Click library
- Network access to Marelli Artifactory
- Valid Marelli credentials in netrc file

## Support

For issues related to:

- **Conan CLI Tool**: Check [troubleshooting section](#troubleshooting) above
- **Artifactory Access**: Contact your IT administrator
- **Authentication**: Verify [netrc file configuration](#creating-netrc-file)
- **Network Issues**: Check VPN and firewall settings

## References

- [Conan 2 - C and C++ Package Manager Documentation][1]
- [Marelli Conan 2 Confluence Page][1]
- [Marelli Conan 1 CLI][1]

[1]: https://docs.conan.io/2/index.html

