"""
loader.py — Auto-discover and register feature modules.

Drop a new .py file (or package) into  app/modules/  that exposes a
FastAPI ``router`` and it will be picked up automatically on next restart.
If a module fails to import, the rest of the app keeps running.
"""
from __future__ import annotations

import importlib
import logging
import pkgutil
from pathlib import Path

logger = logging.getLogger("astro.loader")


def discover_and_load(app) -> dict:
    """
    Scan ``app/modules/`` for Python modules/packages.
    Each one must expose a ``router`` (FastAPI APIRouter).
    Returns a summary of what loaded and what failed.
    """
    modules_pkg = "app.modules"
    modules_dir = Path(__file__).resolve().parent / "modules"

    loaded: list[str] = []
    failed: list[dict] = []

    for finder, name, is_pkg in pkgutil.iter_modules([str(modules_dir)]):
        if name.startswith("_"):
            continue  # skip __init__, __pycache__, etc.

        module_path = f"{modules_pkg}.{name}"
        try:
            mod = importlib.import_module(module_path)
            router = getattr(mod, "router", None)
            if router is None:
                logger.warning("Module '%s' has no router attribute — skipped", name)
                continue
            app.include_router(router)
            loaded.append(name)
            logger.info("Loaded module: %s", name)
        except Exception as exc:
            failed.append({"module": name, "error": str(exc)})
            logger.error("Failed to load module '%s': %s", name, exc, exc_info=True)

    logger.info(
        "Module loading complete: %d loaded, %d failed", len(loaded), len(failed)
    )
    return {"loaded": loaded, "failed": failed}
