PRAGMA user_version=1;

CREATE TABLE IF NOT EXISTS "runbooks" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT,
    "external_id"  NOT NULL,
    "name" TEXT NOT NULL,
    "file_path" TEXT NOT NULL,
    "created_at" TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

    UNIQUE("external_id")
    UNIQUE("name")
);
