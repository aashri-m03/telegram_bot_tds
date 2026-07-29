from huggingface_hub import HfApi
import os

api = HfApi(
    token=os.getenv("HF_TOKEN")
)

models = api.list_models(
    pipeline_tag="text-generation",
    limit=20
)

for model in models:
    print(model.id)