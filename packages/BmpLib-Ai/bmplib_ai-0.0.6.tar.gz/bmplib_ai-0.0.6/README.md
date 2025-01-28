# BmpLib-Ai

**BmpLib-Ai** est une bibliothèque Python intelligente et sur-mesure conçue pour simplifier et enrichir la consommation de contenu de presse écrite. Elle intègre des outils d'analyse avancés pour générer des résumés, des conversions texte-audio et une interaction via un chatbot.

## Fonctionnalités principales :

- **Formats courts et simplifiés** : Obtenez des résumés clairs et précis en quelques secondes.
- **Formats diversifiés** : Transformez vos articles en texte ou en audio.
- **Playlists personnalisées** : Créez des collections audio de vos résumés préférés.
- **Chatbot interactif** : Posez des questions sur un article et recevez des réponses adaptées.

## Installation

Pour installer la bibliothèque, exécutez la commande suivante :

```python
pip install BmpLib-Ai
```

[GitHub Page](https://github.com/Taoufiq-Ouedraogo/Brief-My-Press-AI-Library)

[Pypi Page](https://pypi.org/project/BmpLib-Ai/)


[API Streamlit du Package Page](https://brief-my-press-ai.streamlit.app/Use_Python_API)



[Tuto on how to publish python package](https://packaging.python.org/en/latest/tutorials/packaging-projects/)

Pour chaque version:
- python3 -m build

- twine upload dist/*
- twine upload --skip-existing dist/*


## Exemple d’utilisation

```python
import BmpLib_Ai as bmp
```


### Résumés des articles

```python
# Contenu de l'article et ID du média
text = "L'intelligence artificielle transforme de nombreux secteurs en facilitant les processus analytiques."
media_id = "bmp_media1"

# Création de l'objet BMP
bmp_object = bmp.get_BMP_Article_Object(text, media_id)

# Obtenir les résumés
extractive_summary, abstractive_summary = bmp_object.get_summaries()

# Générer les audios
extractive_audio, abstractive_audio = bmp_object.get_audios()

# Poser une question sur l'article via le chatbot
response = bmp_object.chat_with_question("Quel est le sujet principal de cet article ?")
print("Réponse du chatbot :", response)
```

### Gestions des audios
```python
# Résultats
extractiveAudioBuffer, abstractiveAudioBuffer = bmp_object.get_audios()
        
# Enregistrement du buffer audio en MP3
with open("audio_extractif.mp3", "wb") as f:
    f.write(extractiveAudioBuffer.read())

with open("audio_abstractif.mp3", "wb") as f:
    f.write(abstractiveAudioBuffer.read())
```


### Interaction avec le Chatbot
```python
question = "De quoi parle cet article ?"
response = bmp_object.chat_with_question(question)
print("Réponse :", response)
```






## Auteur

Taoufiq Ouedraogo