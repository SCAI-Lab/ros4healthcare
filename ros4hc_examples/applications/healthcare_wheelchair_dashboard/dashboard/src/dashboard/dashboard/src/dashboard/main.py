import sys

from rqt_gui.main import Main
from dashboard.interface import Interface


def main():
    plugin = 'dashboard.interface.Interface'
    main = Main(filename=plugin)
    sys.exit(main.main(standalone=plugin))


if __name__ == '__main__':
    main()
