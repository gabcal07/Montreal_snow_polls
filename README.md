# Element de recherche opérationnelle

## Préparation de l'environnement d'execution

Avant de lancer le programme, exécutez les commandes suivantes pour installer toutes les bibliothèques nécessaires :

```bash
python3 -m venv env

source env/bin/activate

pip install -r requirements.txt
```

## Deneigeons ou Lançons un Drone

Après avoir installé les bibliothèques nécessaires avec la commande `requirements.txt`, procédez comme suit pour lancer le projet et commencer le déneigement à Montréal :

1. Accédez au répertoire source :
   ```bash
   cd src
   ```
2. Lancer le projet :
    ```bash
    python3 ero1.py
    ```
3. Une fois que vous avez terminé :
    ```bash
    cd ..
    
    deactivate

    rm -rf env
    ```

## Choisissez les Scénarios et les Villes

Une fois le programme lancé, sélectionnez les scénarios et les villes que vous souhaitez déneiger. Après que le programme ait fini de compiler, des fichiers `.html` seront générés dans le dossier de la ville choisie.

## Visualisation des Opérations

Pour visualiser le déneigement ou le passage du drone, ouvrez le fichier `.html` correspondant dans un navigateur web. Les fichiers sont nommés selon le format suivant :

- Pour une déneigeuse : `nom-de-ville-animation_{numero_du_scenario}.html`
- Pour le drone : `animation.html`

### Exemple

Ouvrez le fichier dans un navigateur web comme suit :

```bash
firefox nom_du_fichier.html
```
Ou encore drag and drop le fichier dans votre navigateur

Cliquez sur le bouton pour lancer l'animation et visualiser le déneigement ou le passage du drone dans la ville que vous avez choisie.

### Le site internet

Vous pouvez aussi utiliser le site internet react qui est dans le dossier ERO1.
Pour ce faire

Se rendre dans le dossier ERO1

```bash
cd ERO1/
```

Installer les dépendances

```bash
npm install
```

Lancer le server

```bash
npm run dev
```

Cliquer sur le lien qui s'affiche dans votre terminal. Le site affiche alors possibilité de selectionner les différents quartier avec les différents scénarios, et il permet aussi d'afficher uniquement le trajet du drone.

### Attention

La ville de Rivière-des-Prairies–Pointe-aux-Trembles est assez grande, et le traitement des données peut donc prendre un certain temps. Veuillez patienter pendant que les fichiers sont générés pour la visualisation.

# Structure du Projet DÉNEIGEMENT

Voici une description détaillée des répertoires et fichiers principaux du projet :

## Répertoires et Fichiers

### Dossiers de Quartiers
Chaque quartier de Montréal dispose de son propre dossier contenant les fichiers suivants :
- `animation.html` : Animation visualisant le déneigement ou le passage du drone.
- `graph.pkl` : Fichier de données sérialisées utilisé pour stocker les structures de données complexes.
- `map.html` : Carte interactive pour visualiser les résultats du déneigement.
- Fichiers HTML additionnels pour différentes animations spécifiques.

### `AUTHORS`
Contient des informations sur les créateurs et contributeurs du projet.

### `ERO1`
Dossier destiné aux développements web (Front-end du projet):
- Fichiers de configuration pour les frameworks (React, Vite, etc.)
- Dossiers pour les ressources publiques et les composants React.

### `src`
Contient le code source du projet :
- `drone.py` : Script pour les simulations de drone.
- `ero1.py` : Script principal pour lancer les simulations de déneigement.
- `SPRP.py` : Fonctions spécifiques au projet.

### `test`
Dossier pour les tests unitaires et d'intégration :
- `test_drone_min_cost.py` : Teste les algorithmes de coût minimal des drones.
- `test_drone.py` : Teste les fonctionnalités de simulation de drone.

### `utils`
Utilitaires pour la gestion des données et des graphiques :
- `create_graph.py` : Script pour créer et dessiner des graphes très utiles pour les tests.

## Fichiers Racine
- **README.md** : Instructions détaillées sur l'installation et l'utilisation du projet.
- **requirements.txt** : Liste toutes les bibliothèques Python nécessaires pour exécuter les scripts.