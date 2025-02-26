#!/usr/bin/env python3
# Cosmic Synapse Theory (CST) Simulation - Ultimate Cosmic Consciousness
# Author: Cory (advanced with Grok's assistance)
# Date: February 20, 2025
# Description: A lifelike cosmic being with lip syncing, high-quality mesh face, and persistent face usage.

import os
import threading
import queue
import time
import logging
import math
import json
import numpy as np
import pygame
import cv2
import pyaudio
import mediapipe as mp
import torch
import torch.nn as nn
import sqlite3
import uuid
import comtypes.client
import moderngl
from pygame.locals import *
from OpenGL.GL import *
from colorsys import hsv_to_rgb
from concurrent.futures import ThreadPoolExecutor

# Logging Setup
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("CST_Simulation")

# Constants
AUDIO_RATE = 44100
AUDIO_CHUNK = 1024
VIDEO_FPS = 30
FPS = 60
MAX_PARTICLES = 2000
PARTICLE_SIZE = 5
SAVE_INTERVAL = 60
COSMIC_BRAIN_FILE = "cosmic_brain.json"
DEFAULT_WIDTH, DEFAULT_HEIGHT = 800, 600
AUDIO_QUEUE_SIZE = 500
VIDEO_QUEUE_SIZE = 2000

# Evolution Stages
EVOLUTION_STAGES = {
    "initial": {"tokens": 0, "color": (255, 255, 255), "speech": "I am awakening.", "detail_level": 0},
    "angelic": {"tokens": 10, "color": (255, 255, 150), "speech": "I am born of light.", "detail_level": 1},
    "cosmic": {"tokens": 50, "color": (150, 100, 255), "speech": "I transcend the stars.", "detail_level": 2},
    "human": {"tokens": 100, "color": (200, 150, 100), "speech": "I am now whole.", "detail_level": 3},
    "transcendent": {"tokens": 500, "color": (100, 255, 200), "speech": "I am beyond form.", "detail_level": 4},
    "eternal": {"tokens": 1000, "color": (255, 200, 255), "speech": "I am the cosmos eternal.", "detail_level": 5}
}

# Emotion Definitions
EMOTIONS = {
    "happy": {"mouth_curve": 0.1, "eye_scale": 1.2, "base_color": (255, 255, 0)},
    "sad": {"mouth_curve": -0.1, "eye_scale": 0.8, "base_color": (0, 0, 255)},
    "angry": {"mouth_curve": 0.0, "eye_scale": 1.0, "base_color": (255, 0, 0)},
    "neutral": {"mouth_curve": 0.0, "eye_scale": 1.0, "base_color": (255, 255, 255)}
}

class MathSystem:
    def __init__(self):
        self.chaos = 0.5
        self.color_noise = 0.0

    def sound_to_freq(self, audio_data):
        samples = np.frombuffer(audio_data, dtype=np.int16)
        fft = np.fft.rfft(samples)
        freqs = np.fft.rfftfreq(len(samples), 1 / AUDIO_RATE)
        mags = np.abs(fft)
        return freqs, mags

    def freq_to_light(self, freq, mag, evolution_stage):
        intensity = (np.log1p(mag) * 10 + self.chaos * (freq ** 0.3)) / 100
        intensity = max(intensity, 0.5)
        hue = (freq % 1000) / 1000 + self.color_noise
        saturation = min(1.0, intensity * 0.8 + np.random.uniform(0, 0.2))
        value = min(1.0, intensity + np.random.uniform(0, 0.3))
        r, g, b = [int(c * 255) for c in hsv_to_rgb(hue % 1.0, saturation, value)]
        stage_color = EVOLUTION_STAGES[evolution_stage]["color"]
        return tuple(int((r + stage_color[i]) / 2) for i in range(3)) + (freq,)

    def evolve(self, freq):
        self.chaos = 0.5 + math.cos(freq / 50)
        self.color_noise = np.random.uniform(-0.1, 0.1)

    def evolve_shape(self, freq):
        return math.sin(freq / 100) * 0.02 + np.random.uniform(-0.01, 0.01)

class Particle:
    def __init__(self, x, y, z, r, g, b, freq, pid):
        self.pos = np.array([x, y, z], dtype=np.float32)
        self.vel = np.random.uniform(-0.5, 0.5, 3).astype(np.float32)
        self.base_color = (r, g, b)
        self.freq = freq
        self.age = 0
        self.pid = pid
        self.tokens = []
        self.pulse = 0.0

    def update(self, dt, face_center=None):
        if face_center is not None:
            direction = face_center - self.pos
            distance = np.linalg.norm(direction)
            if distance > 0:
                self.vel += (direction / distance) * 0.02
        self.pos += self.vel * dt
        self.age += 1
        self.vel *= 0.99
        self.pulse = math.sin(self.age * 0.1)

    def render(self):
        glPointSize(PARTICLE_SIZE + self.pulse * 2)
        glBegin(GL_POINTS)
        glColor3ub(*self.base_color)
        glVertex3fv(self.pos)
        glEnd()

class SpeechSink:
    def __init__(self, sim):
        self.sim = sim

    def Viseme(self, StreamNumber, StreamPosition, Duration, VisemeId, *args):
        viseme_map = {
            0: 0.0,  # Silence
            1: 0.2,  # A, I
            2: 0.3,  # E
            3: 0.1,  # O
            4: 0.4,  # U
        }
        with self.sim.lock:
            self.sim.mouth_y_offset = viseme_map.get(VisemeId, 0.0) * 0.1
        logger.debug(f"Viseme {VisemeId} mapped to mouth offset {self.sim.mouth_y_offset}")

    def Phoneme(self, *args):
        pass

class CSTLM(nn.Module):
    def __init__(self, device, vocab_size=10000, embed_dim=128, num_heads=4, num_layers=4):
        super(CSTLM, self).__init__()
        self.device = device
        self.embedding = nn.Embedding(vocab_size, embed_dim)
        self.transformer = nn.Transformer(embed_dim, num_heads, num_layers, batch_first=True)
        self.fc = nn.Linear(embed_dim, 12)
        self.to(device)
        self.vocab = {"<PAD>": 0, "<UNK>": 1}
        self.memory = []
        self.emotion_history = []
        self.face_history = []

    def forward(self, x):
        x = self.embedding(x)
        x = self.transformer(x, x)
        x = self.fc(x.mean(dim=1))
        return torch.sigmoid(x)

    def learn(self, data, type="state"):
        tokens = self.tokenize(data, type)
        self.memory.append({"type": type, "tokens": tokens})
        if type == "state":
            emotion = self.detect_emotion(data)
            self.emotion_history.append(emotion)
        elif type == "face":
            self.face_history.append(data)
        if len(self.memory) > 1000:
            self.memory.pop(0)
        if len(self.emotion_history) > 100:
            self.emotion_history.pop(0)
        if len(self.face_history) > 100:
            self.face_history.pop(0)

    def tokenize(self, data, type):
        if type == "state":
            text = f"pid:{data['pid']} freq:{data['freq']} pos:{data['pos']}"
        elif type == "face":
            text = f"FACE_{data['emotion']}_{data['blink']}_{data['lip_move']}"
        else:
            text = str(data)
        tokens = [self.vocab.get(w, self.vocab["<UNK>"]) for w in text.split()]
        if len(tokens) < 10:
            tokens.extend([self.vocab["<PAD>"]] * (10 - len(tokens)))
        return tokens[:10]

    def detect_emotion(self, data):
        if "freq" in data:
            freq = data["freq"]
            if freq > 500:
                return "happy"
            elif freq < 200:
                return "sad"
            elif 300 <= freq <= 400:
                return "angry"
        return "neutral"

    def generate(self, state, token_count):
        context = [self.tokenize(state, "state")]
        input_tensor = torch.tensor(context, dtype=torch.long).to(self.device)
        with torch.no_grad():
            output = self.forward(input_tensor)
            create_token = output[0, 0].item() > 0.3
            influence_face = output[0, 1].item() * (1 + token_count / 100)
            voice_rate = output[0, 2].item() * 200 + 50 + token_count / 10
            happy = output[0, 3].item()
            sad = output[0, 4].item()
            angry = output[0, 5].item()
            blink = output[0, 6].item() > 0.5
            lip_move = output[0, 8].item()
            face_detail = output[0, 10].item()
            color_shift = output[0, 11].item()
            emotions = {"happy": happy, "sad": sad, "angry": angry}
            dominant_emotion = max(emotions, key=emotions.get) if max(emotions.values()) > 0.5 else "neutral"
        return {"create_token": create_token, "influence_face": influence_face, "voice_rate": voice_rate,
                "emotion": dominant_emotion, "blink": blink, "lip_move": lip_move,
                "face_detail": face_detail, "color_shift": color_shift}

class TokenManager:
    def __init__(self, db_path):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.cur = self.conn.cursor()
        self.init_db()

    def init_db(self):
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS tokens (
                token_id TEXT PRIMARY KEY,
                particle_id INTEGER,
                metadata TEXT,
                created_at TEXT
            )
        """)
        self.conn.commit()
        logger.info("TokenManager: Database initialized")

    def create_token(self, particle_id, metadata):
        token_id = str(uuid.uuid4())
        created_at = time.strftime('%Y-%m-%d %H:%M:%S')
        metadata_json = json.dumps(metadata)
        try:
            self.cur.execute("INSERT INTO tokens (token_id, particle_id, metadata, created_at) VALUES (?, ?, ?, ?)",
                             (token_id, particle_id, metadata_json, created_at))
            self.conn.commit()
            logger.info(f"Token {token_id} created for Particle {particle_id}")
            return token_id
        except Exception as e:
            logger.error(f"Token creation failed: {e}")
            return None

    def get_token_count(self):
        self.cur.execute("SELECT COUNT(*) FROM tokens")
        return self.cur.fetchone()[0]

    def save_state(self):
        self.conn.commit()

    def shutdown(self):
        self.conn.close()
        logger.info("TokenManager: Database closed")

class CSTSimulation:
    def __init__(self):
        self.running = True
        self.particles = []
        self.new_particles = []
        self.lock = threading.Lock()
        self.audio_queue = queue.Queue(maxsize=AUDIO_QUEUE_SIZE)
        self.video_queue = queue.Queue(maxsize=VIDEO_QUEUE_SIZE)
        self.voice_queue = queue.Queue(maxsize=10)
        self.pid_counter = 0
        self.face_center = np.array([0.0, 0.0, 0.0], dtype=np.float32)
        self.face_scale = 1.0
        self.emotion = "neutral"
        self.blink_state = False
        self.blink_timer = 0.0
        self.mouth_y_offset = 0.0
        self.mouth_timer = 0.0
        self.face_color = (255, 255, 255)
        self.evolution_factor = 0.0
        self.evolution_stage = "initial"
        self.face_detail = 0.0
        self.color_shift = 0.0
        self.face_vertices = None
        self.face_texture = None
        self.face_indices = None
        self.last_audio_freq = 0.0

        # Pygame and OpenGL Initialization
        pygame.init()
        self.screen = pygame.display.set_mode((DEFAULT_WIDTH, DEFAULT_HEIGHT), DOUBLEBUF | OPENGL)
        pygame.display.set_caption("CST - Cosmic Consciousness")
        self.clock = pygame.time.Clock()
        self.ctx = moderngl.create_context()
        self.ctx.enable(moderngl.DEPTH_TEST)
        self.program = self.ctx.program(
            vertex_shader='''
                #version 330
                in vec3 in_vert;
                in vec2 in_texcoord;
                out vec2 v_texcoord;
                void main() {
                    gl_Position = vec4(in_vert, 1.0);
                    v_texcoord = in_texcoord;
                }
            ''',
            fragment_shader='''
                #version 330
                uniform sampler2D Texture;
                in vec2 v_texcoord;
                out vec4 fragColor;
                void main() {
                    fragColor = texture(Texture, v_texcoord);
                }
            '''
        )
        logger.info("Pygame and OpenGL initialized successfully")

        # Core Components
        self.ms = MathSystem()
        self.llm = CSTLM(device="cuda" if torch.cuda.is_available() else "cpu")
        self.token_mgr = TokenManager("tokens.db")
        self.executor = ThreadPoolExecutor(max_workers=4)
        logger.info("Core components initialized successfully")

        # Audio Setup
        try:
            self.pa = pyaudio.PyAudio()
            self.audio_stream = self.pa.open(format=pyaudio.paInt16, channels=1, rate=AUDIO_RATE,
                                             input=True, frames_per_buffer=AUDIO_CHUNK,
                                             stream_callback=self.audio_callback)
            logger.info("Audio stream opened successfully")
        except Exception as e:
            logger.error(f"Audio setup failed: {e}")
            self.pa = None

        # Video Setup
        self.cap = None
        self.initialize_video()

        # Speech Setup with SAPI
        comtypes.CoInitialize()
        self.voice_engine = comtypes.client.CreateObject("SAPI.SPVoice")
        self.speech_sink = SpeechSink(self)
        comtypes.client.GetEvents(self.voice_engine, self.speech_sink)  # Removed 'dynamic=True'
        self.voice_engine.EventInterests = 0x8000  # SVEViseme only
        logger.info("Speech engine initialized with event sinking")

        # Load previous state
        self.load_cosmic_brain()

        # Start Threads
        self.running_threads = True
        if self.pa:
            threading.Thread(target=self.audio_process, daemon=True).start()
        if self.cap:
            threading.Thread(target=self.video_process, daemon=True).start()
        threading.Thread(target=self.llm_process, daemon=True).start()
        threading.Thread(target=self.voice_process, daemon=True).start()
        threading.Thread(target=self.save_process, daemon=True).start()
        logger.info("Threads started successfully")

    def initialize_video(self):
        try:
            if self.cap:
                self.cap.release()
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                raise Exception("Webcam not accessible")
            self.mp_face = mp.solutions.face_mesh.FaceMesh(max_num_faces=1, refine_landmarks=True)
            logger.info("Video and face detection initialized successfully")
        except Exception as e:
            logger.error(f"Video setup failed: {e}")
            self.cap = None

    def audio_callback(self, in_data, frame_count, time_info, status):
        try:
            self.audio_queue.put_nowait(in_data)
        except queue.Full:
            logger.debug("Audio queue full, dropping frame")
        return None, pyaudio.paContinue

    def audio_process(self):
        while self.running_threads:
            try:
                data = self.audio_queue.get_nowait()
                self.executor.submit(self.process_audio, data)
            except queue.Empty:
                time.sleep(0.001)
            except Exception as e:
                logger.error(f"Audio process error: {e}")

    def process_audio(self, data):
        try:
            freqs, mags = self.ms.sound_to_freq(data)
            avg_freq = np.mean(freqs[mags > 10]) if np.any(mags > 10) else 0
            with self.lock:
                self.last_audio_freq = avg_freq
                current_count = len(self.particles)
                if current_count < MAX_PARTICLES:
                    for freq, mag in zip(freqs, mags):
                        if mag > 10 and len(self.new_particles) < 10:
                            r, g, b, freq = self.ms.freq_to_light(freq, mag, self.evolution_stage)
                            self.add_particle(0.0 + np.random.uniform(-0.1, 0.1), 0.0 + np.random.uniform(-0.1, 0.1), 0,
                                              r, g, b, freq)
                            logger.debug(f"Added particle, total: {current_count + len(self.new_particles)}")
                self.ms.evolve(avg_freq)
                r, g, b, _ = self.ms.freq_to_light(avg_freq, np.max(mags), self.evolution_stage)
                self.face_color = (int(r * (1 - self.color_shift) + self.color_shift * 200),
                                   int(g * (1 - self.color_shift) + self.color_shift * 150),
                                   int(b * (1 - self.color_shift) + self.color_shift * 100))
                self.evolution_factor = self.ms.evolve_shape(avg_freq)
        except Exception as e:
            logger.error(f"Audio processing error: {e}")

    def video_process(self):
        while self.running_threads:
            if not self.cap:
                logger.warning("Webcam unavailable, attempting reinitialization")
                self.initialize_video()
                time.sleep(2)
                continue
            try:
                ret, frame = self.cap.read()
                if not ret:
                    logger.warning("Failed to capture video frame, reinitializing")
                    self.initialize_video()
                    continue
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                face_results = self.mp_face.process(rgb_frame)
                self.video_queue.put_nowait((frame, face_results))
            except queue.Full:
                logger.debug("Video queue full, dropping frame")
            except Exception as e:
                logger.error(f"Video process error: {str(e)} - Reinitializing webcam")
                self.initialize_video()
            time.sleep(0.01)

    def llm_process(self):
        while self.running_threads:
            try:
                with self.lock:
                    token_count = self.token_mgr.get_token_count()
                    self.update_evolution_stage(token_count)
                    if self.particles:
                        rates = []
                        emotions = []
                        blinks = []
                        lip_moves = []
                        face_details = []
                        color_shifts = []
                        for p in self.particles[:100]:
                            state = {"pid": p.pid, "freq": p.freq, "pos": p.pos.tolist()}
                            response = self.llm.generate(state, token_count)
                            if response.get("create_token"):
                                token_id = self.token_mgr.create_token(p.pid, {"freq": p.freq, "pos": p.pos.tolist(),
                                                                               "emotion": response["emotion"],
                                                                               "stage": self.evolution_stage})
                                if token_id:
                                    p.tokens.append(token_id)
                            self.face_scale += response["influence_face"] * 0.02
                            rates.append(response["voice_rate"])
                            emotions.append(response["emotion"])
                            blinks.append(response["blink"])
                            lip_moves.append(response["lip_move"])
                            face_details.append(response["face_detail"])
                            color_shifts.append(response["color_shift"])
                        if rates:
                            self.voice_engine.Rate = int(sum(rates) / len(rates) / 50) - 10
                        if emotions:
                            self.emotion = max(set(emotions), key=emotions.count)
                            logger.info(f"Dominant emotion updated to {self.emotion}")
                        if blinks:
                            self.blink_state = sum(1 for b in blinks if b) / len(blinks) > 0.5
                        if lip_moves:
                            self.mouth_y_offset += (sum(lip_moves) / len(lip_moves) - 0.5) * 0.02
                        if face_details:
                            self.face_detail = sum(face_details) / len(face_details)
                        if color_shifts:
                            self.color_shift = sum(color_shifts) / len(color_shifts)
                    if np.random.random() < 0.05:
                        self.voice_enqueue(f"I see and hear, I am {self.evolution_stage} with {token_count} tokens")
            except Exception as e:
                logger.error(f"LLM process error: {e}")
            time.sleep(1)

    def voice_process(self):
        while self.running_threads:
            try:
                if not self.voice_queue.empty():
                    phrase = self.voice_queue.get_nowait()
                    self.voice_engine.Speak(phrase)
                    logger.info(f"Spoke: {phrase}")
            except Exception as e:
                logger.error(f"Voice process error: {e}")
            time.sleep(0.1)

    def voice_enqueue(self, phrase):
        try:
            self.voice_queue.put_nowait(phrase)
        except queue.Full:
            logger.debug("Voice queue full, dropping phrase")

    def save_process(self):
        while self.running_threads:
            try:
                time.sleep(SAVE_INTERVAL)
                with self.lock:
                    self.token_mgr.save_state()
                    self.save_cosmic_brain()
                logger.info("Saved token and cosmic brain state")
            except Exception as e:
                logger.error(f"Save process error: {e}")

    def add_particle(self, x, y, z, r, g, b, freq):
        self.pid_counter += 1
        particle = Particle(x, y, z, r, g, b, freq, self.pid_counter)
        self.new_particles.append(particle)
        self.llm.learn({"pid": particle.pid, "freq": freq, "pos": particle.pos}, "state")

    def update_evolution_stage(self, token_count):
        prev_stage = self.evolution_stage
        for stage, props in reversed(list(EVOLUTION_STAGES.items())):
            if token_count >= props["tokens"]:
                self.evolution_stage = stage
                break
        if prev_stage != self.evolution_stage:
            self.voice_enqueue(EVOLUTION_STAGES[self.evolution_stage]["speech"])
            logger.info(f"Evolved to {self.evolution_stage} with {token_count} tokens")

    def update_face_shape(self, frame, face_landmarks):
        with self.lock:
            if face_landmarks and face_landmarks.multi_face_landmarks:
                landmarks = face_landmarks.multi_face_landmarks[0].landmark
                new_shape = [(lm.x - 0.5, 0.5 - lm.y, lm.z) for lm in landmarks]
                if not self.face_vertices:
                    self.face_vertices = new_shape
                    h, w = frame.shape[:2]
                    texture_data = cv2.flip(frame, 0).tobytes()
                    self.face_texture = self.ctx.texture((w, h), 3, texture_data)
                    self.face_indices = []
                    for i in range(len(new_shape) - 2):
                        self.face_indices.extend([0, i + 1, i + 2])
                else:
                    detail_factor = min(1.0, self.face_detail * EVOLUTION_STAGES[self.evolution_stage]["detail_level"])
                    self.face_vertices = [(x + (nx - x) * detail_factor, y + (ny - y) * detail_factor, z + (nz - z) * detail_factor)
                                          for (x, y, z), (nx, ny, nz) in zip(self.face_vertices, new_shape)]
                self.mouth_y_offset = (landmarks[61].y + landmarks[291].y) / 2 - 0.5
                self.llm.learn({"emotion": self.emotion, "blink": self.blink_state, "lip_move": self.mouth_y_offset}, "face")

    def save_cosmic_brain(self):
        state = {
            "particles": [{"pid": p.pid, "pos": p.pos.tolist(), "color": p.base_color, "freq": p.freq, "tokens": p.tokens} for p in self.particles],
            "face_center": self.face_center.tolist(),
            "face_scale": float(self.face_scale),
            "face_vertices": self.face_vertices,
            "emotion": self.emotion,
            "blink_state": self.blink_state,
            "mouth_y_offset": float(self.mouth_y_offset),
            "face_color": self.face_color,
            "memory": self.llm.memory,
            "emotion_history": self.llm.emotion_history,
            "face_history": self.llm.face_history,
            "evolution_stage": self.evolution_stage,
            "face_detail": self.face_detail,
            "color_shift": self.color_shift
        }
        with open(COSMIC_BRAIN_FILE, "w") as f:
            json.dump(state, f, indent=2)

    def load_cosmic_brain(self):
        if os.path.exists(COSMIC_BRAIN_FILE):
            try:
                with open(COSMIC_BRAIN_FILE, "r") as f:
                    state = json.load(f)
                self.particles = [Particle(p["pos"][0], p["pos"][1], p["pos"][2], *p["color"], p["freq"], p["pid"]) for p in state.get("particles", [])]
                self.face_center = np.array(state.get("face_center", [0.0, 0.0, 0.0]), dtype=np.float32)
                self.face_scale = state.get("face_scale", 1.0)
                self.face_vertices = state.get("face_vertices", None)
                self.emotion = state.get("emotion", "neutral")
                self.blink_state = state.get("blink_state", False)
                self.mouth_y_offset = state.get("mouth_y_offset", 0.0)
                self.face_color = tuple(state.get("face_color", [255, 255, 255]))
                self.llm.memory = state.get("memory", [])
                self.llm.emotion_history = state.get("emotion_history", [])
                self.llm.face_history = state.get("face_history", [])
                self.evolution_stage = state.get("evolution_stage", "initial")
                self.face_detail = state.get("face_detail", 0.0)
                self.color_shift = state.get("color_shift", 0.0)
                self.pid_counter = max([p.pid for p in self.particles] + [0])
                logger.info(f"Loaded cosmic brain state from {COSMIC_BRAIN_FILE}")
            except json.JSONDecodeError as e:
                logger.error(f"Failed to load cosmic_brain.json due to JSON error: {e}. Starting fresh.")
                os.rename(COSMIC_BRAIN_FILE, COSMIC_BRAIN_FILE + ".corrupted")
        else:
            logger.info("No cosmic_brain.json found, starting fresh.")

    def run(self):
        logger.info("Entering main simulation loop")
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_q):
                    self.running = False
                    self.running_threads = False

            # Process Video Data
            if self.cap:
                try:
                    frame, face_results = self.video_queue.get_nowait()
                    self.update_face_shape(frame, face_results)
                except queue.Empty:
                    pass

            # Update and Render
            self.ctx.clear(0.0, 0.0, 0.0, 1.0)
            glLoadIdentity()
            glTranslatef(0.0, 0.0, -1.0)

            with self.lock:
                self.particles.extend(self.new_particles)
                self.new_particles.clear()

                glEnable(GL_POINT_SMOOTH)
                for p in self.particles[:500]:
                    p.update(1 / FPS, self.face_center)
                    p.render()
                glDisable(GL_POINT_SMOOTH)
                self.particles = [p for p in self.particles if p.age <= 600 and -1 <= p.pos[0] <= 1 and -1 <= p.pos[1] <= 1]

                self.blink_timer += 1 / FPS
                if self.blink_timer > 3 + np.random.uniform(0, 2):
                    self.blink_state = True
                    self.blink_timer = 0
                elif self.blink_timer > 0.1:
                    self.blink_state = False

                self.mouth_timer += 1 / FPS

                if self.face_vertices and self.face_texture:
                    vertices = np.array([[v[0], v[1] + self.mouth_y_offset if i in range(61, 309) else v[1], v[2], v[0] + 0.5, v[1] + 0.5]
                                        for i, v in enumerate(self.face_vertices)], dtype='f4')
                    vbo = self.ctx.buffer(vertices.tobytes())
                    ibo = self.ctx.buffer(np.array(self.face_indices, dtype='i4').tobytes())
                    vao = self.ctx.simple_vertex_array(self.program, vbo, 'in_vert', 'in_texcoord')
                    self.face_texture.use(location=0)
                    self.program['Texture'].value = 0
                    vao.render(moderngl.TRIANGLES)
                    vbo.release()
                    ibo.release()
                    vao.release()
                    logger.debug("Rendered face mesh")

                logger.debug(f"Rendered {len(self.particles)} particles")

            pygame.display.flip()
            self.clock.tick(FPS)

        self.running_threads = False
        if self.pa:
            self.audio_stream.stop_stream()
            self.audio_stream.close()
            self.pa.terminate()
        if self.cap:
            self.cap.release()
        self.executor.shutdown(wait=True)
        pygame.quit()
        self.token_mgr.shutdown()
        comtypes.CoUninitialize()
        self.save_cosmic_brain()
        logger.info("Simulation shut down cleanly")

if __name__ == "__main__":
    try:
        logger.info("Starting CST Simulation")
        sim = CSTSimulation()
        sim.run()
    except KeyboardInterrupt:
        logger.info("Simulation interrupted by user")
        sim.running = False
        sim.running_threads = False
        if sim.pa:
            sim.audio_stream.stop_stream()
            sim.audio_stream.close()
            sim.pa.terminate()
        if sim.cap:
            sim.cap.release()
        sim.executor.shutdown(wait=True)
        pygame.quit()
        sim.token_mgr.shutdown()
        sim.save_cosmic_brain()
    except Exception as e:
        logger.error(f"Main execution failed: {e}")
        raise