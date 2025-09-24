-- MySQL dump 10.13  Distrib 9.4.0, for macos15.4 (arm64)
--
-- Host: localhost    Database: sistema_inventario
-- ------------------------------------------------------
-- Server version	9.4.0

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Current Database: `sistema_inventario`
--

/*!40000 DROP DATABASE IF EXISTS `sistema_inventario`*/;

CREATE DATABASE /*!32312 IF NOT EXISTS*/ `sistema_inventario` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;

USE `sistema_inventario`;

--
-- Table structure for table `categorias`
--

DROP TABLE IF EXISTS `categorias`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `categorias` (
  `nombre` varchar(50) NOT NULL,
  PRIMARY KEY (`nombre`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `categorias`
--

LOCK TABLES `categorias` WRITE;
/*!40000 ALTER TABLE `categorias` DISABLE KEYS */;
INSERT INTO `categorias` VALUES ('General'),('Nueva'),('Otra');
/*!40000 ALTER TABLE `categorias` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `entradas`
--

DROP TABLE IF EXISTS `entradas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `entradas` (
  `id` int NOT NULL AUTO_INCREMENT,
  `inventario_id` int DEFAULT NULL,
  `nombre` varchar(50) DEFAULT NULL,
  `cantidad` int DEFAULT NULL,
  `costo` decimal(10,2) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `inventario_id` (`inventario_id`),
  CONSTRAINT `entradas_ibfk_1` FOREIGN KEY (`inventario_id`) REFERENCES `inventario` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `entradas`
--

LOCK TABLES `entradas` WRITE;
/*!40000 ALTER TABLE `entradas` DISABLE KEYS */;
INSERT INTO `entradas` VALUES (1,1,'Producto 1',3,4.00),(2,2,'Producto 2',NULL,NULL),(3,3,'Producto 3',NULL,NULL),(4,4,'Producto 4',NULL,NULL),(5,5,'Producto 5',NULL,NULL),(6,6,'Producto 6',NULL,NULL),(7,7,'Producto 7',NULL,NULL),(8,8,'Producto 8',NULL,NULL),(9,9,'Producto 9',NULL,NULL),(10,10,'Producto 10',NULL,NULL),(11,12,NULL,5,10.00);
/*!40000 ALTER TABLE `entradas` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `existencia_final`
--

DROP TABLE IF EXISTS `existencia_final`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `existencia_final` (
  `id` int NOT NULL AUTO_INCREMENT,
  `inventario_id` int DEFAULT NULL,
  `nombre` varchar(50) DEFAULT NULL,
  `cantidad` int DEFAULT NULL,
  `costo` decimal(10,2) DEFAULT NULL,
  `monto` decimal(10,2) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `inventario_id` (`inventario_id`),
  CONSTRAINT `existencia_final_ibfk_1` FOREIGN KEY (`inventario_id`) REFERENCES `inventario` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `existencia_final`
--

LOCK TABLES `existencia_final` WRITE;
/*!40000 ALTER TABLE `existencia_final` DISABLE KEYS */;
INSERT INTO `existencia_final` VALUES (1,1,'Producto 1',NULL,NULL,NULL),(2,2,'Producto 2',NULL,NULL,NULL),(3,3,'Producto 3',NULL,NULL,NULL),(4,4,'Producto 4',NULL,NULL,NULL),(5,5,'Producto 5',NULL,NULL,NULL),(6,6,'Producto 6',NULL,NULL,NULL),(7,7,'Producto 7',NULL,NULL,NULL),(8,8,'Producto 8',NULL,NULL,NULL),(9,9,'Producto 9',NULL,NULL,NULL),(10,10,'Producto 10',NULL,NULL,NULL);
/*!40000 ALTER TABLE `existencia_final` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `existencia_inicial`
--

DROP TABLE IF EXISTS `existencia_inicial`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `existencia_inicial` (
  `id` int NOT NULL AUTO_INCREMENT,
  `inventario_id` int DEFAULT NULL,
  `nombre` varchar(50) DEFAULT NULL,
  `cantidad` int DEFAULT NULL,
  `costo` decimal(10,2) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `inventario_id` (`inventario_id`),
  CONSTRAINT `existencia_inicial_ibfk_1` FOREIGN KEY (`inventario_id`) REFERENCES `inventario` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=19 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `existencia_inicial`
--

LOCK TABLES `existencia_inicial` WRITE;
/*!40000 ALTER TABLE `existencia_inicial` DISABLE KEYS */;
INSERT INTO `existencia_inicial` VALUES (1,1,'Producto 1',1,1.00),(2,2,'Producto 2',NULL,NULL),(3,3,'Producto 3',NULL,NULL),(4,4,'Producto 4',NULL,NULL),(5,5,'Producto 5',10,5.00),(6,6,'Producto 6',10,3.00),(7,7,'Producto 7',10,50.00),(8,8,'Producto 8',10,3.00),(9,9,'Producto 9',NULL,NULL),(10,10,'Producto 10',NULL,NULL),(11,11,NULL,25,25.00),(12,11,NULL,25,25.00),(13,11,NULL,25,25.00),(14,11,NULL,30,30.00),(15,12,NULL,2,10.00),(16,13,NULL,1,10.00),(17,35,NULL,1,5.00),(18,44,NULL,44,44.00);
/*!40000 ALTER TABLE `existencia_inicial` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Inventario`
--

DROP TABLE IF EXISTS `Inventario`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Inventario` (
  `id` int NOT NULL AUTO_INCREMENT,
  `descripcion_insumo` varchar(255) DEFAULT NULL,
  `tipo` varchar(25) DEFAULT NULL,
  `cantidad` int DEFAULT NULL,
  `costo_unitario` decimal(10,2) DEFAULT NULL,
  `monto_total` decimal(10,2) DEFAULT NULL,
  `categoria` varchar(50) NOT NULL DEFAULT 'General',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=45 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Inventario`
--

LOCK TABLES `Inventario` WRITE;
/*!40000 ALTER TABLE `Inventario` DISABLE KEYS */;
INSERT INTO `Inventario` VALUES (1,'LaFinal',NULL,1,1.00,0.00,'General'),(2,'Producto 2',NULL,1,4.00,0.00,'General'),(3,'Producto 3',NULL,1,2.00,0.00,'General'),(4,'Producto 4',NULL,1,3.00,0.00,'General'),(5,'Producto 5',NULL,1,5.00,0.00,'General'),(6,'Producto 6',NULL,1,3.00,0.00,'Otra'),(7,'Producto 7 Update',NULL,1,50.00,0.00,'Nueva'),(8,'Producto 8',NULL,1,3.00,0.00,'Nueva'),(9,'Producto 9',NULL,1,3.00,0.00,'General'),(10,'Producto 10',NULL,1,0.00,0.00,'General'),(11,'yolanda',NULL,NULL,30.00,NULL,'General'),(12,'LaFinal2',NULL,NULL,10.00,NULL,'General'),(13,'Test',NULL,NULL,10.00,NULL,'General'),(35,'test2',NULL,NULL,5.00,NULL,'General'),(44,'test44',NULL,NULL,44.00,NULL,'General');
/*!40000 ALTER TABLE `Inventario` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `personal`
--

DROP TABLE IF EXISTS `personal`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `personal` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) NOT NULL,
  `apellido` varchar(100) NOT NULL,
  `tiempo` int DEFAULT NULL,
  `contrasena` varchar(128) NOT NULL,
  `tipo` varchar(10) NOT NULL DEFAULT 'user',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `personal`
--

LOCK TABLES `personal` WRITE;
/*!40000 ALTER TABLE `personal` DISABLE KEYS */;
INSERT INTO `personal` VALUES (1,'Naila','gutierrrez',0,'pbkdf2_sha256$100000$20eb927a37adacc7ead95297c3c98227$d1ea099a87e3fe052e2eeaa6dc53b4913c3505ffba66a5f89b434a74a1f9ff45','admin'),(3,'Deivys','Rodriguez',NULL,'pbkdf2_sha256$100000$121f0de17ef7008e64e2aa1ba3842e4c$d103b25accd17e2b0876744e38491849f18919e7f81a7520b0bddb7bedabf3c4','admin'),(4,'Jorge','Caraballo',NULL,'pbkdf2_sha256$100000$9625751eefd901ed9ed0d30c7f3094c4$046aa91eaccaac1c4fa460ac646bafb0b3b62b9d9895dad5b22e4dcd9ab0b8c3','user');
/*!40000 ALTER TABLE `personal` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `salidas`
--

DROP TABLE IF EXISTS `salidas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `salidas` (
  `id` int NOT NULL AUTO_INCREMENT,
  `inventario_id` int DEFAULT NULL,
  `nombre` varchar(50) DEFAULT NULL,
  `cantidad` int DEFAULT NULL,
  `costo` decimal(10,2) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `inventario_id` (`inventario_id`),
  CONSTRAINT `salidas_ibfk_1` FOREIGN KEY (`inventario_id`) REFERENCES `inventario` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `salidas`
--

LOCK TABLES `salidas` WRITE;
/*!40000 ALTER TABLE `salidas` DISABLE KEYS */;
INSERT INTO `salidas` VALUES (1,1,'Producto 1',2,4.00),(2,2,'Producto 2',NULL,NULL),(3,3,'Producto 3',NULL,NULL),(4,4,'Producto 4',NULL,NULL),(5,5,'Producto 5',NULL,NULL),(6,6,'Producto 6',NULL,NULL),(7,7,'Producto 7',NULL,NULL),(8,8,'Producto 8',NULL,NULL),(9,9,'Producto 9',NULL,NULL),(10,10,'Producto 10',NULL,NULL);
/*!40000 ALTER TABLE `salidas` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping events for database 'sistema_inventario'
--

--
-- Dumping routines for database 'sistema_inventario'
--
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-09-23  0:04:27
