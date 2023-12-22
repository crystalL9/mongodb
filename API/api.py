from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient

app = FastAPI()

# CORS middleware for allowing requests from all origins
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# MongoDB configurations
MONGO_DB_NAME = 'OSINT_db'
MONGO_DB_ADDRESS = 'mongodb://192.168.143.92:27017/'

# Function to insert or update link in the specified table
async def insert_or_update_link(table_name: str, object_id: str, new_link: str):
    client = AsyncIOMotorClient(MONGO_DB_ADDRESS)
    db = client[MONGO_DB_NAME]
    col = db[table_name]

    existing_document = await col.find_one({"object": object_id})

    if existing_document:
        await col.update_one(
            {"object": object_id},
            {"$addToSet": {"link": new_link}}
        )
        return {
            "status_code": 200,
            "object_id": object_id,
            "message": f"Link added to existing document in {MONGO_DB_NAME}.{table_name} successfully"
        }
    else:
        new_document = {
            "object": object_id,
            "link": [new_link]
        }
        await col.insert_one(new_document)
        return {
            "status_code": 201,  # Created
            "object_id": object_id,
            "message": f"New document created in {MONGO_DB_NAME}.{table_name} successfully"
        }
# Function to drop a table
async def drop_table(table_name: str):
    client = AsyncIOMotorClient(MONGO_DB_ADDRESS)
    db = client[MONGO_DB_NAME]

    try:
        await db.drop_collection(table_name)
        return {"status_code": 200, "message": f"Table {table_name} in {MONGO_DB_NAME} dropped successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
# Function to delete an object_id from a table
async def delete_object_id(table_name: str, object_id: str):
    client = AsyncIOMotorClient(MONGO_DB_ADDRESS)
    db = client[MONGO_DB_NAME]

    try:
        col = db[table_name]
        result = await col.delete_one({"object": object_id})
        if result.deleted_count > 0:
            return {"status_code": 200, "message": f"Object with id {object_id} deleted from {table_name} successfully"}
        else:
            return {"status_code": 404, "message": f"No object found with id {object_id} in {table_name}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

# async def get_links(table_name: str, object_id: str):
#     client = AsyncIOMotorClient(MONGO_DB_ADDRESS)
#     db = client[MONGO_DB_NAME]

#     try:
#         col = db[table_name]
#         cursor = col.find_one({"object": object_id}, {"link": 1, "_id": 0})

#         if cursor:
#             links = cursor.get("link", [])
#             result = {"status_code": 200, "object_id": object_id, "link_count": len(links), "links": links}
#         else:
#             result = {"status_code": 404, "message": f"No object found with id {object_id} in {table_name}"}
        
#         return result
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

# Function to get links from a table and object_id
async def get_links(table_name: str, object_id: str):
    client = AsyncIOMotorClient(MONGO_DB_ADDRESS)
    db = client[MONGO_DB_NAME]

    try:
        col = db[table_name]
        cursor = await col.find_one({"object": object_id}, {"link": 1, "_id": 0})

        if cursor and "link" in cursor:
            links = cursor["link"]
            result = {"status_code": 200, "object_id": object_id, "link_count": len(links), "links": links}
        else:
            result = {"status_code": 404, "message": f"No object found with id {object_id} in {table_name}"}
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

# API endpoint to get links from a table and object_id
@app.get("/get-links/{table_name}/{object_id}")
async def get_links_endpoint(table_name: str, object_id: str):
    try:
        result = await get_links(table_name, object_id)
        return result
    except HTTPException as e:
        return {"status_code": e.status_code, "message": str(e.detail)}

# API endpoint to delete an object_id from a table
@app.delete("/delete-object/{table_name}/{object_id}")
async def delete_object_id_endpoint(table_name: str, object_id: str):
    try:
        result = await delete_object_id(table_name, object_id)
        return result
    except HTTPException as e:
        return {"status_code": e.status_code, "message": str(e.detail)}
# Function to get object_ids from a table
async def get_object_ids(table_name: str):
    client = AsyncIOMotorClient(MONGO_DB_ADDRESS)
    db = client[MONGO_DB_NAME]

    try:
        col = db[table_name]
        cursor = col.find({}, {"object": 1, "_id": 0})
        object_ids = [doc["object"] for doc in await cursor.to_list(None)]
        return {"status_code": 200, "count": len(object_ids),"object_ids": object_ids}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

# API endpoint to get object_ids from a table
@app.get("/get-object-ids/{table_name}")
async def get_object_ids_endpoint(table_name: str):
    try:
        result = await get_object_ids(table_name)
        return result
    except HTTPException as e:
        return {"status_code": e.status_code, "message": str(e.detail)}
# API endpoint to drop a table
@app.delete("/drop-table/{table_name}")
async def drop_table_endpoint(table_name: str):
    try:
        result = await drop_table(table_name)
        return result
    except HTTPException as e:
        return {"status_code": e.status_code, "message": str(e.detail)}

# API endpoint to get links
@app.post("/insert/{table_name}/{object_id}")
async def insert_update_link(table_name: str, object_id: str, new_links: str):
    links = new_links.split(',')
    list_link = [link for link in links]
    for link_ in list_link:
        try:
            result = await insert_or_update_link(table_name, object_id, link_)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
    return result

# Run the FastAPI app with Uvicorn
# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)
