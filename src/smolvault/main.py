import json
import logging
import pathlib
import sys
import urllib.parse
from logging.handlers import RotatingFileHandler
from typing import Annotated

from fastapi import (
    BackgroundTasks,
    Depends,
    FastAPI,
    HTTPException,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import FileResponse, Response
from fastapi.security import OAuth2PasswordRequestForm

from smolvault.auth.decoder import (
    authenticate_user,
    create_access_token,
    get_current_user,
)
from smolvault.auth.models import Token, User
from smolvault.cache.cache_manager import CacheManager
from smolvault.clients.aws import S3Client
from smolvault.clients.database import DatabaseClient, FileMetadataRecord
from smolvault.config import Settings, get_settings
from smolvault.models import FileMetadata, FileTagsDTO

logging.basicConfig(
    handlers=[
        RotatingFileHandler("app.log", maxBytes=100_000, backupCount=10),
        logging.StreamHandler(sys.stdout),
    ],
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(title="smolvault")

app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


settings: Settings = get_settings()
s3_client = S3Client(bucket_name=settings.smolvault_bucket)
cache = CacheManager(cache_dir=settings.smolvault_cache)


@app.get("/")
async def read_root(current_user: Annotated[User, Depends(get_current_user)]) -> User:
    return current_user


# @app.post("/users/new")
# async def create_user(
#     user: NewUserDTO, db_client: Annotated[DatabaseClient, Depends(DatabaseClient)]
# ) -> dict[str, str]:
#     db_client.add_user(user)
#     return {"username": user.username}


@app.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db_client: Annotated[DatabaseClient, Depends(DatabaseClient)],
) -> Token:
    logger.info("Authenticating user %s", form_data.username)
    user = authenticate_user(db_client, form_data.username, form_data.password)
    if not user:
        logger.info("Incorrect username or password for %s", form_data.username)
        raise HTTPException(
            status_code=400,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.username})
    logger.info("User %s authenticated successfully", user.username)
    return access_token


# @app.post("/file/upload")
# async def upload_file(
#     current_user: Annotated[User, Depends(get_current_user)],
#     db_client: Annotated[DatabaseClient, Depends(DatabaseClient)],
#     file: Annotated[UploadFile, File()],
#     tags: str | None = Form(default=None),
# ) -> Response:
#     logger.info("Received file upload request from %s", current_user.username)
#     contents = await file.read()
#     if file.filename is None:
#         logger.error("Filename not received in request")
#         raise ValueError("Filename is required")
#     file_upload = FileUploadDTO(
#         name=file.filename,
#         size=len(contents),
#         content=contents,
#         tags=tags,
#         user_id=current_user.id,
#     )
#     logger.info(
#         "Uploading file to S3 with name %s uploaded by %s",
#         file_upload.name,
#         current_user.username,
#     )
#     object_key = s3_client.upload(data=file_upload)
#     db_client.add_metadata(file_upload, object_key)
#     logger.info("File %s uploaded successfully", file_upload.name)
#     return Response(
#         content=json.dumps(file_upload.model_dump(exclude={"content", "tags"})),
#         status_code=201,
#         media_type="application/json",
#     )


@app.get("/file/original")
async def get_file(
    current_user: Annotated[User, Depends(get_current_user)],
    db_client: Annotated[DatabaseClient, Depends(DatabaseClient)],
    filename: str,
    background_tasks: BackgroundTasks,
) -> Response:
    logger.info("Received file download request for %s from %s", filename, current_user.username)
    record = db_client.get_metadata(filename, current_user.id)
    if record is None:
        logger.info("File not found: %s", filename)
        return Response(
            content=json.dumps({"error": "File not found"}),
            status_code=404,
            media_type="application/json",
        )
    if record.local_path is None or cache.file_exists(record.file_name) is False:
        logger.info("File %s not found in cache, downloading from S3", filename)
        content = s3_client.download(record.object_key)
        record.local_path = cache.save_file(record.file_name, content)
        record.cache_timestamp = int(pathlib.Path(record.local_path).stat().st_mtime)
        logger.info("Saved file %s at time %d", record.local_path, record.cache_timestamp)
        background_tasks.add_task(db_client.update_metadata, record)
    logger.info("Serving file %s from cache", record.file_name)
    return FileResponse(path=record.local_path, filename=record.file_name)


@app.get("/file/{name}/metadata")
async def get_file_metadata(
    current_user: Annotated[User, Depends(get_current_user)],
    db_client: Annotated[DatabaseClient, Depends(DatabaseClient)],
    name: str,
) -> FileMetadata | None:
    logger.info("Retrieving metadata for file %s requested by %s", name, current_user.username)
    record: FileMetadataRecord | None = db_client.get_metadata(urllib.parse.unquote(name), current_user.id)
    if record:
        logger.info("Retrieved metadata for file %s", name)
        return FileMetadata.model_validate(record.model_dump())
    logger.info("File metadata for %s not found", name)
    return None


@app.get("/files")
async def get_files(
    current_user: Annotated[User, Depends(get_current_user)],
    db_client: Annotated[DatabaseClient, Depends(DatabaseClient)],
) -> list[FileMetadata]:
    logger.info("Retrieving all files for user %s", current_user.username)
    raw_metadata = db_client.get_all_metadata(current_user.id)
    logger.info("Retrieved %d records from database", len(raw_metadata))
    results = [FileMetadata.model_validate(metadata.model_dump()) for metadata in raw_metadata]
    return results


@app.get("/files/search")
async def search_files(
    current_user: Annotated[User, Depends(get_current_user)],
    db_client: Annotated[DatabaseClient, Depends(DatabaseClient)],
    tag: str,
) -> list[FileMetadata]:
    logger.info("Retrieving files with tag %s for user %s", tag, current_user.username)
    raw_metadata = db_client.select_metadata_by_tag(tag, current_user.id)
    logger.info("Retrieved %d records from database with tag %s", len(raw_metadata), tag)
    results = [FileMetadata.model_validate(metadata.model_dump()) for metadata in raw_metadata]
    return results


@app.patch("/file/{name}/tags")
async def update_file_tags(
    current_user: Annotated[User, Depends(get_current_user)],
    db_client: Annotated[DatabaseClient, Depends(DatabaseClient)],
    name: str,
    tags: FileTagsDTO,
) -> Response:
    logger.info("Updating tags for file %s requested by %s", name, current_user.username)
    record: FileMetadataRecord | None = db_client.get_metadata(name, current_user.id)
    if record is None:
        logger.info("Tag update failed. File %s not found", name)
        return Response(
            content=json.dumps({"error": "File not found"}),
            status_code=404,
            media_type="application/json",
        )

    record.tags = tags.tags_str
    db_client.update_metadata(record)
    file_metadata = FileMetadata.model_validate(record.model_dump())
    logger.info("Tags updated for file %s", name)
    return Response(
        content=json.dumps(
            {
                "message": "Tags updated successfully",
                "record": file_metadata.model_dump(),
            }
        ),
        status_code=200,
        media_type="application/json",
    )


@app.delete("/file/{name}")
async def delete_file(
    current_user: Annotated[User, Depends(get_current_user)],
    db_client: Annotated[DatabaseClient, Depends(DatabaseClient)],
    name: str,
    background_tasks: BackgroundTasks,
) -> Response:
    logger.info("Recieved delete request for file %s from %s", name, current_user.username)
    record: FileMetadataRecord | None = db_client.get_metadata(name, current_user.id)
    if record is None:
        logger.info("File %s not found", name)
        return Response(
            content=json.dumps({"error": "File not found"}),
            status_code=404,
            media_type="application/json",
        )
    s3_client.delete(record.object_key)
    db_client.delete_metadata(record, current_user.id)
    if record.local_path:
        background_tasks.add_task(cache.delete_file, record.local_path)
    logger.info("File %s deleted successfully", name)
    return Response(
        content=json.dumps({"message": "File deleted successfully", "record": record.model_dump()}),
        status_code=200,
        media_type="application/json",
    )
