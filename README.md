
# Celery Assignment  
  
A FastAPI-based web service that allows users to process Excel files.
  
## Features  
  
- Create new categories of Excel files.
- Upload Excel files and associate them with a named category.
- Query for the total sum of numbers for all files in a given category type  
- Query for category regions that have uploaded files matching a search term  
  
## Installation  
  
### 1. Clone the repository  
  
```bash  
git clone https://github.com/alonver/celery-assignment.git
cd celery-assignment
```  
  
### 2. Create a virtual environment  

```bash    
python -m venv venv  
source venv/bin/activate   # On Windows: venv\Scripts\activate
```

  
### 3. Install dependencies  
```bash  
pip install -r requirements.txt  
```
  
### 4. Run the database  

```bash    
docker compose up
```
  
### 5. Run the server in dev mode
```bash  
fastapi dev celery/main.py
```

## Example API Usage  

### 1. Create a category  
```bash  
curl -X POST http://localhost:8000/create_category \  
  -H "Content-Type: application/json" \  
  -d '{"category_name": "superheroes", "region": "new-york", "type": "marvel"}'  
```
  
### 2. Upload an Excel file  
```bash  
curl -X POST http://localhost:8000/upload_file/superheroes \  
  -F "file=@spider-man.xlsx"  
```
  
### 3. Get sum of all Excel values by category type  
```bash
curl http://localhost:8000/sum_type/marvel
```

### 4. Find category regions that match a search term  
```bash
curl http://localhost:8000/find_regions?search_term=spider
```
## What I would improve

Given more time or a real production system, i would've made the following changes:
1. Save the DB login details in a secret manager/vault and not hardcoded in the code.
2. Use a better, more complex migration tool than sqlalchemy's `Base.metadata.create_all`.
3. I would've saved the files texts in a datastore more suitable for searching large amounts of texts (like Elastic) and not in the Postgres DB.
4. Add a queue for processing the uploaded Excel files, so that all the file's parsing will be done offline and not block the user's call.
5. Save the uploaded Excel files to an Object Store (Like S3)


