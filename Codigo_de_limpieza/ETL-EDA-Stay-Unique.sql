-- Databricks notebook source
--1: Crear un schema(base de datos)
--show databases
create database dbstayunique


-- COMMAND ----------

--seleccionar la base de datos creada
use dbstayunique

-- COMMAND ----------

-- MAGIC %md
-- MAGIC Realizando ETL

-- COMMAND ----------

--2: Crear un vista temporal desde CSV Booking
CREATE OR REPLACE TEMPORARY VIEW vistaBooking
USING csv
OPTIONS (
  path '/FileStore/tables/Bookings.csv',
  header = "true",
  inferSchema = "true",
  delimiter  = ','
);


-- COMMAND ----------

--3: Crear una tabla persistente limpia, apartir de la vista temporal Booking
CREATE OR REPLACE TABLE tablaBooking
AS
Select PropertyId,Property_BookingId,BookingCreatedDate,ArrivalDate,DepartureDate,COALESCE(Adults,0) Adults,COALESCE(Children,0) Children,COALESCE(Infants,0) Infants,	
Persons,	NumNights,	Channel,	COALESCE(RoomRate,0) RoomRate,	COALESCE(CleaningFee,0) CleaningFee,	COALESCE(Revenue,0) Revenue,	COALESCE(ADR,0) ADR,	
COALESCE(TouristTax,0) TouristTax,	TotalPaid
from vistaBooking
where ArrivalDate is not null and DepartureDate is not null
    and Persons > 0 and NumNights >0 and Channel is not null and TotalPaid > 0

-- COMMAND ----------

Select count(1) from tablaBooking

-- COMMAND ----------

--4: Crear un vista temporal desde CSV Properties
CREATE OR REPLACE TEMPORARY VIEW vistaPropertie
USING csv
OPTIONS (
  path '/FileStore/tables/Properties.csv',
  header = "true",
  inferSchema = "true",
  delimiter  = ','
);


-- COMMAND ----------

--5: Crear una tabla persistente limpia, apartir de la vista temporal Properties
CREATE OR REPLACE TABLE tablaPropertie
AS
Select * from vistaPropertie 
where RealProperty is not null and Capacity > 0 
and Square > 0 and PropertyType is not null
and NumBedrooms > 0


-- COMMAND ----------

Select count(1) from tablaPropertie

-- COMMAND ----------

--6: Crear una tabla resultado persistente limpia, apartir de las dos tablas tablaBooking y tablaPropertie
CREATE OR REPLACE TABLE tablaBookingCharacteristic
AS
Select p.PropertyId,b.ArrivalDate, b.DepartureDate, p.Capacity, p.PropertyType,p.NumBedrooms,  b.Persons, b.NumNights,b.Channel,b.TotalPaid
from tablaBooking b inner join tablaPropertie p on (b.PropertyId = p.PropertyId) 




-- COMMAND ----------

-- MAGIC %md
-- MAGIC Realizando exploración de datos

-- COMMAND ----------

select * from tablaBookingCharacteristic

-- COMMAND ----------

-- MAGIC %python
-- MAGIC #7: Grabar la tabla resultado como csv
-- MAGIC from pyspark.sql import SparkSession
-- MAGIC # Crear una sesión de Spark
-- MAGIC spark = SparkSession.builder \
-- MAGIC     .appName("My Spark Application") \
-- MAGIC     .getOrCreate()
-- MAGIC
-- MAGIC # Asignar al dataframe la tabla tablaBookingCharacteristic
-- MAGIC dfBookingCharacteristic = spark.sql("""
-- MAGIC SELECT *
-- MAGIC FROM tablaBookingCharacteristic
-- MAGIC """)
-- MAGIC # Grabar el dataframe como un archivo csv en una ruta 
-- MAGIC dfBookingCharacteristic.write.csv("dbfs:/FileStore/tables/tablaBookingCharacteristic", header=True)
-- MAGIC

-- COMMAND ----------


