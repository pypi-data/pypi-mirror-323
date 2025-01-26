import click
from loguru import logger


@click.command()
def main():
    logger.info("Hello, dqt!")


if __name__ == "__main__":
    main()
