"""
AI Trading Operating System
Main Entry Point
"""

from core.kernel import ApplicationKernel


def main() -> None:
    kernel = ApplicationKernel()
    kernel.run()


if __name__ == "__main__":
    main()