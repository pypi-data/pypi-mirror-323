<img src="static/Marianne.png" alt="Marianne" width="150"/>

# Olympiabhub

Olympiabhub est une librairie Python pour interagir avec l'API Olympia, compatible avec le format OpenAI.

## Installation

```sh
pip install olympiabhub
```

## Configuration

1. Ajouter votre token API :
   - Via variable d'environnement : `OLYMPIA_API_TOKEN` ou `OLYMPIA_API_KEY` dans votre `.env`
   - Ou directement dans le code : `token="votre-token"`

2. Pour utiliser via Nubonyxia, ajouter la variable dans votre `.env` :
```
PROXY=127.0.0.1:8080  # Format: IP:PORT
```

## Utilisation

### Chat Completions

```python
from olympiabhub import OlympiaAPI
from dotenv import load_dotenv

load_dotenv()

# Initialisation
api = OlympiaAPI(model="llama3.1")

# Format de messages façon OpenAI
messages = [
    {"role": "system", "content": "Tu es un assistant utile et concis."},
    {"role": "user", "content": "Explique-moi ce qu'est l'effet de serre en une phrase."}
]

# Sans proxy
response = api.chat_completion(
    messages=messages,
    temperature=0.7,
    max_tokens=500
)
# Afficher la réponse
print(response['choices'][0]['message']['content'])

# Avec proxy Nubonyxia
response = api.chat_completion_nubonyxia(
    messages=messages,
    temperature=0.7,
    max_tokens=500
)
# Afficher la réponse
print(response['choices'][0]['message']['content'])
```

### Completions (texte simple)

```python
# Sans proxy
response = api.completion(
    prompt="Explique-moi comment fonctionne la photosynthèse.",
    temperature=0.7,
    max_tokens=500
)
# Afficher la réponse
print(response['choices'][0]['text'])

# Avec proxy Nubonyxia
response = api.completion_nubonyxia(
    prompt="Explique-moi comment fonctionne la photosynthèse.",
    temperature=0.7,
    max_tokens=500
)
# Afficher la réponse
print(response['choices'][0]['text'])
```

### Embeddings

```python
# Création d'embeddings pour une liste de textes
texts = [
    "Premier texte à encoder",
    "Second texte à encoder"
]

# Sans proxy
embeddings = api.embedding(texts=texts)
# Afficher les embeddings
for i, embedding in enumerate(embeddings['data']):
    print(f"Embedding {i+1}:", embedding['embedding'][:5], "...") # Affiche les 5 premières valeurs

# Avec proxy Nubonyxia
embeddings = api.embedding_nubonyxia(texts=texts)
# Afficher les embeddings
for i, embedding in enumerate(embeddings['data']):
    print(f"Embedding {i+1}:", embedding['embedding'][:5], "...") # Affiche les 5 premières valeurs
```

### Liste des modèles disponibles

```python
# Obtenir la liste des modèles LLM
# Sans proxy
llm_models = api.get_llm_models()
print("Modèles LLM disponibles:", llm_models)

# Avec proxy Nubonyxia
llm_models = api.get_llm_models_nubonyxia()
print("Modèles LLM disponibles:", llm_models)

# Obtenir la liste des modèles d'embedding
# Sans proxy
embedding_models = api.get_embedding_models()
print("Modèles d'embedding disponibles:", embedding_models)

# Avec proxy Nubonyxia
embedding_models = api.get_embedding_models_nubonyxia()
print("Modèles d'embedding disponibles:", embedding_models)
```

## Paramètres disponibles

### Chat Completion et Completion

| Paramètre | Type | Défaut | Description |
|-----------|------|---------|-------------|
| temperature | float | 0.7 | Contrôle la créativité (0 = déterministe, 1 = créatif) |
| max_tokens | int | 500 | Nombre maximum de tokens dans la réponse |
| top_p | float | 1.0 | Contrôle la diversité des réponses |
| n | int | 1 | Nombre de réponses à générer |
| stream | bool | False | Activer le streaming de la réponse |
| frequency_penalty | float | 0 | Pénalité pour la répétition de fréquence |
| presence_penalty | float | 0 | Pénalité pour la répétition de présence |

## Configuration avancée

Vous pouvez personnaliser l'URL de base et le User-Agent :

```python
api = OlympiaAPI(
    model="llama3.1",
    token="votre-token",
    base_url="https://votre-url-api.com",
    user_agent="Votre-User-Agent"
)
```