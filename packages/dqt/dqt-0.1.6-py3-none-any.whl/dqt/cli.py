import click
from loguru import logger


@click.command()
def run():
    logger.info("Checking data quality...")


if __name__ == "__main__":
    main()
