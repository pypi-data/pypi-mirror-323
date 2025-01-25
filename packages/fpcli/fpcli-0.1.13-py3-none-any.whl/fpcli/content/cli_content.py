def get_controller_content(name: str):
    class_name = f"{name.capitalize()}Controller"
    return f'''
from fastapi import Request

class {class_name}:

    async def index(self):
        """
        Get all the data.

        Returns:
            str: A message indicating that all data is being fetched.
        """
        return "getting all data"

    async def edit(self, uuid: str):
        """
        Read or edit the data based on the given UUID.

        Args:
            uuid (str): The unique identifier for the data to be read or edited.

        Returns:
            str: A message indicating the action for read or edit.
        """
        return "for read or edit the data "

    async def create(self, request: Request):
        """
        Create new data based on the request.

        Args:
            request (Request): The request object containing the data to be created.

        Returns:
            str: A message indicating the creation of new data.
        """
        return f"for post request : creating the data"

    async def update(self, request: Request, uuid: str):
        """
        Update the data based on the given UUID.

        Args:
            request (Request): The request object containing the updated data.
            uuid (str): The unique identifier for the data to be updated.

        Returns:
            str: A message indicating that the data is being updated.
        """
        return f"for update the data on the respect of the uuid"

    async def destroy(self, uuid: str):
        """
        Delete the data based on the given UUID.

        Args:
            uuid (str): The unique identifier for the data to be deleted.

        Returns:
            str: A message indicating the deletion of the data.
        """
        return "for delete the data"
        '''


def get_model_contant(name: str):
    class_name = f"{name.capitalize()}Model"
    return f'''
from typing import Optional
from pydantic import BaseModel, Field
from beanie import Document

class {class_name}(Document):
    """
    {class_name} represents the schema for {name}.
    """
    uuid: str = Field(..., description="Unique identifier for the document")

    status: Optional[bool] = Field(True, description="Last update timestamp")
    created_at: Optional[str] = Field(None, description="Creation timestamp")
    updated_at: Optional[str] = Field(None, description="Last update timestamp")
    deleted_at: Optional[str] = Field(None, description="Last update timestamp")

    class Settings:
        name = "{name.lower()}_collection"
    '''


def get_validator_content(name: str):
    class_name = f"{name.capitalize()}Validator"
    return f'''
from pydantic import BaseModel, Field
from typing import Optional

class {class_name}(BaseModel):
    """
    {class_name} is used to validate {name} data.
    """
    uuid: Optional[str] = Field(None, description="Unique identifier for the data")
    name: str = Field(..., description="Name field")
    description: Optional[str] = Field(None, description="Description of the entity")
    created_at: Optional[str] = Field(None, description="Creation timestamp")
    updated_at: Optional[str] = Field(None, description="Last update timestamp")
    '''


def get_servie_content(name: str):
    class_name = f"{name.capitalize()}Service"

    return f'''
from typing import List, Optional
from beanie import PydanticObjectId
from app.models.{name.lower()}_model import {name.capitalize()}Model

class {class_name}:
    """
    {class_name} handles the business logic and database operations for {name}.
    """

    @staticmethod
    async def create(data: dict) -> {name.capitalize()}Model:
        """
        Create a new {name}.
        
        Args:
            data (dict): The data to create the {name}.
        
        Returns:
            {name.capitalize()}Model: The created {name}.
        """
        instance = {name.capitalize()}Model(**data)
        await instance.insert()
        return instance

    @staticmethod
    async def get_all() -> List[{name.capitalize()}Model]:
        """
        Fetch all {name}s.
        
        Returns:
            List[{name.capitalize()}Model]: List of all {name}s.
        """
        return await {name.capitalize()}Model.find_all().to_list()

    @staticmethod
    async def get_by_id(id: PydanticObjectId) -> Optional[{name.capitalize()}Model]:
        """
        Fetch a {name} by its ID.
        
        Args:
            id (PydanticObjectId): The unique identifier of the {name}.
        
        Returns:
            Optional[{name.capitalize()}Model]: The {name} if found, else None.
        """
        return await {name.capitalize()}Model.get(id)

    @staticmethod
    async def update(id: PydanticObjectId, data: dict) -> Optional[{name.capitalize()}Model]:
        """
        Update an existing {name}.
        
        Args:
            id (PydanticObjectId): The unique identifier of the {name}.
            data (dict): The updated data.
        
        Returns:
            Optional[{name.capitalize()}Model]: The updated {name} if successful, else None.
        """
        instance = await {name.capitalize()}Model.get(id)
        if instance:
            for key, value in data.items():
                setattr(instance, key, value)
            await instance.save()
        return instance

    @staticmethod
    async def delete(id: PydanticObjectId) -> bool:
        """
        Delete a {name} by its ID.
        
        Args:
            id (PydanticObjectId): The unique identifier of the {name}.
        
        Returns:
            bool: True if deletion was successful, False otherwise.
        """
        instance = await {name.capitalize()}Model.get(id)
        if instance:
            await instance.delete()
            return True
        return False
    '''


def get_middleware_content(name: str):
    class_name = f"{name.capitalize()}Middleware"

    return f'''
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
import logging

class {class_name}(BaseHTTPMiddleware):
    """
    {class_name} is a custom middleware for processing requests and responses.
    """
    async def dispatch(self, request: Request, call_next):
        """
        Intercept the incoming request, process it, then call the next handler.
        
        Args:
            request (Request): The incoming request.
            call_next (Callable): The function to call the next middleware or route handler.
        
        Returns:
            Response: The final response to be returned.
        """


        # Call the next middleware or route handler
        response = await call_next(request)


        return response
    '''


def get_seeder_content(name: str, app_name: str):
    class_name = f"{name.capitalize()}Seeder"
    service_name = f"{name.capitalize()}Service"
    return f'''
import asyncio
from {app_name.lower()}.services.{name.lower()}_service import {service_name}

class {class_name}:
    """
    Seeder for {name.capitalize()}Model to populate initial data.
    """

    @staticmethod
    async def run():
        """
        Run the seeder to insert sample data into the database.
        """
        data = [
            {{
                "status": True,
                "created_at": "2025-01-01T00:00:00Z",
                "updated_at": "2025-01-01T00:00:00Z"
            }},
            {{
                "status": False,
                "created_at": "2025-01-02T00:00:00Z",
                "updated_at": "2025-01-02T00:00:00Z"
            }}
        ]

        # Insert the data into the database using a loop
        for record in data:
            await {service_name}.create(record)

        print(f"{class_name} seed successfully!")
    '''




def get_route_content(controller_name: str, method: str, route_name: str):
    """
    Generate FastAPI route snippet in the format of app_router.add_api_route.
    
    Args:
        controller_name (str): The name of the controller (e.g., UserController).
        method (str): HTTP method (GET, POST, PUT, DELETE, etc.).
        route_name (str): The route name (e.g., '/user/', '/user/create').
    
    Returns:
        str: The generated route snippet in the desired format.
    """
    # Extract the controller method name dynamically
    controller_method = route_name.strip('/').replace('/', '_')

    # Generate the route content in app_router.add_api_route format
    return f'app_router.add_api_route("{route_name}", {controller_name}().{controller_method}, methods={["{method}"]})'

