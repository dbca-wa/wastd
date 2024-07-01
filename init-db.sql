-- Connect as the superuser
\c postgres

-- Create the test_user if it does not exist
DO
$$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'test_user') THEN
        CREATE USER test_user WITH PASSWORD 'test_password';
    END IF;
END
$$;

-- Create the test_db database if it does not exist
DO
$$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_database WHERE datname = 'test_db') THEN
        CREATE DATABASE test_db OWNER test_user;
    END IF;
END
$$;

-- Connect to test_db as the superuser
\c test_db

-- -- Ensure PostGIS extension is installed
-- DO
-- $$
-- BEGIN
--     IF NOT EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'postgis') THEN
--         CREATE EXTENSION postgis;
--     END IF;
-- END
-- $$;

-- Grant all privileges on test_db to test_user
GRANT ALL PRIVILEGES ON DATABASE test_db TO test_user;

-- Grant necessary privileges on the public schema to test_user
GRANT ALL PRIVILEGES ON SCHEMA public TO test_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO test_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO test_user;
GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public TO test_user;
