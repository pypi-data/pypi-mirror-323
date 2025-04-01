# RS = '' # &#x001e in HTML
# """The record separator."""
# US = '' # &#x001f in HTML
# """The unit separator."""

# FS = '' # &#x001c in HTML
# """The File separator."""
# GS = '' # &#x001d in HTML
# """The group separator."""


_RS = '' # &#x001e in HTML --Record separator
_US = '' # &#x001f in HTML --Unit separator

_FS = '' # &#x001c in HTML --File separator
_GS = '' # &#x001d in HTML --Group separator

_SOHG = '' # &#x0001 --Start of Header for table level
_STXG = '' # &#x0002 --Start of Text for table level
_ETXG = '' # &#x0003 --End of Text for table level

_SOHF = '' # &#x0001 --Start of Header for group level --Literal['\u0001\u0001']
_STXF = '' # &#x0002 --Start of Text for group level
_ETXF = '' # &#x0003 --End of Text for group level

_SOHFG = '' # &#x0001 --Start of Header for File level
_STXFG = '' # &#x0002 --Start of Text for File level
_ETXFG = '' # &#x0003 --End of Text for File level

_HTAB = "\t" # &#x0009 in HTML - Horizontal Tab
_NEWLINE = "\n" # &#x000A in HTML - Line Feed
_VTAB = "\v" # &#x000B in HTML - Vertical Tab  


#############################################
# define functions for readable file formats
F_RS = lambda r: _RS+_NEWLINE if r == True else _RS
F_US = lambda r: _US+_HTAB if r == True else _US

F_FS = lambda r: _FS+_NEWLINE if r == True else _FS
F_GS = lambda r: _GS+_NEWLINE if r == True else _GS

F_SOHG = lambda r: _SOHG+_NEWLINE if r == True else _SOHG
F_STXG = lambda r: _STXG+_NEWLINE if r == True else _STXG
F_ETXG = lambda r: _ETXG+_NEWLINE if r == True else _ETXG

F_SOHF = lambda r: _SOHF+_NEWLINE if r == True else _SOHF
F_STXF = lambda r: _STXF+_NEWLINE if r == True else _STXF
F_ETXF = lambda r: _ETXF+_NEWLINE if r == True else _ETXF

F_SOHFG = lambda r: _SOHFG+_NEWLINE if r == True else _SOHFG
F_STXFG = lambda r: _STXFG+_NEWLINE if r == True else _STXFG
F_ETXFG = lambda r: _ETXFG+_NEWLINE if r == True else _ETXFG


# ASCII = dict(
#     RS = '', # &#x001e in HTML
#     US = '', # &#x001f in HTML

#     FS = '', # &#x001c in HTML
#     GS = '', # &#x001d in HTML

#     SOH = '', # &#x0001
#     STX = '', # &#x0002
#     ETX = '' # &#x0003
# )
# ASCII['RS']
# check on:  https://www.w3schools.com/charsets/tryit.asp?deci=8251

