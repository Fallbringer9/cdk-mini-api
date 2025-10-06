#  Mini API Serverless – AWS CDK, Lambda, API Gateway, S3

Ce projet présente une architecture serverless déployée avec **AWS CDK** en Python.  
Il a pour objectif de démontrer la mise en place d’une API REST simple, sécurisée et conforme au free tier AWS.

## Objectif

Construire une API minimale permettant :
- de vérifier l’état du service via `GET /health`
- d’envoyer un contenu texte vers un bucket S3 via `POST /upload`

## Architecture

**Services utilisés :**
- **AWS Lambda** : exécution du code Python sans serveur  
- **API Gateway** : exposition des endpoints HTTP  
- **S3** : stockage des fichiers envoyés  
- **IAM** : gestion des droits d’accès (principe du “least privilege”)  
- **CloudWatch** : logs et suivi des métriques

**Flux principal :**

### Endpoints
| Méthode | Route | Description |
|----------|--------|-------------|
| GET | `/health` | Vérifie le statut de l’API |
| POST | `/upload` | Reçoit un JSON avec un nom de fichier et un contenu, puis enregistre le fichier sur S3 |

**Exemple d’appel :**
```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"filename":"note.txt","content":"hello from lambda"}' \
  https://<api-id>.execute-api.eu-west-3.amazonaws.com/prod/upload

{
  "message": "uploaded",
  "key": "uploads/note.txt",
  "bucket": "<bucket-name>",
  "time": "2025-10-06T22:08:12.372977+00:00"
}