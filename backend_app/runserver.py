import uvicorn


if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host="127.0.0.1",
        port=8082,
        reload=True,
        log_config="logconf.yaml",
        log_level="debug",
    )
