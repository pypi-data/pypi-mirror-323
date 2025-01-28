# Helloensai

Projet hello minimal pour packaging python au format .whl et envoi sur le dépôt Pypi. https://pypi.org/

Cours disponible ici : https://conception-logicielle.abrunetti.fr/

## Pour créer ce package

1. Utilisation de poetry pour l'installation simplifiée d'un package a distribué (création facilitée du pyproject.toml)
2. `poetry build` pour créer le fichier au format `.whl` 
3. Sur Pypi.org, création d'un compte, création d'un projet, création d'un token d'API
4. Configuration du token côté client poetry : `poetry config pypi-token.pypi LETOKENQUEVOUSAVEZRECUPERE`
5. `poetry publish` qui va envoyer le livrable sur `helloensai` par rapport a ce qui a été configuré sur le pyproject.toml et avec la valeur par défaut pypi

## Pour utiliser ce package

Depuis un environnement qui a python et pip d'installé

```
pip install helloensai
python -m helloensai
```
