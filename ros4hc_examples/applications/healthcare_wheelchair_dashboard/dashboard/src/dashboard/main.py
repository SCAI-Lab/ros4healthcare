import sys
from rqt_gui.main import Main

def main(args=None):
    plugin = 'dashboard.interface.Interface'
    main = Main(filename=plugin)
    sys.exit(main.main(standalone=plugin))


if __name__ == '__main__':
    main()
