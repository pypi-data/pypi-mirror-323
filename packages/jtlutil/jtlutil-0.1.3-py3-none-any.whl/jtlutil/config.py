

from pathlib import Path
from typing import Any, Dict, List, Tuple
from dotenv import dotenv_values
import os 

class Config:
    def __init__(self, config_dict: Dict[str, Any]):
        self._config_dict = config_dict

    def __setattr__(self, name: str, value: Any) -> None:
        if name == "_config_dict":
            super().__setattr__(name, value)
        else:
            self._config_dict[name] = value

    def __getattr__(self, name: str) -> Any:
        try:
            return self._config_dict[name]
        except KeyError:
            raise AttributeError(f"'Config' object has no attribute '{name}'")

    def __getitem__(self, key: str) -> Any:
        return self._config_dict[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self._config_dict[key] = value

    def __delitem__(self, key: str) -> None:
        del self._config_dict[key]

    def __contains__(self, key: str) -> bool:
        return key in self._config_dict

    def get(self, key: str, default: Any = None) -> Any:
        return self._config_dict.get(key, default)

    def keys(self) -> List[str]:
        return list(self._config_dict.keys())

    def values(self) -> List[Any]:
        return list(self._config_dict.values())

    def items(self) -> List[Tuple[str, Any]]:
        return list(self._config_dict.items())

def walk_up(d, f=None) -> List[Path]:
    d = Path(d).resolve()
    paths = []
    while True:
        d = d.parent
        if d == Path('/'):
            break

        if f is not None:
            paths.append(d / f)
        else:
            paths.append(d)

    return paths
def get_config_dirs(cwd=None, root=Path('/'), home=Path().home()) -> List[Path]:
    
    if cwd is None:
        cwd = Path.cwd()
    else:
        cwd = Path(cwd)

    root = Path(root)
    home = Path(home)

    return  [
        cwd,
        home.joinpath('.jtl'),
        root / Path('etc/jtl'), 
        root / Path('etc/jtl/secrets'), 
        root / Path('app/config'),
        root / Path('app/secrets'),
        cwd.joinpath('secrets'),
        cwd.parent.joinpath('secrets'),
    ] 


def find_config_file(file: str | List[str], dirs: List[str] | List[Path] = None) -> Path:
    """Find the first instance of a config file, from  a list of possible files, 
    in a list of directories. Return the first file that exists. """

    if isinstance(file, str):
        file = [file]

    if dirs is None:
        dirs = get_config_dirs()


    for d in dirs:
        for f in file:
            p = Path(d) / f 
            if p.exists():
                return p    
    
    raise FileNotFoundError(f"Could not find any of {file} in {dirs}")


def get_config(file: str | Path = None, dirs: List[str] | List[Path] = None) -> Config:

    if file is None:
        file = 'config.env'


    if '/' in str(file):
        fp = Path(file)
    else:
        fp = find_config_file(file, dirs)

    config = {
        '__CONFIG_PATH': str(fp.absolute()),
        **os.environ,
        **dotenv_values(fp),
    }

    return Config(config)


def path_interp(path: str, **kwargs) -> Tuple[str, Dict[str, Any]]:
    """
    Interpolates the parameters into the endpoint URL. So if you have a path
    like '/api/v1/leagues/:league_id/teams/:team_id' and you call

            path_interp(path, league_id=1, team_id=2, foobar=3)

    it will return '/api/v1/leagues/1/teams/2', along with a dictionary of
    the remaining parameters {'foobar': 3}.

    :param path: The endpoint URL template with placeholders.
    :param kwargs: The keyword arguments where the key is the placeholder (without ':') and the value is the actual value to interpolate.

    :return: A string with the placeholders in the path replaced with actual values from kwargs.
    """

    params = {}
    for key, value in kwargs.items():
        placeholder = f":{key}"  # Placeholder format in the path
        if placeholder in path:
            path = path.replace(placeholder, str(value))
        else:
            # Remove the trailing underscore from the key, so we can use params
            # like 'from' that are python keywords.
            params[key.rstrip('_')] = value

    return path, params
