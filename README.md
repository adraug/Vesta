# Vesta

![GitHub top language](https://img.shields.io/github/languages/top/adraug/vesta?style=plastic)
![Lines of code](https://img.shields.io/tokei/lines/github/adraug/vesta?style=plastic)
![GitHub release (latest by date)](https://img.shields.io/github/v/release/adraug/vesta?style=plastic)
![GitHub Release Date](https://img.shields.io/github/release-date/adraug/vesta)
![GitHub](https://img.shields.io/github/license/adraug/vesta?style=plastic)

![Docker Image Version (latest by date)](https://img.shields.io/docker/v/adraug/vesta?arch=amd64&style=plastic)
![Docker Image Size (latest by date)](https://img.shields.io/docker/image-size/adraug/vesta)

![Developpers][developpers-shield]
[![Adrien][adrien-shield]][adrien-url]
[![Lucie][lucie-shield]][lucie-url]

![Confiance][confiance-shield]
[![GravenDev][gravendev-shield]][gravendev-url]

Vesta est un bot discord avec des fonctionnalitées assez spécifiques, mais non proposées par d'autres.

Rename automatiquement les gens ayant un pseudo impossible à mentionner, pouvoir faire des présentations qui pourront être vérifiées par le staff avant d'être postées dans un salon prédéfini, ainsi que la possibilité pour le staff de créer des slash commands custom pour le serveur.

## Lancer le bot

Il faudra de toute façon avoir une base de donnée postgres

### En baremetal

Tout d'abord, il faut télécharger le code

```bash
$ git clone https://github.com/adraug/Vesta
$ cd Vesta
```

Ensuite, il faut potentiellement installer les dépendances

```bash
$ pip install requirements.txt
```

Et enfin, vous pouvez lancer le code

```bash
$ python -m vesta --token "Your token" --postgres "Postgresql database url"
```

### Avec l'image docker

Si vous souhaitez passer par l'image docker, vous pouvez lancer le bot avec

```bash
$ docker run -d \
  -e TOKEN=<your_token> \
  -e POSTGRES_USER=<your_postgres_user> \
  -e POSTGRES_PASSWORD=<your_postgres_password> \
  -e POSTGRES_DATABASE=<your_postgres_database> \
  -e LOGGING_LEVEL=<logging_level> \
  vesta:latest
```

ou avec docker-compose

```yml 
version: '3.5'

services:

  vesta:
    image: vesta:latest

    environment:
      TOKEN: <your token>
      POSTGRES_USER: <your_postgres_user>
      POSTGRES_PASSWORD: <your_postgres_password>
      POSTGRES_DATABASE: <your_postgres_database>
      LOGGING_LEVEL: <your desired logging level>
```

## Utilisations

Voici les fonctionnalités qu'il y a actuellement sur Vesta :

### Nick
- Par défaut, renomme les gens par un pseudo random si ils join ou renomment d'eux-même avec un truc invalide pour le bot, sauf si il a un rôle staff. 
- `/nickname "name"` pour changer de pseudo, suivant une regex
- `/nickmanage ban *user*` pour empêcher un utilisateur de se nickname (staff)
- `/nickmanage unban *user*` pour re-permettre à un utilisateur de se nickname (staff)
- `/nickmanage list` pour voir la liste des personnes bannies du système de nickname (staff)
### Presentation
- `/presentation` Permet de créer une présentation (ouvre un modal)
- `/presentationmanage ban *user*` pour empêcher un utilisateur de poster des présentations (staff)
- `/presentationmanage unban *user*` pour re-permettre à un utilisateur de poster des présentations (staff)
- `/presentationmanage list` pour voir la liste des personnes bannies du système de présentations (staff)
### Custom
- `Clique droit sur un message => Applications => Create Custom Command` permet de transformer un message en une slash command pour le serveur (ouvre un modal) (staff)
- `/custom add "name"` permet de créer un message en slash command pour le serveur (ouvre un modal) (staff)
- `/custom remove "name"` supprime une slash commande personnalisée du serveur (staff)
- `/custom list` affiche la liste des slash commands du serveur (staff)

[developpers-shield]: https://img.shields.io/badge/-Developpers-555?style=plastic

[adrien-shield]: https://img.shields.io/badge/-Adrien-66AADD?style=plastic&logo=Github
[adrien-url]: https://github.com/adraug

[lucie-shield]: https://img.shields.io/badge/-Lucie-66AADD?style=plastic&logo=Github
[lucie-url]: https://github.com/Astremy

[confiance-shield]: https://img.shields.io/badge/-Ils%20nous%20font%20confiance-555?style=plastic

[gravendev-shield]: https://img.shields.io/badge/-GravenDev-555?style=plastic&logo=data:image/svg+xml;base64,PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0iVVRGLTgiPz48c3ZnIGlkPSJMYXllcl8xIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCA1MDUuMDIgNTYzLjEiPjxkZWZzPjxzdHlsZT4uY2xzLTF7ZmlsbDojZjE5OTBlO30uY2xzLTEsLmNscy0ye3N0cm9rZTojMjMxZjIwO3N0cm9rZS1taXRlcmxpbWl0OjEwO3N0cm9rZS13aWR0aDo1cHg7fS5jbHMtMntmaWxsOiNmZmY7fTwvc3R5bGU+PC9kZWZzPjxwYXRoIGNsYXNzPSJjbHMtMiIgZD0iTTIuNTIsMjYyLjNjLTMuNTYsMzkxLjc4LDQwNC44OSwzMjIuNDQsNTAwLDIxMnYtMTgxLjMzbC0xMTYtLjYydjEyOS4yOUMyNjQuMTgsNDg1LjYsNjUuMzIsNDYzLjU3LDIuNTIsMjYyLjNaIi8+PHBhdGggY2xhc3M9ImNscy0xIiBkPSJNMTA1Ljg0LDMwNi45N2MtMTAtMjEwLjY3LDE2Mi42Ny0yNDAsMjkwLTE0MS4zM2w2My4zMy04My4zM0MxOTkuMTgtMTIyLjM2LTYxLjQ5LDEwOC4zLDEwNS44NCwzMDYuOTdaIi8+PC9zdmc+
[gravendev-url]: https://discord.gg/graven
