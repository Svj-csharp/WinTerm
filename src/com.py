import os
import subprocess
import sys
import platform
import json
import tarfile
import zipfile
import urllib.request
import shutil
import psutil
import datetime
import math
from pathlib import Path

class TerminalCommands:
    def __init__(self):
        self.hostname = platform.node()
        self.username = os.getenv('USER', 'user')
        self.current_dir = os.getcwd()
        self.home_dir = os.path.expanduser('~')
        self.command_history = []
        
    def print_prompt(self):
        """Print terminal prompt"""
        dir_display = self.current_dir.replace(self.home_dir, '~')
        return f"{self.username}@{self.hostname}:{dir_display}$ "
    
    def execute(self, command, *args):
        """Execute terminal command"""
        self.command_history.append(f"{command} {' '.join(args)}".strip())
        
        if command == "ls":
            return self.ls(*args)
        elif command == "cd":
            return self.cd(*args)
        elif command == "pwd":
            return self.pwd()
        elif command == "cat":
            return self.cat(*args)
        elif command == "echo":
            return self.echo(*args)
        elif command == "mkdir":
            return self.mkdir(*args)
        elif command == "rm":
            return self.rm(*args)
        elif command == "cp":
            return self.cp(*args)
        elif command == "mv":
            return self.mv(*args)
        elif command == "touch":
            return self.touch(*args)
        elif command == "clear" or command == "cls":
            return self.clear()
        elif command == "neofetch":
            return self.neofetch()
        elif command == "whoami":
            return self.whoami()
        elif command == "date":
            return self.date()
        elif command == "uname":
            return self.uname(*args)
        elif command == "df":
            return self.df(*args)
        elif command == "du":
            return self.du(*args)
        elif command == "find":
            return self.find(*args)
        elif command == "grep":
            return self.grep(*args)
        elif command == "ps":
            return self.ps()
        elif command == "kill":
            return self.kill(*args)
        elif command == "history":
            return self.history()
        elif command == "git_clone":
            return self.git_clone(*args)
        elif command == "download_release":
            return self.download_release(*args)
        elif command == "help":
            return self.help()
        elif command == "exit":
            sys.exit(0)
        else:
            # Try to execute as system command
            try:
                result = subprocess.run([command] + list(args), 
                                      capture_output=True, 
                                      text=True,
                                      cwd=self.current_dir)
                if result.stdout:
                    return result.stdout
                elif result.stderr:
                    return f"Error: {result.stderr}"
            except FileNotFoundError:
                return f"Command not found: {command}"
    
    def ls(self, *args):
        """List directory contents"""
        path = self.current_dir
        if args and not args[0].startswith('-'):
            path = os.path.join(self.current_dir, args[0])
        
        show_all = '-a' in args
        long_format = '-l' in args
        
        try:
            items = os.listdir(path)
            if not show_all:
                items = [item for item in items if not item.startswith('.')]
            
            if long_format:
                output = []
                for item in items:
                    item_path = os.path.join(path, item)
                    stat = os.stat(item_path)
                    size = stat.st_size
                    mtime = datetime.datetime.fromtimestamp(stat.st_mtime)
                    is_dir = os.path.isdir(item_path)
                    perm = oct(stat.st_mode)[-3:]
                    
                    type_char = 'd' if is_dir else '-'
                    output.append(f"{type_char}{perm} {size:8} {mtime:%b %d %H:%M} {item}")
                return "\n".join(output)
            else:
                return "  ".join(items)
        except FileNotFoundError:
            return f"ls: cannot access '{path}': No such file or directory"
    
    def cd(self, *args):
        """Change directory"""
        if not args:
            self.current_dir = self.home_dir
            return ""
        
        path = args[0]
        if path == "~":
            new_dir = self.home_dir
        elif path == "..":
            new_dir = os.path.dirname(self.current_dir)
        elif path.startswith("/"):
            new_dir = path
        else:
            new_dir = os.path.join(self.current_dir, path)
        
        try:
            if os.path.isdir(new_dir):
                self.current_dir = os.path.abspath(new_dir)
                return ""
            else:
                return f"cd: {path}: No such file or directory"
        except Exception as e:
            return f"cd: {e}"
    
    def pwd(self):
        """Print working directory"""
        return self.current_dir
    
    def cat(self, *args):
        """Concatenate and display files"""
        if not args:
            return "cat: missing operand"
        
        output_lines = []
        for filename in args:
            filepath = os.path.join(self.current_dir, filename)
            try:
                with open(filepath, 'r') as f:
                    output_lines.append(f.read())
            except FileNotFoundError:
                return f"cat: {filename}: No such file or directory"
            except IsADirectoryError:
                return f"cat: {filename}: Is a directory"
        
        return "\n".join(output_lines)
    
    def echo(self, *args):
        """Display text"""
        return " ".join(args)
    
    def mkdir(self, *args):
        """Make directories"""
        if not args:
            return "mkdir: missing operand"
        
        for dirname in args:
            try:
                os.makedirs(os.path.join(self.current_dir, dirname), exist_ok=True)
            except Exception as e:
                return f"mkdir: {e}"
        return ""
    
    def rm(self, *args):
        """Remove files/directories"""
        if not args:
            return "rm: missing operand"
        
        recursive = '-r' in args or '-rf' in args
        args = [arg for arg in args if not arg.startswith('-')]
        
        for target in args:
            target_path = os.path.join(self.current_dir, target)
            try:
                if os.path.isdir(target_path):
                    if recursive:
                        shutil.rmtree(target_path)
                    else:
                        return f"rm: {target}: is a directory"
                else:
                    os.remove(target_path)
            except FileNotFoundError:
                return f"rm: cannot remove '{target}': No such file or directory"
            except Exception as e:
                return f"rm: {e}"
        return ""
    
    def cp(self, *args):
        """Copy files"""
        if len(args) < 2:
            return "cp: missing operand"
        
        source = os.path.join(self.current_dir, args[0])
        dest = os.path.join(self.current_dir, args[1])
        
        try:
            if os.path.isdir(source):
                if os.path.exists(dest):
                    dest = os.path.join(dest, os.path.basename(source))
                shutil.copytree(source, dest)
            else:
                shutil.copy2(source, dest)
        except FileNotFoundError:
            return f"cp: cannot stat '{args[0]}': No such file or directory"
        except Exception as e:
            return f"cp: {e}"
        return ""
    
    def mv(self, *args):
        """Move/rename files"""
        if len(args) < 2:
            return "mv: missing operand"
        
        source = os.path.join(self.current_dir, args[0])
        dest = os.path.join(self.current_dir, args[1])
        
        try:
            shutil.move(source, dest)
        except FileNotFoundError:
            return f"mv: cannot stat '{args[0]}': No such file or directory"
        except Exception as e:
            return f"mv: {e}"
        return ""
    
    def touch(self, *args):
        """Create empty files"""
        for filename in args:
            try:
                filepath = os.path.join(self.current_dir, filename)
                Path(filepath).touch()
            except Exception as e:
                return f"touch: {e}"
        return ""
    
    def clear(self):
        """Clear terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
        return ""
    
    def neofetch(self):
        """Display system information"""
        system_info = platform.uname()
        
        # Get CPU information
        cpu_info = platform.processor()
        if not cpu_info:
            cpu_info = "Unknown"
        
        # Get memory information
        memory = psutil.virtual_memory()
        mem_total = memory.total / (1024**3)
        mem_used = memory.used / (1024**3)
        
        # Get disk information
        disk = psutil.disk_usage('/')
        disk_total = disk.total / (1024**3)
        disk_used = disk.used / (1024**3)
        
        info = f"""
               {self.username}@{self.hostname}
               ---------------
               OS: {system_info.system} {system_info.release}
               Kernel: {system_info.version.split('#')[0]}
               Uptime: {self._get_uptime()}
               Shell: {os.environ.get('SHELL', 'Unknown')}
               Terminal: {os.environ.get('TERM', 'Unknown')}
               CPU: {cpu_info}
               Memory: {mem_used:.1f}GiB / {mem_total:.1f}GiB
               Disk: {disk_used:.1f}GiB / {disk_total:.1f}GiB
        """
        
        # Add ASCII art based on OS
        ascii_art = self._get_ascii_art(system_info.system)
        
        return ascii_art + info
    
    def _get_uptime(self):
        """Get system uptime"""
        try:
            with open('/proc/uptime', 'r') as f:
                uptime_seconds = float(f.readline().split()[0])
            
            days = uptime_seconds // 86400
            hours = (uptime_seconds % 86400) // 3600
            minutes = (uptime_seconds % 3600) // 60
            
            if days > 0:
                return f"{int(days)} days, {int(hours)} hours"
            elif hours > 0:
                return f"{int(hours)} hours, {int(minutes)} mins"
            else:
                return f"{int(minutes)} mins"
        except:
            return "Unknown"
    
    def _get_ascii_art(self, os_name):
        """Get ASCII art for the OS"""
        arts = {
            "Linux": """
                   .88888888:.
                88888888.88888.
              .8888888888888888.
              888888888888888888
              88' _`88'_  `88888
              88 88 88 88  88888
              88_88_::_88_:88888
              88:::,::,:::::8888
              88`:::::::::'`8888
             .88  `::::'    8:88.
            8888            `8:888.
          .8888'             `888888.
         .8888:..  .::.  ...:'8888888:.
        .8888.'     :'     `'::`88:88888
       .8888        '         `.888:8888.
      888:8         .           888:88888
    .888:88        .:           888:88888:
    8888888.       ::           88:888888
    `.::.888.      ::          .88888888
   .::::::.888.    ::         :::`8888'.:.
  ::::::::::.888   '         .::::::::::::
  ::::::::::::.8    '      .:8::::::::::::.
 .::::::::::::::.        .:888:::::::::::::
 :::::::::::::::88:.__..:88888:::::::::::'
  `'.:::::::::::88888888888.88:::::::::'
        `':::_:' -- '' -'-' `':_::::'`
            """,
            "Windows": """
            ⠀⠀⠀⣤⣴⣾⣿⣿⣿⣿⣿⣶⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⡄
⠀⠀⢀⣿⣿⣿⣿⣿⣿⣿⣿⣿⠀⠀⢰⣦⣄⣀⣀⣠⣴⣾⣿⠃
⠀⠀⢸⣿⣿⣿⣿⣿⣿⣿⣿⡏⠀⠀⣼⣿⣿⣿⣿⣿⣿⣿⣿⠀
⠀⠀⣼⣿⡿⠿⠛⠻⠿⣿⣿⡇⠀⠀⣿⣿⣿⣿⣿⣿⣿⣿⡿⠀
⠀⠀⠉⠀⠀⠀⢀⠀⠀⠀⠈⠁⠀⢰⣿⣿⣿⣿⣿⣿⣿⣿⠇⠀
⠀⠀⣠⣴⣶⣿⣿⣿⣷⣶⣤⠀⠀⠀⠈⠉⠛⠛⠛⠉⠉⠀⠀⠀
⠀⢸⣿⣿⣿⣿⣿⣿⣿⣿⡇⠀⠀⣶⣦⣄⣀⣀⣀⣤⣤⣶⠀⠀
⠀⣾⣿⣿⣿⣿⣿⣿⣿⣿⡇⠀⢀⣿⣿⣿⣿⣿⣿⣿⣿⡟⠀⠀
⠀⣿⣿⣿⣿⣿⣿⣿⣿⣿⠁⠀⢸⣿⣿⣿⣿⣿⣿⣿⣿⡇⠀⠀
⢠⣿⡿⠿⠛⠉⠉⠉⠛⠿⠀⠀⢸⣿⣿⣿⣿⣿⣿⣿⣿⠁⠀⠀
⠘⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠻⢿⣿⣿⣿⣿⣿⠿⠛⠀⠀⠀
        """,
            "Darwin": """
                    c.'
                 ,xNMM.
               .OMMMMo
               lMM"
     .;loddo:.  .olloddol;.
   cKMMMMMMMMMMNWMMMMMMMMMM0:
 .KMMMMMMMMMMMMMMMMMMMMMMMWd.
 XMMMMMMMMMMMMMMMMMMMMMMMX.
;MMMMMMMMMMMMMMMMMMMMMMMMM:
:MMMMMMMMMMMMMMMMMMMMMMMMM:
.MMMMMMMMMMMMMMMMMMMMMMMMX.
 kMMMMMMMMMMMMMMMMMMMMMMMMWd.
 'XMMMMMMMMMMMMMMMMMMMMMMMMMMk
  'XMMMMMMMMMMMMMMMMMMMMMMMMK.
    kMMMMMMMMMMMMMMMMMMMMMMd
     ;KMMMMMMMWXXWMMMMMMMk.
       "cooc*"    "*coo'"
            """
        }
        
        return arts.get(os_name, """
            OS not recognized
               ⠀⠀⠀⠀
        """)
    
    def whoami(self):
        """Print current user"""
        return self.username
    
    def date(self):
        """Print current date and time"""
        return datetime.datetime.now().strftime("%a %b %d %H:%M:%S %Y")
    
    def uname(self, *args):
        """Print system information"""
        system_info = platform.uname()
        
        if '-a' in args:
            return f"{system_info.system} {system_info.node} {system_info.release} {system_info.version} {system_info.machine}"
        elif '-s' in args:
            return system_info.system
        elif '-n' in args:
            return system_info.node
        elif '-r' in args:
            return system_info.release
        elif '-m' in args:
            return system_info.machine
        else:
            return system_info.system
    
    def df(self, *args):
        """Display disk space usage"""
        partitions = psutil.disk_partitions()
        output = ["Filesystem      Size  Used  Avail  Use%  Mounted on"]
        
        for partition in partitions:
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                size_gb = usage.total / (1024**3)
                used_gb = usage.used / (1024**3)
                avail_gb = usage.free / (1024**3)
                percent = usage.percent
                
                output.append(f"{partition.device[:14]:14} {size_gb:4.1f}G {used_gb:4.1f}G {avail_gb:4.1f}G {percent:4.0f}%  {partition.mountpoint}")
            except:
                continue
        
        return "\n".join(output)
    
    def du(self, *args):
        """Estimate file space usage"""
        path = self.current_dir
        if args:
            path = os.path.join(self.current_dir, args[0])
        
        try:
            total_size = 0
            for dirpath, dirnames, filenames in os.walk(path):
                for f in filenames:
                    fp = os.path.join(dirpath, f)
                    if os.path.exists(fp):
                        total_size += os.path.getsize(fp)
            
            # Convert to human readable format
            for unit in ['B', 'K', 'M', 'G']:
                if total_size < 1024.0:
                    return f"{total_size:.1f}{unit}"
                total_size /= 1024.0
            return f"{total_size:.1f}T"
        except Exception as e:
            return f"du: {e}"
    
    def find(self, *args):
        """Search for files"""
        if len(args) < 2:
            return "Usage: find [path] -name [pattern]"
        
        path = args[0]
        pattern = args[2] if '-name' in args else '*'
        
        try:
            results = []
            for root, dirs, files in os.walk(os.path.join(self.current_dir, path)):
                for name in files:
                    if pattern in name:
                        results.append(os.path.join(root, name))
            return "\n".join(results) if results else "No files found"
        except Exception as e:
            return f"find: {e}"
    
    def grep(self, *args):
        """Search text using patterns"""
        if len(args) < 2:
            return "Usage: grep [pattern] [file]"
        
        pattern = args[0]
        filename = args[1]
        filepath = os.path.join(self.current_dir, filename)
        
        try:
            with open(filepath, 'r') as f:
                lines = f.readlines()
            
            matches = []
            for i, line in enumerate(lines, 1):
                if pattern in line:
                    matches.append(f"{i}: {line.strip()}")
            
            return "\n".join(matches) if matches else f"No matches found for '{pattern}'"
        except FileNotFoundError:
            return f"grep: {filename}: No such file or directory"
    
    def ps(self):
        """Display process status"""
        output = ["PID    CMD"]
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                output.append(f"{proc.info['pid']:<6} {proc.info['name']}")
            except:
                continue
        
        return "\n".join(output[:20])  # Show first 20 processes
    
    def kill(self, *args):
        """Terminate processes"""
        if not args:
            return "Usage: kill [pid]"
        
        try:
            pid = int(args[0])
            os.kill(pid, 9)
            return f"Process {pid} terminated"
        except ProcessLookupError:
            return f"kill: ({pid}) - No such process"
        except Exception as e:
            return f"kill: {e}"
    
    def history(self):
        """Show command history"""
        return "\n".join([f"{i+1}  {cmd}" for i, cmd in enumerate(self.command_history[-20:])])
    
    def git_clone(self, *args):
        """Clone a Git repository"""
        if not args:
            return "Usage: git_clone [repository_url]"
        
        url = args[0]
        repo_name = url.split('/')[-1]
        if repo_name.endswith('.git'):
            repo_name = repo_name[:-4]
        
        target_dir = os.path.join(self.current_dir, repo_name)
        
        try:
            # For GitHub, we can use the API for public repos
            if 'github.com' in url:
                api_url = url.replace('github.com', 'api.github.com/repos').replace('.git', '')
                if not api_url.startswith('http'):
                    api_url = 'https://' + api_url
                
                # Get repository info
                with urllib.request.urlopen(api_url) as response:
                    repo_data = json.loads(response.read())
                    default_branch = repo_data.get('default_branch', 'main')
                    clone_url = repo_data.get('clone_url', url)
                
                # Download as zip
                zip_url = f"{url.replace('.git', '')}/archive/refs/heads/{default_branch}.zip"
                
                print(f"Cloning into '{repo_name}'...")
                zip_path = os.path.join(self.current_dir, f"{repo_name}.zip")
                
                # Download zip file
                with urllib.request.urlopen(zip_url) as response, open(zip_path, 'wb') as out_file:
                    shutil.copyfileobj(response, out_file)
                
                # Extract zip file
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(self.current_dir)
                
                # Remove zip file
                os.remove(zip_path)
                
                # Rename extracted directory
                extracted_dir = os.path.join(self.current_dir, f"{repo_name}-{default_branch}")
                if os.path.exists(extracted_dir):
                    if os.path.exists(target_dir):
                        shutil.rmtree(target_dir)
                    os.rename(extracted_dir, target_dir)
                
                return f"Repository cloned to {target_dir}"
            else:
                return "Currently only GitHub repositories are supported"
        except Exception as e:
            return f"Error cloning repository: {e}"
    
    def download_release(self, *args):
        """Download a GitHub release"""
        if not args:
            return "Usage: download_release [owner/repo] [tag?]"
        
        repo = args[0]
        tag = args[1] if len(args) > 1 else 'latest'
        
        try:
            if tag == 'latest':
                api_url = f"https://api.github.com/repos/{repo}/releases/latest"
            else:
                api_url = f"https://api.github.com/repos/{repo}/releases/tags/{tag}"
            
            with urllib.request.urlopen(api_url) as response:
                release_data = json.loads(response.read())
            
            # Find asset (prefer source code)
            asset = None
            for a in release_data.get('assets', []):
                if 'source' in a['name'].lower() or 'src' in a['name'].lower():
                    asset = a
                    break
            
            if not asset and release_data.get('assets'):
                asset = release_data['assets'][0]
            
            if asset:
                download_url = asset['browser_download_url']
                filename = asset['name']
                
                print(f"Downloading {filename}...")
                filepath = os.path.join(self.current_dir, filename)
                
                with urllib.request.urlopen(download_url) as response, open(filepath, 'wb') as out_file:
                    shutil.copyfileobj(response, out_file)
                
                # Extract if it's an archive
                if filename.endswith('.zip'):
                    with zipfile.ZipFile(filepath, 'r') as zip_ref:
                        zip_ref.extractall(self.current_dir)
                    os.remove(filepath)
                    return f"Release extracted to {self.current_dir}"
                elif filename.endswith('.tar.gz') or filename.endswith('.tgz'):
                    with tarfile.open(filepath, 'r:gz') as tar_ref:
                        tar_ref.extractall(self.current_dir)
                    os.remove(filepath)
                    return f"Release extracted to {self.current_dir}"
                else:
                    return f"Release downloaded to {filepath}"
            else:
                # Fallback to source code zip
                source_url = f"https://github.com/{repo}/archive/refs/tags/{release_data['tag_name']}.zip"
                filename = f"{repo.split('/')[1]}-{release_data['tag_name']}.zip"
                
                print(f"Downloading source code...")
                filepath = os.path.join(self.current_dir, filename)
                
                with urllib.request.urlopen(source_url) as response, open(filepath, 'wb') as out_file:
                    shutil.copyfileobj(response, out_file)
                
                with zipfile.ZipFile(filepath, 'r') as zip_ref:
                    zip_ref.extractall(self.current_dir)
                
                os.remove(filepath)
                return f"Source code extracted to {self.current_dir}"
                
        except Exception as e:
            return f"Error downloading release: {e}"
    
    def help(self):
        """Display help information"""
        help_text = """
Available commands:
  ls [path] [-l] [-a]     - List directory contents
  cd [path]               - Change directory
  pwd                     - Print working directory
  cat [file...]           - Display file contents
  echo [text...]          - Display text
  mkdir [dir...]          - Create directories
  rm [file...] [-r]       - Remove files/directories
  cp [source] [dest]      - Copy files
  mv [source] [dest]      - Move/rename files
  touch [file...]         - Create empty files
  clear/cls               - Clear terminal screen
  neofetch                - Display system information
  whoami                  - Print current user
  date                    - Print date and time
  uname [-a]              - Print system information
  df                      - Display disk usage
  du [path]               - Estimate file space usage
  find [path] -name [pat] - Search for files
  grep [pattern] [file]   - Search text in files
  ps                      - Display processes
  kill [pid]              - Terminate process
  history                 - Show command history
  git_clone [url]         - Clone Git repository
  download_release [repo] [tag?] - Download GitHub release
  help                    - Show this help
  exit                    - Exit terminal
        """
        return help_text