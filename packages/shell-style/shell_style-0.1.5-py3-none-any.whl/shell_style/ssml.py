from .enums import (Styles, ForegroundColors, BackgroundColors, Other)
from re import sub

def interpret(text: str, mode: int = 0) -> str:
    """
    Interprets text into SSML (Shell-Style Markup Language) or ANSI escape sequences depending on the mode
    
    Args:
        text: str,
        mode: int = 0 (must be 0 or 1)
        
    Returns: str 
    """
    
    if mode == 0:
        return ssml_to_ansi(text)
    
    elif mode == 1:
        return ansi_to_ssml(text)

    raise ValueError(f"Invalid 'mode' argument: {mode}. Must be 1 or 0")

def ssml_to_ansi(text: str) -> str:
    """
    Interprets SSML (Shell-Style Markup Language) text into ANSI escape sequences for terminal styling.
    
    Args:
        text: str 
        
    Returns: str 
    """
    
    ssml_to_ansi = {
        "<@bold>": Styles.BOLD,
        "<@dim>": Styles.DIM,
        "<@italic>": Styles.ITALIC,
        "<@underline>": Styles.UNDERLINE,
        "<@blink>": Styles.BLINK,
        "<@inverse>": Styles.INVERSE,
        "<@hidden>": Styles.HIDDEN,
        "<@strikethrough>": Styles.STRIKETHROUGH,
        "<@fg_black>": ForegroundColors.BLACK,
        "<@fg_red>": ForegroundColors.RED,
        "<@fg_green>": ForegroundColors.GREEN,
        "<@fg_yellow>": ForegroundColors.YELLOW,
        "<@fg_blue>": ForegroundColors.BLUE,
        "<@fg_magenta>": ForegroundColors.MAGENTA,
        "<@fg_cyan>": ForegroundColors.CYAN,
        "<@fg_white>": ForegroundColors.WHITE,
        "<@bg_black>": BackgroundColors.BLACK,
        "<@bg_red>": BackgroundColors.RED,
        "<@bg_green>": BackgroundColors.GREEN,
        "<@bg_blue>": BackgroundColors.BLUE,
        "<@bg_magenta>": BackgroundColors.MAGENTA,
        "<@bg_cyan>": BackgroundColors.CYAN,
        "<@bg_white>": BackgroundColors.WHITE,
        "<@stop>": Other.STOP,
        "<@info>": ForegroundColors.CYAN,
        "<@success>": ForegroundColors.GREEN,
        "<@warning>": ForegroundColors.YELLOW,
        "<@error>": ForegroundColors.RED,
        "<@heading>": Styles.BOLD.value + Styles.UNDERLINE.value
    }

    for ssml, ansi in ssml_to_ansi.items():
        text = text.replace(ssml, ansi)

    return text

def ansi_to_ssml(text: str) -> str:
    """
    Interprets ANSI escape sequences into SSML (Shell-Style Markup Language) text for terminal styling.
    
    Args:
        text: str 
        
    Returns: str 
    """
    
    ansi_to_ssml_map = {
        r"\033\[1m": "<@bold>",                  
        r"\033\[2m": "<@dim>",                 
        r"\033\[3m": "<@italic>",              
        r"\033\[4m": "<@underline>",            
        r"\033\[5m": "<@blink>",                
        r"\033\[7m": "<@inverse>",              
        r"\033\[8m": "<@hidden>",               
        r"\033\[9m": "<@strikethrough>",         
        r"\033\[38;2;(\d+);(\d+);(\d+)m": r"<@fg_rgb(\1,\2,\3)>",  
        r"\033\[48;2;(\d+);(\d+);(\d+)m": r"<@bg_rgb(\1,\2,\3)>", 
        r"\033\[38;5;(\d+)m": r"<@fg_color(\1)>",  
        r"\033\[48;5;(\d+)m": r"<@bg_color(\1)>", 
        r"\033\[38;2;([0-9a-fA-F]{6})m": r"<@fg_hex(\1)>",  
        r"\033\[48;2;([0-9a-fA-F]{6})m": r"<@bg_hex(\1)>", 
        r"\033\[0m": "<@stop>",                  
    }

    for ansi, ssml in ansi_to_ssml_map.items():
        text = sub(ansi, ssml, text)

    return text
