import os

import uvicorn

from app.config import get_settings


def main():
    s = get_settings()

    reload = bool(s.reload)

    uvicorn.run(
        "app.main:app",
        host=s.host,
        port=s.port,
        log_level=s.log_level.lower(),
        reload=s.reload,
        access_log=True,
    )


if __name__ == "__main__":
    main()