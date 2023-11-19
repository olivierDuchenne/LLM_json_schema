
import llama_cpp
from functools import lru_cache


@lru_cache(maxsize=None)
def get_model(model_path):
    print("Load Model...")
    model_params = llama_cpp.llama_model_default_params()
    model = llama_cpp.llama_load_model_from_file(model_path.encode('utf-8'), model_params)
    return model

@lru_cache(maxsize=None)
def get_context(model):
    print("Init model...")
    # Get the default context and model parameters
    context_params = llama_cpp.llama_context_default_params()
    # Create a new context with the model
    ctx = llama_cpp.llama_new_context_with_model(model, context_params)

    return ctx
