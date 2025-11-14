from __future__ import annotations

import sys
from pathlib import Path

import hydra
from omegaconf import DictConfig, OmegaConf

CURRENT_DIR = Path(__file__).resolve().parent
SRC_DIR = CURRENT_DIR.parent
for path in {CURRENT_DIR, SRC_DIR}:
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

import week7.dash_app as dash_app  # noqa: E402


@hydra.main(version_base=None, config_path="../../conf", config_name="week7")
def main(cfg: DictConfig) -> None:
    print("=== Week7 Hydra 설정 ===")
    print(OmegaConf.to_yaml(cfg, resolve=True))

    dash_app.API_ENDPOINT = cfg.ui.api_endpoint
    dash_app.app.run(
        host=cfg.ui.host,
        port=int(cfg.ui.port),
        debug=bool(cfg.ui.debug),
    )


if __name__ == "__main__":
    main()