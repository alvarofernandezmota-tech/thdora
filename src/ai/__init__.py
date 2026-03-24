"""
Módulo IA de THDORA.

Gestiona la integración con Ollama para IA local privada.

Hardware objetivo:
    GPU:  NVIDIA GTX 1060 6GB VRAM
    RAM:  16GB
    OS:   WSL2 (Ubuntu) con CUDA
    Modelo: mistral-nemo:12b (offload híbrido GPU+CPU)

Config Ollama recomendada::

    export OLLAMA_NUM_GPU=35
    export OLLAMA_GPU_OVERHEAD=200
    export OLLAMA_MAX_LOADED_MODELS=1
    ollama run mistral-nemo:12b

Submódulos planificados (Fase 8-9):
    ollama_client.py    → cliente HTTP para Ollama
    training/           → scripts de fine-tuning con datos propios
    datasets/           → datasets para entrenamiento
"""
