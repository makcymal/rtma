import logging
import uvicorn


if __name__ == "__main__":
    logging.basicConfig(
        filename="rtma-backen.log",
        level=logging.DEBUG,
        format="%(levelname)s:%(asctime)s - %(module)s:%(lineno)s - %(message)s",
        datefmt="%H:%M:%S",
    )
    uvicorn.run("main:app", host="127.0.0.1", port=8082, log_level="info", reload=True)
    
