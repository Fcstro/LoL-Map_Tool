#!/usr/bin/env python3

import sys
from app.application import App


def main():
    app = App(sys.argv)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
