# Helloensai

Projet hello minimal pour packaging python au format .whl et envoi sur le dépôt Pypi. https://pypi.org/

Cours disponible ici : https://conception-logicielle.abrunetti.fr/

## Pour créer ce package

1. Utilisation de poetry pour l'installation simplifiée d'un package a distribué (création facilitée du pyproject.toml)
2. `poetry build` pour créer le fichier au format `.whl` 
3. Sur Pypi.org, création d'un compte, création d'un projet, création d'un token d'API
4. `poetry publish --build --repository conception-logicielle`