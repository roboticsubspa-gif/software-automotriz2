-- Quitar solo las tablas del taller (orden por FK). Luego importa backup_supabase.sql con psql.
-- Ejecutar en Supabase → SQL Editor (una vez), o con: psql ... -f scripts/drop_app_tables.sql

DROP TABLE IF EXISTS public.repuesto_usado CASCADE;
DROP TABLE IF EXISTS public.ot CASCADE;
DROP TABLE IF EXISTS public.servicio CASCADE;
DROP TABLE IF EXISTS public.vehiculo CASCADE;
DROP TABLE IF EXISTS public.cliente CASCADE;
DROP TABLE IF EXISTS public.repuesto CASCADE;
DROP TABLE IF EXISTS public.cotizacion CASCADE;
DROP TABLE IF EXISTS public.gasto_st CASCADE;
DROP TABLE IF EXISTS public.tarea CASCADE;
DROP TABLE IF EXISTS public.toma_hora CASCADE;
DROP TABLE IF EXISTS public.usuario CASCADE;
