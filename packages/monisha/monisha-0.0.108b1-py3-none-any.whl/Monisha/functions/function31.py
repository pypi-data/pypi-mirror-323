from .function29 import Extensions
#=============================================================================

class CheckExtension:
    
    async def get01(filename):
        moones = filename.lower()
        return True if moones.endswith(Extensions.DATA02) else False

#=============================================================================
