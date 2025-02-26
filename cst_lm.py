#!/usr/bin/env python3
# CST-LM: Custom Language Model for Cosmic Synapse Theory
# Description: A lightweight, multimodal LLM that learns from everything.

import torch
import torch.nn as nn
import json
import logging
from torch.nn.utils.rnn import pad_sequence

logger = logging.getLogger("CST_LM")

# Simple Transformer Model
class CSTLM(nn.Module):
    def __init__(self, device, vocab_size=10000, embed_dim=128, num_heads=4, num_layers=2):
        super(CSTLM, self).__init__()
        self.device = device
        self.embedding = nn.Embedding(vocab_size, embed_dim)
        self.transformer = nn.Transformer(embed_dim, num_heads, num_layers)
        self.fc = nn.Linear(embed_dim, vocab_size)
        self.to(device)

        self.vocab = {"<PAD>": 0, "<UNK>": 1}
        self.vocab_size = vocab_size
        self.memory = []
        self.state_file = "cst_lm_state.json"
        self.load_state()

    def forward(self, x):
        x = self.embedding(x)
        x = self.transformer(x, x)
        return self.fc(x)

    def learn(self, data, type="text"):
        if type == "text":
            tokens = self.tokenize(data)
        elif type == "gesture":
            tokens = self.tokenize_gesture(data)
        elif type == "pose":
            tokens = self.tokenize_pose(data)
        else:
            tokens = [self.vocab.get("<UNK>", 1)]
        self.memory.append({"type": type, "tokens": tokens})
        if len(self.memory) > 1000:  # Limit memory size
            self.memory.pop(0)

    def tokenize(self, text):
        words = text.lower().split()
        tokens = []
        for w in words:
            if len(self.vocab) < self.vocab_size:
                self.vocab[w] = self.vocab.get(w, len(self.vocab))
            tokens.append(self.vocab.get(w, self.vocab["<UNK>"]))
        return tokens

    def tokenize_gesture(self, gesture):
        token = f"GESTURE_{gesture['type']}_{int(gesture['x'])}_{int(gesture['y'])}"
        self.vocab[token] = self.vocab.get(token, len(self.vocab))
        return [self.vocab[token]]

    def tokenize_pose(self, landmarks):
        tokens = []
        for lm in landmarks.landmark:
            token = f"POSE_{int(lm.x * 100)}_{int(lm.y * 100)}"
            self.vocab[token] = self.vocab.get(token, len(self.vocab))
            tokens.append(self.vocab[token])
        return tokens

    def generate(self, state):
        context = " ".join([f"{k}:{v}" for k, v in state.items()])
        tokens = self.tokenize(context)
        input_tensor = torch.tensor(tokens, dtype=torch.long).unsqueeze(0).to(self.device)
        with torch.no_grad():
            output = self.forward(input_tensor)
            pred = torch.argmax(output, dim=-1)
        resp = {"create_token": np.random.random() > 0.5}
        if "freq" in state and state["freq"] > 200:
            resp["remove"] = True
        return resp

    def learn_gesture(self, gesture):
        self.learn(gesture, "gesture")

    def learn_pose(self, pose):
        self.learn(pose, "pose")

    def save_state(self):
        state = {"vocab": self.vocab, "memory": self.memory}
        with open(self.state_file, "w") as f:
            json.dump(state, f)
        logger.info("CST-LM state saved.")

    def load_state(self):
        if os.path.exists(self.state_file):
            with open(self.state_file, "r") as f:
                state = json.load(f)
            self.vocab = state.get("vocab", self.vocab)
            self.memory = state.get("memory", self.memory)
            logger.info("CST-LM state loaded.")