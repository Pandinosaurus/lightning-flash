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
import flash
from flash.core.utilities.imports import _TORCH_GEOMETRIC_AVAILABLE
from flash.graph.classification.data import GraphClassificationData
from flash.graph.classification.model import GraphClassifier

if _TORCH_GEOMETRIC_AVAILABLE:
    from torch_geometric.datasets import TUDataset
else:
    raise ModuleNotFoundError("Please, pip install -e '.[graph]'")

# 1. Create the DataModule
dataset = TUDataset(root="data", name="KKI")

datamodule = GraphClassificationData.from_datasets(
    train_dataset=dataset,
    val_split=0.1,
)

# 2. Build the task
model = GraphClassifier(num_features=datamodule.num_features, num_classes=datamodule.num_classes)

# 3. Create the trainer and fit the model
trainer = flash.Trainer(max_epochs=3)
trainer.fit(model, datamodule=datamodule)

# 4. Classify some graphs!
predictions = model.predict(dataset[:3])
print(predictions)

# 5. Save the model!
trainer.save_checkpoint("graph_classification.pt")
