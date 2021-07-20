# Copyright The PyTorch Lightning team.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from os.path import join

import pytest
import torch
from pytorch_lightning import seed_everything

from flash import Trainer
from flash.core.data.data_source import DefaultDataKeys
from flash.core.data.utils import download_data
from flash.pointcloud.segmentation import PointCloudSegmentation, PointCloudSegmentationData
from tests.helpers.utils import _POINTCLOUD_TESTING


@pytest.mark.skipif(not _POINTCLOUD_TESTING, reason="pointcloud libraries aren't installed")
def test_pointcloud_segmentation_data(tmpdir):

    seed_everything(52)

    download_data("https://pl-flash-data.s3.amazonaws.com/SemanticKittiMicro.zip", tmpdir)

    dm = PointCloudSegmentationData.from_folders(train_folder=join(tmpdir, "SemanticKittiMicro", "train"), )

    class MockModel(PointCloudSegmentation):

        def training_step(self, batch, batch_idx: int):
            assert batch[DefaultDataKeys.INPUT]["xyz"][0].shape == torch.Size([2, 45056, 3])
            assert batch[DefaultDataKeys.INPUT]["xyz"][1].shape == torch.Size([2, 11264, 3])
            assert batch[DefaultDataKeys.INPUT]["xyz"][2].shape == torch.Size([2, 2816, 3])
            assert batch[DefaultDataKeys.INPUT]["xyz"][3].shape == torch.Size([2, 704, 3])
            assert batch[DefaultDataKeys.INPUT]["labels"].shape == torch.Size([2, 45056])
            assert batch[DefaultDataKeys.INPUT]["labels"].max() == 19
            assert batch[DefaultDataKeys.INPUT]["labels"].min() == 0
            assert batch[DefaultDataKeys.METADATA][0]["name"] == '00_000000'
            assert batch[DefaultDataKeys.METADATA][1]["name"] == '00_000001'

    num_classes = 19
    model = MockModel(backbone="randlanet", num_classes=num_classes)
    trainer = Trainer(max_epochs=1, limit_train_batches=1, limit_val_batches=0)
    trainer.fit(model, dm)

    predictions = model.predict(join(tmpdir, "SemanticKittiMicro", "predict"))
    assert torch.stack(predictions[0][DefaultDataKeys.INPUT]).shape == torch.Size([45056, 3])
    assert torch.stack(predictions[0][DefaultDataKeys.PREDS]).shape == torch.Size([45056, 19])
    assert torch.stack(predictions[0][DefaultDataKeys.TARGET]).shape == torch.Size([45056])
