import uuid
from typing import Generic, Optional, Type, TypeVar, Union

from sqlmodel import Session, SQLModel, select

from database_utils.core.database_connection import get_engine

ModelType = TypeVar("ModelType", bound=SQLModel)
CreateType = TypeVar("CreateType", bound=SQLModel)
UpdateType = TypeVar("UpdateType", bound=SQLModel)


class ModelRepository(Generic[ModelType, CreateType, UpdateType]):
    """
    A generic repository class for performing CRUD operations on a SQLModel.
    This repository is designed to work seamlessly with SQLModel and FastAPI, providing a solid foundation for building APIs and database interactions.

    This implementation utilizes the models and concepts outlined in the SQLModel documentation, in conjunction with FastAPI for building high-performance asynchronous APIs.

    https://sqlmodel.tiangolo.com/tutorial/fastapi/multiple-models/#avoid-duplication-keep-it-simple

    Attributes:
        model (Type[ModelType]): The SQLModel class to perform operations on.

    Methods:
        get_all() -> List[ModelType]:
            Asynchronously retrieves all records of the model from the database.

        get_by_id(obj_id: uuid.UUID) -> Optional[ModelType]:
            Asynchronously retrieves a single record by its UUID from the database.

        create(obj_create: CreateType) -> ModelType:
            Asynchronously creates a new record in the database.

        update(obj_id: uuid.UUID, obj_update: UpdateType) -> Optional[ModelType]:
            Asynchronously updates an existing record in the database.

        delete(obj_id: uuid.UUID) -> Optional[ModelType]:
            Asynchronously deletes a record from the database.

    # Example of instantiating the ModelRepository with the User model from a UserManager or UserService class
    class UserManager:
        def __init__(self) -> None:
            self._user_repository = ModelRepository[User, UserCreate, UserUpdate](User)

    # Example of instantiating the ModelRepository from a UserRepository file inheriting from ModelRepository
    # This allows you to add custom functions for more elaborate queries using SQLModel.
    class UserRepository(ModelRepository[User, UserCreate, UserUpdate]):

        # Example of a custom query
        async def get_users_by_role(self, role: RoleUser):
            statement = select(User).where(User.role == role)
            result = await self.session.execute(statement)
            return result.scalars().all()

    class UserManager:
        def __init__(self) -> None:
            self._user_repo = UserRepository(User)

    # SQLModel and FastAPI
    # This repository pattern aligns well with FastAPI's dependency injection system,
    # making it easy to integrate with endpoints. Here’s an example of a FastAPI route using this repository:

    from fastapi import APIRouter

    router = APIRouter()

    @router.get("/users/", response_model=List[UserRead])
    async def get_all_users():
        return await user_manager.get_all_users()

    @router.post("/users/", response_model=UserRead)
    async def create_user(user_create: UserCreate = Body(...)):
        return await user_manager.create_user(user_create)

    """

    def __init__(self, model: Type[ModelType]):
        """
        Initialize the ModelRepository with the given model type.

        Args:
            model (Type[ModelType]): The model class to be used by the repository.
        """

        self.model = model

    async def get_all(self):
        """
        Retrieve all records of the model from the database.

        This asynchronous method opens a new session with the database engine,
        executes a SELECT statement to fetch all records of the specified model,
        and returns the result as a list.

        Returns:
            List[Model]: A list of all records of the model from the database.
        """

        with Session(get_engine()) as session:
            result = session.exec(select(self.model)).all()
            return result

    async def get_by_id(self, obj_id: Optional[Union[int, uuid.UUID]]):
        """
        Retrieve an object by its ID.

        Args:
            obj_id (Optional[Union[int, uuid.UUID]]): The ID of the object to retrieve.
                It can be an integer or a UUID.

        Returns:
            The object with the specified ID, or None if no such object exists.
        """

        with Session(get_engine()) as session:
            obj = session.get(self.model, obj_id)
            return obj

    async def create(self, obj_create: CreateType):
        """
        Create a new record in the database.

        Args:
            obj_create (CreateType): The data required to create a new record.

        Returns:
            The newly created database object.
        """

        with Session(get_engine()) as session:
            db_obj = self.model.model_validate(obj_create)
            session.add(db_obj)
            session.commit()
            session.refresh(db_obj)
            return db_obj

    async def update(
        self, obj_id: Optional[Union[int, uuid.UUID]], obj_update: UpdateType
    ):
        """
        Update an existing object in the database.
        Args:
            obj_id (Optional[Union[int, uuid.UUID]]): The ID of the object to update. Can be an integer or a UUID.
            obj_update (UpdateType): An object containing the updated data.
        Returns:
            The updated object if found and updated, otherwise None.
        """

        with Session(get_engine()) as session:
            db_obj = session.get(self.model, obj_id)
            if not db_obj:
                return None

            update_data = obj_update.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(db_obj, key, value)

            session.add(db_obj)
            session.commit()
            session.refresh(db_obj)
            return db_obj

    async def delete(self, obj_id: Optional[Union[int, uuid.UUID]]):
        """
        Deletes an object from the database by its ID.
        Args:
            obj_id (Optional[Union[int, uuid.UUID]]): The ID of the object to delete. Can be an integer or a UUID.
        Returns:
            The deleted object if it was found and deleted, otherwise None.
        """

        with Session(get_engine()) as session:
            db_obj = session.get(self.model, obj_id)
            if not db_obj:
                return None

            session.delete(db_obj)
            session.commit()
            return db_obj
