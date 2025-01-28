from tbint_logger import tbint_logger

logger = tbint_logger.Logger()

logger.error_sync(
    tbint_logger.Data(
        description="This is a test",
    )
)
