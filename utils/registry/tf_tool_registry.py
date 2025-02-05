import os
from importlib import import_module
from typing import Type, Dict

class TFToolRegistry:
    _instance = None
    _tools: Dict[str, Type] = {}
    
    @classmethod
    def register(cls, tool_class) -> None:
        if not hasattr(tool_class, 'metadata'):
            raise ValueError(f"Tool class {tool_class.__name__} must have metadata attribute")
        cls._tools[tool_class.metadata.name] = tool_class
    
    @classmethod
    def get_tools(cls) -> Dict[str, Type]:
        return cls._tools.copy()
    
    @classmethod
    def auto_discover_tools(cls, tools_dir: str = 'implements') -> None:
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        full_path = os.path.join(base_path, '..', tools_dir)
        
        if not os.path.exists(full_path):
            return
            
        base_module_path = tools_dir.replace('/', '.')
        
        for root, _, files in os.walk(full_path):
            rel_path = os.path.relpath(root, full_path)
            
            if rel_path == '.':
                current_module_path = base_module_path
            else:
                current_module_path = f"{base_module_path}.{rel_path.replace(os.sep, '.')}"
            
            for filename in files:
                if filename.endswith('.py') and not filename.startswith('__'):
                    module_name = f"{current_module_path}.{filename[:-3]}"
                    try:
                        import_module(module_name)
                    except ImportError as e:
                        print(f"Failed to import {module_name}: {str(e)}")
