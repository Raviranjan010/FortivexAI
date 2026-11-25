from sqlalchemy.schema import CreateTable

from .models import Appointment


def initialize_appointment_schema(engine):
    if engine.dialect.name != "sqlite":
        return
    table = Appointment.__table__
    with engine.begin() as connection:
        connection.exec_driver_sql("BEGIN IMMEDIATE")
        ddl = connection.exec_driver_sql(
            "SELECT sql FROM sqlite_master WHERE type='table' AND name='appointments'"
        ).scalar_one()
        if "uq_appointment_start" in ddl.lower():
            replacement = str(CreateTable(table).compile(dialect=engine.dialect))
            connection.exec_driver_sql(replacement.replace("CREATE TABLE appointments", "CREATE TABLE appointments_migration", 1))
            columns = ", ".join(table.columns.keys())
            connection.exec_driver_sql(f"INSERT INTO appointments_migration ({columns}) SELECT {columns} FROM appointments")
            connection.exec_driver_sql("DROP TABLE appointments")
            connection.exec_driver_sql("ALTER TABLE appointments_migration RENAME TO appointments")
            for index in table.indexes:
                index.create(connection)
        for operation in ("INSERT", "UPDATE"):
            connection.exec_driver_sql(f"""
                CREATE TRIGGER IF NOT EXISTS prevent_appointment_overlap_{operation.lower()}
                BEFORE {operation} ON appointments
                WHEN NEW.status = 'confirmed' AND EXISTS (
                    SELECT 1 FROM appointments
                    WHERE status = 'confirmed' AND id <> NEW.id
                    AND starts_at < NEW.ends_at AND ends_at > NEW.starts_at
                )
                BEGIN SELECT RAISE(ABORT, 'Appointment overlaps a confirmed booking'); END
            """)
