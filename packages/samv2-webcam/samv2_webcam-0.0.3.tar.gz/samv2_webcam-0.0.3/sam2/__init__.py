# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.

# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.

from hydra import initialize

from .build_sam import load_model

initialize("configs", version_base="1.2")
