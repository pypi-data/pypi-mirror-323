"""
This module contains constants used throughout the project.

"""
### USER EDITABLE
# Change this if you want to change the library location - default: on the same level as your project.
LIBRARIES_ROOT_PATH = '../_Libraries'


### CHANGE AT YOUR OWN RISK - YOU SHOULD NOT NEED TO CHANGE THEM

PROJECT_ROOT_PATH = '.'
KICAD_PROJECT_ROOT_PATH = '${KIPRJMOD}'

LIBRARY_SYMBOL_NAME = 'symbols.kicad_sym'
LIBRARY_FOOTPRINT_FOLDER = 'footprints.pretty'
LIBRARY_3DMODEL_FOLDER = '3dmodels'

KICAD_SYMBOL_EXT = '.kicad_sym'
KICAD_FOOTPRINT_EXT = '.kicad_mod'
KICAD_3DMODEL_EXT = '.step'

KICAD_CUSTOM_SYMBOL_FILE = 'sym-lib-table'
KICAD_CUSTOM_FOOTPRINT_FILE = 'fp-lib-table'

KICAD_CUSTOM_SYMBOL_FILE_DEFAULT_CONTENT = """
(sym_lib_table
  (version 7)
)
"""
# KICAD_CUSTOM_SYMBOL_FILE_DEFAULT_CONTENT = """
# (sym_lib_table
#   (version 7)
#   (lib (name "testLib")(type "KiCad")(uri "${KIPRJMOD}/../_Libraries/StepUp_Custom/symbols.kicad_sym")(options "")(descr ""))
# )
# """
KICAD_CUSTOM_FOOTPRINT_FILE_DEFAULT_CONTENT = """
(fp_lib_table
  (version 7)
)
"""
#Note: Fill name then uri with "${KIPRJMOD}/../_Libraries/xxx/symbols.kicad_sym"
KICAD_LIBRARY_TEMPLATE_ENTRY = """
(lib (name "")(type "KiCad")(uri "")(options "")(descr ""))
"""


KICAD_SYMBOL_LIB_DEFAULT_CONTENT = """(kicad_symbol_lib
    (version 20211014) 
    (generator kicad_symbol_editor)
)"""