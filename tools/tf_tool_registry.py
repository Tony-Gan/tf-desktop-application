import os
from importlib import import_module
from typing import Type, Dict

class TFToolRegistry:
    """Singleton registry for managing tool registration"""
    _instance = None
    _tools: Dict[str, Type] = {}
    
    @classmethod
    def register(cls, tool_class) -> None:
        """Register a tool class"""
        if not hasattr(tool_class, 'metadata'):
            raise ValueError(f"Tool class {tool_class.__name__} must have metadata attribute")
        cls._tools[tool_class.__name__] = tool_class
    
    @classmethod
    def get_tools(cls) -> Dict[str, Type]:
        """Get all registered tools"""
        return cls._tools.copy()
    
    @classmethod
    def auto_discover_tools(cls, tools_dir: str = 'ui/tf_frames_impl') -> None:
        """
        Automatically discover and register tools from the specified directory
        
        Args:
            tools_dir: Directory path containing tool implementations
        """
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        full_path = os.path.join(base_path, tools_dir)
        
        if not os.path.exists(full_path):
            return
            
        # Convert directory path to module path
        module_path = tools_dir.replace('/', '.')
        
        # Scan for Python files in the directory
        for filename in os.listdir(full_path):
            if filename.endswith('.py') and not filename.startswith('__'):
                module_name = f"{module_path}.{filename[:-3]}"
                import_module(module_name)
