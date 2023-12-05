# Import necessary libraries
import ctypes
import os
from typing import List
from .model_utils import get_context, get_model
import sys
# Import the llama_cpp library
import llama_cpp
import re

def get_vocab(model) -> List[str]:
    vocab = []
    n_vocab = llama_cpp.llama_n_vocab(model)
    size = 32
    buffer = (ctypes.c_char * size)()
    for id in range(n_vocab):
        n = llama_cpp.llama_token_to_piece(
            model, llama_cpp.llama_token(id), buffer, size)
        vocab.append(buffer[:n])
    return vocab

def adjust_logits_based_on_suggestions(suggestions: List[str], logits, vocab: List[str], n_vocab: int):
    for v in range(n_vocab):
        word = vocab[v]
        for suggestion in suggestions:
            if isinstance(suggestion, re.Pattern):
                if suggestion.match(str(word)):
                    logits[v] += 5.0
                    break
                continue
            if len(word) > len(suggestion):
                continue
            # length = len(suggestion)
            length = min(len(word), len(suggestion))
            if length == 0:
                continue
            elif word[:length] == suggestion[:length]:
                # print(word)
                # print(logits[v])
                logits[v] += 5.0
                # print(logits[v])
                break
        else:
            logits[v] -= -5.0


def do_inference(prompt, model_path=None, model=None, ctx=None, completion_callback=None, verbose=True):
    if model is None and model_path is not None:
        model = get_model(model_path)
    if ctx is None and model is not None:
        ctx = get_context(model)
    vocab = get_vocab(model)
    # Determine the required inference memory per token
    tmp = [0, 1, 2, 3]
    n_past = 0
    llama_cpp.llama_eval(ctx, (llama_cpp.c_int * len(tmp))(*tmp), len(tmp), n_past)

    # Add a space to the beginning of the prompt
    prompt = b" " + prompt

    # Tokenize the prompt
    embd_inp = (llama_cpp.llama_token * (len(prompt) + 1))()
    n_of_tok = llama_cpp.llama_tokenize(model, prompt, len(prompt), embd_inp, len(embd_inp), True)
    embd_inp = embd_inp[:n_of_tok]

    # Get the number of context tokens
    n_ctx = llama_cpp.llama_n_ctx(ctx)

    # Define the number of tokens to predict
    n_predict = 200
    n_predict = min(n_predict, n_ctx - len(embd_inp))

    # Initialize variables
    input_consumed = 0
    input_noecho = False
    remaining_tokens = n_predict
    embd = []
    last_n_size = 64
    last_n_tokens_data = [0] * last_n_size
    n_batch = 24
    last_n_repeat = 64
    repeat_penalty = 1
    frequency_penalty = 0.0
    presence_penalty = 0.0

    auto_complete_suggestions = None
    history = ""
    # Main loop for token prediction
    while remaining_tokens > 0:
        # Evaluate the model with the current tokens
        if len(embd) > 0:
            llama_cpp.llama_eval(ctx, (llama_cpp.c_int * len(embd))(*embd), len(embd), n_past)
        n_past += len(embd)
        embd = []

        # Auto-completion
        if len(embd_inp) <= input_consumed and completion_callback is not None:
            # Compute the auto completions.
            auto_complete_suggestions = completion_callback(history)
            # If there is only one auto completion's suggestion, directly add it.
            there_is_one_suggestion = auto_complete_suggestions \
                and type(auto_complete_suggestions) is list \
                and len(auto_complete_suggestions) == 1 \
                and not isinstance(auto_complete_suggestions[0], re.Pattern)
            if there_is_one_suggestion:
                new_prompt = auto_complete_suggestions[0]
                embd_inp2 = (llama_cpp.llama_token * (len(new_prompt) + 1))()
                n_of_tok2 = llama_cpp.llama_tokenize(model, new_prompt, len(new_prompt), embd_inp2, len(embd_inp2), True)
                embd_inp2 = embd_inp2[:n_of_tok2]
                input_consumed = 0
                embd_inp = embd_inp2

        is_consuming_inputs = True
        # If all input tokens have been consumed, generate new tokens
        if len(embd_inp) <= input_consumed:
            is_consuming_inputs = False
            # Get the logits from the model
            logits = llama_cpp.llama_get_logits(ctx)            
            n_vocab = llama_cpp.llama_n_vocab(model)

            # If there is at least two auto-complete's suggestion
            # (one suggestion case is handle else where),
            #  adjust logits based on suggestions to make sure than one of the suggestion is chosen.
            if auto_complete_suggestions is not None and not there_is_one_suggestion:
                adjust_logits_based_on_suggestions(auto_complete_suggestions, logits, vocab, n_vocab)

            # Create an array of token data
            _arr = (llama_cpp.llama_token_data * n_vocab)(*[
                llama_cpp.llama_token_data(token_id, logits[token_id], 0.0)
                for token_id in range(n_vocab)
            ])
            candidates_p = llama_cpp.ctypes.pointer(
                llama_cpp.llama_token_data_array(_arr, len(_arr), False))

            # Apply penalties and sample tokens
            _arr = (llama_cpp.c_int * len(last_n_tokens_data))(*last_n_tokens_data)
            llama_cpp.llama_sample_repetition_penalty(ctx, candidates_p, _arr, last_n_repeat, repeat_penalty)
            llama_cpp.llama_sample_frequency_and_presence_penalties(ctx, candidates_p, _arr, last_n_repeat, frequency_penalty, presence_penalty)
            llama_cpp.llama_sample_top_k(ctx, candidates_p, k=40, min_keep=1)
            llama_cpp.llama_sample_top_p(ctx, candidates_p, p=0.8, min_keep=1)
            llama_cpp.llama_sample_temperature(ctx, candidates_p, temp=0.2)
            id = llama_cpp.llama_sample_token(ctx, candidates_p)

            # Update the tokens
            last_n_tokens_data = last_n_tokens_data[1:] + [id]
            embd.append(id)
            input_noecho = False
            remaining_tokens -= 1
        else:
            # If there are still input tokens, consume them
            while len(embd_inp) > input_consumed:
                embd.append(embd_inp[input_consumed])
                last_n_tokens_data = last_n_tokens_data[1:] + [embd_inp[input_consumed]]
                input_consumed += 1
                if len(embd) >= n_batch:
                    break

        # Print the generated tokens
        if not input_noecho:
            for id in embd:
                size = 32
                buffer = (ctypes.c_char * size)()
                n = llama_cpp.llama_token_to_piece(model, llama_cpp.llama_token(id), buffer, size)
                assert n <= size
                chunk = buffer[:n].decode('utf-8')
                # Yield chunks if they are not part of the input sequence.
                # If the chunk is part of an autocompletion it should be yield as well.
                if not is_consuming_inputs or auto_complete_suggestions is not None:
                    yield chunk
                if verbose:
                    print(chunk, end="", flush=True)
                sys.stdout.flush()
                history += buffer[:n].decode()

        # Break the loop if the end of sentence token is generated
        if len(embd) > 0 and embd[-1] == llama_cpp.llama_token_eos(ctx):
            break


    # Print the timings
    if verbose:
        llama_cpp.llama_print_timings(ctx)

    # return (history, model, ctx)


def do_completion(history: str):
    if history.endswith("aris"):
        return prompt2


if __name__ == "__main__":
    # Initialize the llama backend
    llama_cpp.llama_backend_init(numa=False)

    # Define the prompt
    # prompt = b"\n\n### Instruction:\nWhat is the capital of France?\n\n### Response:\n"
    # prompt2 = b"\n\n### Instruction:\nWhat is the capital of Russia?\n\n### Response:\n"
    prompt = b"\n\n### Instruction:\nWhat is the area of a square which size is 435.2m?\n\n### Response:\n"
    prompt2 = b"\n\n### Instruction:\nWhat is the capital of Russia?\n\n### Response:\n"

    # model = get_model(model_path=MODEL_PATH)
    # ctx = get_context(model)
    script_path = os.path.dirname(os.path.realpath(__file__))
    model_path=os.environ.get('MODEL_PATH', os.path.join(script_path, "../models/Mistral-7B-v0.1/ggml-model-f16.gguf"))
    (history, model, ctx) = do_inference(
        prompt=prompt,
        model_path=model_path,
        completion_callback=do_completion)

    # Free the context
    llama_cpp.llama_free(ctx)
