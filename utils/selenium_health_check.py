import json
import urllib.request
import logging


def selenium_health_check(remote_addr: str, timeout: int = 5) -> bool:
    logger = logging.getLogger(__name__)
    url = f"{remote_addr.rstrip('/')}/status"

    logger.info("Selenium health check started: %s", url)

    try:
        with urllib.request.urlopen(url, timeout=timeout) as response:
            payload = json.loads(response.read().decode())

        ready = payload.get("value", {}).get("ready", False)

        if ready:
            logger.info("Selenium Grid is READY")
            return True

        logger.info("Selenium Grid is NOT ready: %s", payload)
        return False

    except Exception as e:
        logger.info("Selenium health check failed: %s", e)
        return False
