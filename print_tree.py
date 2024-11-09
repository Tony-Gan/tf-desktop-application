import os

def print_directory_tree(start_path, exclude_dirs=None, exclude_files=None):
    if exclude_dirs is None:
        exclude_dirs = ['.git', '__pycache__', 'build', 'dist', '.idea', '.vscode']
    
    if exclude_files is None:
        exclude_files = ['.pyc', '.pyo', '.pyd', '.so', '.dll']

    prefix = '│   '
    for root, dirs, files in os.walk(start_path):
        level = root.replace(start_path, '').count(os.sep)
        indent = prefix * (level)
        
        foldername = os.path.basename(root)
        if level == 0:
            print(f"📁 {os.path.basename(os.path.abspath(root))}")
        else:
            print(f"{indent[:-4]}└── 📁 {foldername}")
        
        dirs[:] = sorted([d for d in dirs if d not in exclude_dirs])
        
        files = sorted([f for f in files 
                       if not any(f.endswith(ext) for ext in exclude_files) and 
                       not f.startswith('.')])
        
        for i, file in enumerate(files):
            if i == len(files) - 1:
                print(f"{indent}└── 📄 {file}")
            else:
                print(f"{indent}├── 📄 {file}")

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    print("\nProject Structure:")
    print("=================")
    print_directory_tree(current_dir)