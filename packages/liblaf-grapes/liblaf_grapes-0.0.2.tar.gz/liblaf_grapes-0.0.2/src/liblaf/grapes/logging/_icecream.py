from loguru import logger

from liblaf import grapes


def init_icecream() -> None:
    if not grapes.has_module("icecream"):
        return
    from icecream import ic

    ic.configureOutput(
        prefix="", outputFunction=lambda s: logger.opt(depth=2).log("ICECREAM", s)
    )
