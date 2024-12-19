from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "package" (
    "packageId" UUID NOT NULL  PRIMARY KEY,
    "packageName" VARCHAR(40) NOT NULL UNIQUE,
    "price" DOUBLE PRECISION NOT NULL,
    "sumNum" SMALLINT NOT NULL
);
CREATE TABLE IF NOT EXISTS "user" (
    "userId" UUID NOT NULL  PRIMARY KEY,
    "userName" VARCHAR(40) NOT NULL UNIQUE,
    "password" VARCHAR(40) NOT NULL,
    "location" VARCHAR(40) NOT NULL,
    "sumCount" SMALLINT NOT NULL
);
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSONB NOT NULL
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """
