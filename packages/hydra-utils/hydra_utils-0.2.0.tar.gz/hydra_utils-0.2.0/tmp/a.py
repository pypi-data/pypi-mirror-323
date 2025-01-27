#!/usr/bin/env python

import hydra
from hydra_utils import hydra_wrapper


#@hydra.main(config_path="conf", config_name="config", version_base="1.2")
#@hydra.main(config_path="conf", config_name="config", version_base="1.2")
#@hydra_wrapper(config_path="conf", config_name="config", version_base='1.2')

@hydra_wrapper(config_path="conf", config_name="config", version_base='1.2')
def my_app(cfg):
    print(cfg)


if __name__ == "__main__":
    my_app()
