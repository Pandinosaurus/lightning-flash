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
from flash.audio import SpeechRecognition, SpeechRecognitionData
from flash.core.data.utils import download_data

# # 1. Create the DataModule
download_data("https://pl-flash-data.s3.amazonaws.com/timit_data.zip", "./data")

datamodule = SpeechRecognitionData.from_json(
    input_fields="file",
    target_fields="text",
    train_file="data/timit/train.json",
    test_file="data/timit/test.json",
)

# 2. Build the task
model = SpeechRecognition(backbone="facebook/wav2vec2-base-960h")

# 3. Create the trainer and finetune the model
trainer = flash.Trainer(max_epochs=1, limit_train_batches=1, limit_test_batches=1)
trainer.finetune(model, datamodule=datamodule, strategy='no_freeze')

# 4. Predict on audio files!
predictions = model.predict(["data/timit/example.wav"])
print(predictions)

# 5. Save the model!
trainer.save_checkpoint("speech_recognition_model.pt")
