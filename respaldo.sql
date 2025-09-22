-- MySQL dump 10.13  Distrib 9.4.0, for Win64 (x86_64)
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
INSERT INTO `entradas` VALUES (1,1,'Producto 1',3,4.00),(2,2,'Producto 2',NULL,NULL),(3,3,'Producto 3',NULL,NULL),(4,4,'Producto 4',NULL,NULL),(5,5,'Producto 5',NULL,NULL),(6,6,'Producto 6',NULL,NULL),(7,7,'Producto 7',NULL,NULL),(8,8,'Producto 8',NULL,NULL),(9,9,'Producto 9',NULL,NULL),(10,10,'Producto 10',NULL,NULL),(11,12,NULL,4524,456456.00);
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
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `existencia_inicial`
--

LOCK TABLES `existencia_inicial` WRITE;
/*!40000 ALTER TABLE `existencia_inicial` DISABLE KEYS */;
INSERT INTO `existencia_inicial` VALUES (1,1,'Producto 1',1,4.00),(2,2,'Producto 2',NULL,NULL),(3,3,'Producto 3',NULL,NULL),(4,4,'Producto 4',NULL,NULL),(5,5,'Producto 5',NULL,NULL),(6,6,'Producto 6',NULL,NULL),(7,7,'Producto 7',NULL,NULL),(8,8,'Producto 8',NULL,NULL),(9,9,'Producto 9',NULL,NULL),(10,10,'Producto 10',NULL,NULL),(11,11,NULL,25,25.00),(12,11,NULL,25,25.00),(13,11,NULL,25,25.00),(14,11,NULL,30,30.00),(15,12,NULL,456,456.00);
/*!40000 ALTER TABLE `existencia_inicial` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `inventario`
--

DROP TABLE IF EXISTS `inventario`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `inventario` (
  `id` int NOT NULL AUTO_INCREMENT,
  `descripcion_insumo` varchar(255) DEFAULT NULL,
  `tipo` varchar(25) DEFAULT NULL,
  `cantidad` int DEFAULT NULL,
  `costo_unitario` decimal(10,2) DEFAULT NULL,
  `monto_total` decimal(10,2) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `inventario`
--

LOCK TABLES `inventario` WRITE;
/*!40000 ALTER TABLE `inventario` DISABLE KEYS */;
INSERT INTO `inventario` VALUES (1,'Producto 1',NULL,1,3.00,0.00),(2,'Producto 2',NULL,1,4.00,0.00),(3,'Producto 3',NULL,1,2.00,0.00),(4,'Producto 4',NULL,1,3.00,0.00),(5,'Producto 5',NULL,1,3.00,0.00),(6,'Producto 6',NULL,1,3.00,0.00),(7,'Producto 7',NULL,1,3.00,0.00),(8,'Producto 8',NULL,1,3.00,0.00),(9,'Producto 9',NULL,1,3.00,0.00),(10,'Producto 10',NULL,1,0.00,0.00),(11,'yolanda',NULL,NULL,30.00,NULL),(12,'aaa',NULL,NULL,456456.00,NULL);
/*!40000 ALTER TABLE `inventario` ENABLE KEYS */;
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
  `contrasena` varchar(100) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `personal`
--

LOCK TABLES `personal` WRITE;
/*!40000 ALTER TABLE `personal` DISABLE KEYS */;
INSERT INTO `personal` VALUES (1,'Naila','gutierrrez',0,'Gato7Sol'),(2,'geerente','principal',0,'Gato7Sol');
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
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-09-21 21:25:41
