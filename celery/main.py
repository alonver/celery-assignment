import logging
import os
import shutil
import time
from typing import List

import pandas as pd
from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from sqlalchemy import distinct
from sqlalchemy.orm import Session

from celery.db import create_db, Category, ExcelFile, get_db
from celery.models import CategoryCreate

# Creating the DB - In a production system, we'll use a smarter migration tool.
create_db()

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
logging.getLogger("uvicorn.error").setLevel(logging.WARNING)

app = FastAPI()


@app.post("/create_category")
def create_category(category: CategoryCreate, db: Session = Depends(get_db)):
    logger.info(f"Creating category: {category.category_name}")
    if db.query(Category).filter_by(name=category.category_name).first():
        logger.warning(f"Category '{category.category_name}' already exists")
        raise HTTPException(status_code=400, detail="Category already exists")
    new_category = Category(name=category.category_name, region=category.region, type=category.type)
    db.add(new_category)
    logger.info(f"Category '{category.category_name}' created successfully")
    return {"message": "Category created"}


@app.post("/upload_file/{category_name}")
def upload_file(category_name: str, file: UploadFile = File(...), db: Session = Depends(get_db)):
    logger.info(f"Uploading file {file.filename} to category {category_name}")
    category = db.query(Category).filter_by(name=category_name).first()
    if not category:
        logger.error(f"Category '{category_name}' not found")
        raise HTTPException(status_code=404, detail="Category not found")
    filepath = save_file(category_name, file)
    logger.info(f"Finished saving file {file.filename}")
    # If I had more time, I would've added a queue, and enqueue a task to parse the file offline,
    # to avoid blocking the operation if the parsing is heavy
    (num_sum, text) = parse_file(file)
    logger.info(f"Finished parsing file {file.filename}")
    new_file = ExcelFile(filename=file.filename, category_id=category.id, filepath=filepath, num_sum=num_sum, text=text)
    db.add(new_file)
    logger.info(f"Finished uploading file {file.filename} to category {category_name}")
    return {"message": "File uploaded"}


@app.get("/sum_type/{type}")
def sum_type(type: str, db: Session = Depends(get_db)):
    logger.info(f"Getting sum for type {type}")
    files = db.query(ExcelFile).join(Category).filter(Category.type == type).all()
    total = 0.0
    for excel_file in files:
        sum = excel_file.num_sum
        logger.debug(f"Got sum {sum} for file {excel_file.filename}")
        total += sum

    logger.info(f"Got sum {total} for type {type}")
    return {"sum": total}


@app.get("/find_regions", response_model=List[str])
def find_regions(search_term: str, db: Session = Depends(get_db)):
    logger.info(f"Finding regions by search term {search_term}")
    # If I had more time, I would've saved the text to something that's more suitable
    # for text searches (like Elastic), and search the given term there
    regions = (db.query(distinct(Category.region)).join(ExcelFile).
               filter(ExcelFile.text.ilike(f"%{search_term}%")).all())
    result = [region[0] for region in regions]
    logger.info(f"Found regions {result} by search term {search_term}")
    return result


# In a real production system, we would an object store, like S3
def save_file(category_name: str, file: UploadFile) -> str:
    dir_name = f"uploads/{category_name}"
    os.makedirs(dir_name, exist_ok=True)
    timestamp = int(time.time())
    new_filename = f"{timestamp}_{file.filename}"
    filepath = f"{dir_name}/{new_filename}"
    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return filepath


def parse_file(file: UploadFile) -> (float, str):
    sum = 0.0
    all_texts = []
    xls = pd.ExcelFile(file.file)
    for sheet_name in xls.sheet_names:
        sheet = xls.parse(sheet_name, header=None)

        numeric_df = sheet.apply(pd.to_numeric, errors='coerce')
        sum += float(numeric_df.sum().sum())

        all_texts.extend(sheet.fillna('').astype(str).values.flatten())
    text = ' '.join(all_texts)
    return sum, text
