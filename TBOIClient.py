import ModuleUpdate
import Utils
from worlds.tboirp.Client import launch
ModuleUpdate.update()

if __name__ == '__main__':
    Utils.init_logging("TBOIClient", exception_logger="Client")
    launch()
