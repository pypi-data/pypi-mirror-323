"""        
Shell-Style: A Python Package for styling terminal output.
Supports ANSI escape codes, tables, progress bars, and more
"""

from sys import stdout
from warnings import warn
from os import (getenv, environ)
from .models import (ProgressBar, DEFAULT_THEME)

# Set __all__
__all__ = ["rgb_to_ansi", "hex_to_ansi", "run_progress_bar", "DEFAULT_THEME"]

# Check whether the terminal is compatible with Shell-STyle    
compatible = 0

if stdout.isatty():
    compatible += 1
    
term = getenv("TERM", "")
if term and ("xterm" in term or "color" in term):
    compatible += 1
    
if environ.get("COLORTERM", "").lower() in ("truecolor", "24bit"):
    compatible += 1
    
if compatible == 1:
    warn("Warning: This terminal may not be compatible with ShellStyle", Warning)

if compatible == 0:
    warn("Warning: This terminal is probably not compatible with ShellStyle", Warning)
    
del (compatible, stdout, getenv, term)
    
def rgb_to_ansi(red: int, green: int, blue: int, mode: str = "fg") -> str:
    """
    Convert a RGB code into an ANSI escape sequence. Only works on 
    modern terminals.
    
    Args:
        red: int, 
        green: int, 
        blue: int, 
        mode: str = "fg"
    
    Returns: str
    """
    
    for value in (red, green, blue):
        if value < 0 or value > 255:
            raise ValueError("Arguments must be less than 255 and more than one")
    
    return f"\033[38;2;{red};{green};{blue}m" if mode == "fg" else f"\033[48;2;{red};{green};{blue}m"

def hex_to_ansi(code: str, mode: str = "fg") -> str:
    """
    Convert a HEX code into an ANSI escape sequence after converting
    it into a RGB code. Only works on modern terminals.
    
    Args:
        code: str, 
        mode: str = "fg"
    
    Returns: str
    """
    
    code = code.strip()
    
    if "#" in code:
        code = code.strip().replace("#", "")
    
    if len(code) > 6:
        raise ValueError("Argument code must be a valid hex code")
    
    return rgb_to_ansi(int(code[0:2], 16), int(code[2:4], 16), int(code[4:6], 16), mode)

def run_progress_bar(values: int, *, delay: float = 1, symbol: str = "-") -> None:
        """
        Run a progress bar.
        
        Args: 
            values: int,
            delay: float = 1,
            style: str = "default"
            
        Returns: NoReturn
        """
        
        progress_bar = ProgressBar(values)
        progress_bar.run()
        
del ProgressBar
        