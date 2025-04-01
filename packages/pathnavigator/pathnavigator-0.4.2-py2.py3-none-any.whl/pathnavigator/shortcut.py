import json
import keyword
from dataclasses import dataclass
from pathlib import Path

"""
    Methods
    -------
    add(name, path, overwrite=False)
        Adds a new shortcut as an attribute. 
    remove(name)
        Removes an existing shortcut by name and deletes the attribute.
    ls()
        Lists all shortcuts (attributes).
    to_json(filename)
        Returns all shortcuts as a JSON string and saves it to a file.
    to_dict()
        Returns all shortcuts as a dictionary.
    load_dict(data, overwrite=False)
        Loads shortcuts from a dictionary.
    load_json(filename, overwrite=False)
        Loads shortcuts from a JSON file.
"""

@dataclass
class Shortcut:
    """
    A class to manage shortcuts to specific paths and access them as attributes.
    """

    def __setattr__(self, name: str, value: str|Path, overwrite: bool = False):
        """
        Dynamically add shortcut as an attribute.

        Parameters
        ----------
        name : str
            The name of the shortcut.
        value : str or Path
            The path that the shortcut refers to.
        overwrite : bool, optional
            Whether to overwrite an existing shortcut. Default is False.
        """
        if name in self.__dict__ and not overwrite:
            raise AttributeError(f"Cannot add shortcut '{name}' as it conflicts with an existing attribute.")
        super().__setattr__(name, Path(value))
        print(f"Shortcut '{name}' added for path '{value}'")

    def __getattr__(self, name: str) -> str:
        """
        Retrieve the path of a shortcut.

        Parameters
        ----------
        name : str
            The name of the shortcut.

        Returns
        -------
        str
            The path associated with the shortcut.

        Raises
        ------
        AttributeError
            If the shortcut does not exist.
        """
        if name not in self.__dict__:
            raise AttributeError(f"No shortcut found for '{name}'")
        return self.__dict__[name]

    def __delattr__(self, name: str):
        """
        Remove a shortcut by name.

        Parameters
        ----------
        name : str
            The name of the shortcut to remove.

        Raises
        ------
        AttributeError
            If the shortcut does not exist.
        """
        if name not in self.__dict__:
            raise AttributeError(f"No shortcut found for '{name}'")
        super().__delattr__(name)
        print(f"Shortcut '{name}' removed")

    def add(self, name: str, path: str, overwrite: bool = False):
        """
        Add a new shortcut as an attribute.

        Parameters
        ----------
        name : str
            The name of the shortcut.
        path : str
            The path that the shortcut refers to.
        overwrite : bool, optional
            Whether to overwrite an existing shortcut. Default is False.

        Examples
        --------
        >>> shortcut = Shortcut()
        >>> shortcut.add("my_folder", "/path/to/folder")
        >>> shortcut.my_folder
        '/path/to/folder'
        """
        invalid_list = ["add", "remove", "ls", "get", "get_str", "to_json", "to_dict", "load_dict", "load_json"]
        is_valid_attribute_name = name.isidentifier() and not keyword.iskeyword(name) and not name in invalid_list

        if not is_valid_attribute_name:
            raise ValueError(f"Invalid attribute name '{name}'. Please avoid using reserved names and follow the naming conventions. Reserved names {invalid_list}")
        else:
            self.__setattr__(name, path, overwrite=overwrite)

    def get(self, name: str) -> str:
        """
        Retrieve the path of a shortcut.

        Parameters
        ----------
        name : str
            The name of the shortcut.

        Returns
        -------
        str
            The path associated with the shortcut.

        Examples
        --------
        >>> shortcut = Shortcut()
        >>> shortcut.add("my_folder", "/path/to/folder")
        >>> shortcut.get("my_folder")
        '/path/to/folder'
        """
        return self.__getattr__(name)
    
    def get_str(self, name: str) -> str:
        """
        Retrieve the path of a shortcut.

        Parameters
        ----------
        name : str
            The name of the shortcut.

        Returns
        -------
        str
            The path associated with the shortcut.

        Examples
        --------
        >>> shortcut = Shortcut()
        >>> shortcut.add("my_folder", "/path/to/folder")
        >>> shortcut.get("my_folder")
        '/path/to/folder'
        """
        return str(self.__getattr__(name))
    
    def remove(self, name: str):
        """
        Remove a shortcut by name and delete its attribute.

        Parameters
        ----------
        name : str
            The name of the shortcut to remove.

        Examples
        --------
        >>> shortcut = Shortcut()
        >>> shortcut.add("my_folder", "/path/to/folder")
        >>> shortcut.remove("my_folder")
        >>> hasattr(shortcut, "my_folder")
        False
        """
        self.__delattr__(name)

    def ls(self):
        """
        List all shortcuts and their paths.

        Examples
        --------
        >>> shortcut = Shortcut()
        >>> shortcut.add("my_folder", "/path/to/folder")
        >>> shortcut.ls()
        Shortcuts:
        my_folder -> /path/to/folder
        """
        attributes = {key: value for key, value in self.__dict__.items()}
        if not attributes:
            print("No shortcuts available.")
        else:
            print("Shortcuts:")
            for name, path in attributes.items():
                print(f"{name} -> {path}")
    
    def to_json(self, filename: str) -> str:
        """
        Return all shortcuts as a JSON string and save it to a file.

        Parameters
        ----------
        filename : str
            The name of the file where the JSON string will be saved.

        Returns
        -------
        str
            A JSON string representation of all shortcuts.

        Examples
        --------
        >>> shortcut = Shortcut()
        >>> shortcut.add("my_folder", "/path/to/folder")
        >>> shortcut.to_json("shortcuts.json")
        '{"my_folder": "/path/to/folder"}'
        """
        # Converting the dictionary to a pretty-printed JSON string
        # Converting all Path objects to strings before writing to JSON
        json_data = json.dumps({k: str(v) for k, v in self.__dict__.items()}, indent=4)  
        with open(filename, 'w') as f:
            f.write(json_data)  # Writing the JSON data to the file
    
        return json_data  # Returning the JSON string as well

    def to_dict(self, to_str=False) -> dict:
        """
        Return all shortcuts as a dictionary. 

        Parameters
        ----------
        to_str : bool, optional
            Whether to convert all Path objects to strings. Default is False.

        Returns
        -------
        dict
            A dictionary representation of all shortcuts.

        Examples
        --------
        >>> shortcut = Shortcut()
        >>> shortcut.add("my_folder", "/path/to/folder")
        >>> shortcut.to_dict()
        {'my_folder': '/path/to/folder'}
        """
        if to_str:
            return {k: str(v) for k, v in self.__dict__.items()}
        else:
            return self.__dict__.copy()

    def load_dict(self, data: dict, overwrite: bool = False):
        """
        Load shortcuts from a dictionary.

        Parameters
        ----------
        data : dict
            A dictionary where keys are shortcut names and values are paths.
        overwrite : bool, optional
            Whether to overwrite existing shortcuts. Default is False.

        Examples
        --------
        >>> shortcut = Shortcut()
        >>> shortcut.load_dict({"project": "/path/to/project", "data": "/path/to/data"})
        """
        for name, path in data.items():
            self.add(name, Path(path), overwrite=overwrite)

    def load_json(self, filename: str, overwrite: bool = False):
        """
        Load shortcuts from a JSON file.

        Parameters
        ----------
        filename : str
            The name of the file containing the shortcuts in JSON format.
        overwrite : bool, optional
            Whether to overwrite existing shortcuts. Default is False.

        Examples
        --------
        >>> shortcut = Shortcut()
        >>> shortcut.load_json("shortcuts.json")
        """
        with open(filename, 'r') as f:
            data = json.load(f)  # Load the JSON data into a dictionary
            self.load_dict(data, overwrite=overwrite)  # Load the shortcuts using the load_dict method
