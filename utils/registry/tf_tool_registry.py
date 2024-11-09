import os
from importlib import import_module
from typing import Type, Dict

class TFToolRegistry:
    """
    Singleton registry for managing tool registration and discovery.
    
    This class maintains a central registry of all tool classes and provides
    functionality for automatic tool discovery and registration. It ensures
    tools are properly configured with metadata before registration.

    Class Attributes:
        _instance: Internal singleton instance reference.
        _tools (Dict[str, Type]): Dictionary mapping tool class names to tool classes.

    Note:
        Tool classes must define a `metadata` attribute of type `TFToolMetadata`
        to be successfully registered.
    """
    _instance = None
    _tools: Dict[str, Type] = {}
    
    @classmethod
    def register(cls, tool_class) -> None:
        """
        Register a tool class with the registry.

        The tool class must have a metadata attribute defining its configuration.
        Registration makes the tool available for use in the application.

        Args:
            tool_class (Type): Tool class to register.

        Raises:
            ValueError: If the tool class doesn't have the required metadata attribute.
        """
        if not hasattr(tool_class, 'metadata'):
            raise ValueError(f"Tool class {tool_class.__name__} must have metadata attribute")
        cls._tools[tool_class.__name__] = tool_class
    
    @classmethod
    def get_tools(cls) -> Dict[str, Type]:
        """Get a copy of all registered tools.

        Returns:
            Dict[str, Type]: Dictionary mapping tool class names to tool classes.
        """
        return cls._tools.copy()
    
    @classmethod
    def auto_discover_tools(cls, tools_dir: str = 'implements') -> None:
        """
        Automatically discover and register tools from the specified directory.

        Scans the given directory for Python files and attempts to import and
        register any tool classes found within them.

        Args:
            tools_dir (str, optional): 
                Directory path containing tool implementations.
                Defaults to 'ui/tf_frames_impl'.

        Note:
            Tool files must end with '.py' and not start with '__' to be discovered.
            Tools must have proper metadata to be registered successfully.

        Example:
            >>> TFToolRegistry.auto_discover_tools('ui/custom_tools')
        """
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        full_path = os.path.join(base_path, '..', tools_dir)
        
        if not os.path.exists(full_path):
            return
            
        module_path = tools_dir.replace('/', '.')
        
        for filename in os.listdir(full_path):
            if filename.endswith('.py') and not filename.startswith('__'):
                module_name = f"{module_path}.{filename[:-3]}"
                import_module(module_name)
