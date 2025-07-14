from textual.widgets import DirectoryTree as BaseDirectoryTree
from pathlib import Path
from typing import Set


class DirectoryTree(BaseDirectoryTree):
    def __init__(self, path: str, *args, **kwargs):
        super().__init__(path, *args, **kwargs)
        self._file_extensions_to_show = {
            '.py', '.js', '.ts', '.tsx', '.jsx', '.html', '.css', '.scss',
            '.json', '.md', '.yaml', '.yml', '.xml', '.sql', '.sh', '.rs',
            '.go', '.java', '.cpp', '.c', '.h', '.hpp', '.txt', '.log',
            '.php', '.rb', '.swift', '.kt', '.scala', '.r', '.vim', '.lua',
            '.pl', '.tcl', '.dockerfile', '.toml', '.ini', '.cfg', '.conf'
        }
    
    def filter_paths(self, paths):
        """Filter paths to only show relevant files and directories"""
        filtered = []
        for path in paths:
            try:
                path_obj = Path(path)
                
                # Always show directories
                if path_obj.is_dir():
                    # Skip hidden directories and common build/cache directories
                    if not path_obj.name.startswith('.') and path_obj.name not in {
                        'node_modules', '__pycache__', '.git', '.svn', '.hg',
                        'build', 'dist', 'target', '.vscode', '.idea'
                    }:
                        filtered.append(path)
                else:
                    # Show files with relevant extensions or no extension
                    if (path_obj.suffix.lower() in self._file_extensions_to_show or
                        not path_obj.suffix or
                        path_obj.name in {'Makefile', 'README', 'LICENSE', 'Dockerfile'}):
                        filtered.append(path)
            except (OSError, PermissionError):
                # Skip files/directories that can't be accessed
                continue
        
        return filtered