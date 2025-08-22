# Utiliser une image Node.js pour l'environnement de développement
FROM node:16-alpine

# Définir le répertoire de travail
WORKDIR /app

# Copier package.json et installer les dépendances
# Cela permet de mettre en cache les dépendances et d'accélérer les builds suivants
COPY package*.json ./
RUN npm install

# Copier le reste du code de l'application
COPY . .

# Le serveur sera démarré par la commande dans docker-compose.yml
CMD ["npm", "start"]
