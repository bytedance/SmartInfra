/*M!999999\- enable the sandbox mode */
-- MariaDB dump 10.19-11.6.2-MariaDB, for debian-linux-gnu (x86_64)
--
-- Host: localhost    Database: smartinfra
-- ------------------------------------------------------
-- Server version	11.6.2-MariaDB-ubu2404

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*M!100616 SET @OLD_NOTE_VERBOSITY=@@NOTE_VERBOSITY, NOTE_VERBOSITY=0 */;

--
-- Table structure for table `auth_group`
--

DROP TABLE IF EXISTS `auth_group`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_group` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(150) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group`
--

LOCK TABLES `auth_group` WRITE;
/*!40000 ALTER TABLE `auth_group` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_group` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_group_permissions`
--

DROP TABLE IF EXISTS `auth_group_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_group_permissions` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `group_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_group_permissions_group_id_permission_id_0cd325b0_uniq` (`group_id`,`permission_id`),
  KEY `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` (`permission_id`),
  CONSTRAINT `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_group_permissions_group_id_b120cbf9_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group_permissions`
--

LOCK TABLES `auth_group_permissions` WRITE;
/*!40000 ALTER TABLE `auth_group_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_group_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_permission`
--

DROP TABLE IF EXISTS `auth_permission`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_permission` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `content_type_id` int(11) NOT NULL,
  `codename` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_permission_content_type_id_codename_01ab375a_uniq` (`content_type_id`,`codename`),
  CONSTRAINT `auth_permission_content_type_id_2f476e4b_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=93 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_permission`
--

LOCK TABLES `auth_permission` WRITE;
/*!40000 ALTER TABLE `auth_permission` DISABLE KEYS */;
INSERT INTO `auth_permission` VALUES
(1,'Can add log entry',1,'add_logentry'),
(2,'Can change log entry',1,'change_logentry'),
(3,'Can delete log entry',1,'delete_logentry'),
(4,'Can view log entry',1,'view_logentry'),
(5,'Can add permission',2,'add_permission'),
(6,'Can change permission',2,'change_permission'),
(7,'Can delete permission',2,'delete_permission'),
(8,'Can view permission',2,'view_permission'),
(9,'Can add group',3,'add_group'),
(10,'Can change group',3,'change_group'),
(11,'Can delete group',3,'delete_group'),
(12,'Can view group',3,'view_group'),
(13,'Can add user',4,'add_user'),
(14,'Can change user',4,'change_user'),
(15,'Can delete user',4,'delete_user'),
(16,'Can view user',4,'view_user'),
(17,'Can add content type',5,'add_contenttype'),
(18,'Can change content type',5,'change_contenttype'),
(19,'Can delete content type',5,'delete_contenttype'),
(20,'Can view content type',5,'view_contenttype'),
(21,'Can add session',6,'add_session'),
(22,'Can change session',6,'change_session'),
(23,'Can delete session',6,'delete_session'),
(24,'Can view session',6,'view_session'),
(25,'Can add salt_master',7,'add_salt_master'),
(26,'Can change salt_master',7,'change_salt_master'),
(27,'Can delete salt_master',7,'delete_salt_master'),
(28,'Can view salt_master',7,'view_salt_master'),
(29,'Can add shell_template',8,'add_shell_template'),
(30,'Can change shell_template',8,'change_shell_template'),
(31,'Can delete shell_template',8,'delete_shell_template'),
(32,'Can view shell_template',8,'view_shell_template'),
(33,'Can add acl_manage',9,'add_acl_manage'),
(34,'Can change acl_manage',9,'change_acl_manage'),
(35,'Can delete acl_manage',9,'delete_acl_manage'),
(36,'Can view acl_manage',9,'view_acl_manage'),
(37,'Can add resource_group',10,'add_resource_group'),
(38,'Can change resource_group',10,'change_resource_group'),
(39,'Can delete resource_group',10,'delete_resource_group'),
(40,'Can view resource_group',10,'view_resource_group'),
(41,'Can add rg_relationship',11,'add_rg_relationship'),
(42,'Can change rg_relationship',11,'change_rg_relationship'),
(43,'Can delete rg_relationship',11,'delete_rg_relationship'),
(44,'Can view rg_relationship',11,'view_rg_relationship'),
(45,'Can add user_relationship',12,'add_user_relationship'),
(46,'Can change user_relationship',12,'change_user_relationship'),
(47,'Can delete user_relationship',12,'delete_user_relationship'),
(48,'Can view user_relationship',12,'view_user_relationship'),
(49,'Can add hosts',13,'add_hosts'),
(50,'Can change hosts',13,'change_hosts'),
(51,'Can delete hosts',13,'delete_hosts'),
(52,'Can view hosts',13,'view_hosts'),
(53,'Can add authenticate_type',14,'add_authenticate_type'),
(54,'Can change authenticate_type',14,'change_authenticate_type'),
(55,'Can delete authenticate_type',14,'delete_authenticate_type'),
(56,'Can view authenticate_type',14,'view_authenticate_type'),
(57,'Can add general_audit',15,'add_general_audit'),
(58,'Can change general_audit',15,'change_general_audit'),
(59,'Can delete general_audit',15,'delete_general_audit'),
(60,'Can view general_audit',15,'view_general_audit'),
(61,'Can add host_group',16,'add_host_group'),
(62,'Can change host_group',16,'change_host_group'),
(63,'Can delete host_group',16,'delete_host_group'),
(64,'Can view host_group',16,'view_host_group'),
(65,'Can add host_group_minion',17,'add_host_group_minion'),
(66,'Can change host_group_minion',17,'change_host_group_minion'),
(67,'Can delete host_group_minion',17,'delete_host_group_minion'),
(68,'Can view host_group_minion',17,'view_host_group_minion'),
(69,'Can add task_list',18,'add_task_list'),
(70,'Can change task_list',18,'change_task_list'),
(71,'Can delete task_list',18,'delete_task_list'),
(72,'Can view task_list',18,'view_task_list'),
(73,'Can add Scheduled task',19,'add_schedule'),
(74,'Can change Scheduled task',19,'change_schedule'),
(75,'Can delete Scheduled task',19,'delete_schedule'),
(76,'Can view Scheduled task',19,'view_schedule'),
(77,'Can add task',20,'add_task'),
(78,'Can change task',20,'change_task'),
(79,'Can delete task',20,'delete_task'),
(80,'Can view task',20,'view_task'),
(81,'Can add Failed task',21,'add_failure'),
(82,'Can change Failed task',21,'change_failure'),
(83,'Can delete Failed task',21,'delete_failure'),
(84,'Can view Failed task',21,'view_failure'),
(85,'Can add Successful task',22,'add_success'),
(86,'Can change Successful task',22,'change_success'),
(87,'Can delete Successful task',22,'delete_success'),
(88,'Can view Successful task',22,'view_success'),
(89,'Can add Queued task',23,'add_ormq'),
(90,'Can change Queued task',23,'change_ormq'),
(91,'Can delete Queued task',23,'delete_ormq'),
(92,'Can view Queued task',23,'view_ormq');
/*!40000 ALTER TABLE `auth_permission` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_user`
--

DROP TABLE IF EXISTS `auth_user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_user` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `password` varchar(128) NOT NULL,
  `last_login` datetime(6) DEFAULT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `username` varchar(150) NOT NULL,
  `first_name` varchar(150) NOT NULL,
  `last_name` varchar(150) NOT NULL,
  `email` varchar(254) NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `date_joined` datetime(6) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=18 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_user`
--

LOCK TABLES `auth_user` WRITE;
/*!40000 ALTER TABLE `auth_user` DISABLE KEYS */;
INSERT INTO `auth_user` VALUES
(1,'pbkdf2_sha256$870000$HZ39jOJ8ZE7gUHHV6YY1Xn$n2LVoWf8zMbLokpYK+ORNQ/xqj8feYbE+EzBdMwHt6I=','2025-02-26 09:24:13.512656',1,'admin','','','luwanlong@bytedance.com',1,1,'2024-12-27 02:06:55.048078');
/*!40000 ALTER TABLE `auth_user` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_user_groups`
--

DROP TABLE IF EXISTS `auth_user_groups`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_user_groups` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `group_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_user_groups_user_id_group_id_94350c0c_uniq` (`user_id`,`group_id`),
  KEY `auth_user_groups_group_id_97559544_fk_auth_group_id` (`group_id`),
  CONSTRAINT `auth_user_groups_group_id_97559544_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`),
  CONSTRAINT `auth_user_groups_user_id_6a12ed8b_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_user_groups`
--

LOCK TABLES `auth_user_groups` WRITE;
/*!40000 ALTER TABLE `auth_user_groups` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_user_groups` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_user_user_permissions`
--

DROP TABLE IF EXISTS `auth_user_user_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_user_user_permissions` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_user_user_permissions_user_id_permission_id_14a6b632_uniq` (`user_id`,`permission_id`),
  KEY `auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm` (`permission_id`),
  CONSTRAINT `auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_user_user_permissions_user_id_a95ead1b_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_user_user_permissions`
--

LOCK TABLES `auth_user_user_permissions` WRITE;
/*!40000 ALTER TABLE `auth_user_user_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_user_user_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_admin_log`
--

DROP TABLE IF EXISTS `django_admin_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_admin_log` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `action_time` datetime(6) NOT NULL,
  `object_id` longtext DEFAULT NULL,
  `object_repr` varchar(200) NOT NULL,
  `action_flag` smallint(5) unsigned NOT NULL CHECK (`action_flag` >= 0),
  `change_message` longtext NOT NULL,
  `content_type_id` int(11) DEFAULT NULL,
  `user_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `django_admin_log_content_type_id_c4bce8eb_fk_django_co` (`content_type_id`),
  KEY `django_admin_log_user_id_c564eba6_fk_auth_user_id` (`user_id`),
  CONSTRAINT `django_admin_log_content_type_id_c4bce8eb_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `django_admin_log_user_id_c564eba6_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_admin_log`
--

LOCK TABLES `django_admin_log` WRITE;
/*!40000 ALTER TABLE `django_admin_log` DISABLE KEYS */;
/*!40000 ALTER TABLE `django_admin_log` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_content_type`
--

DROP TABLE IF EXISTS `django_content_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_content_type` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `app_label` varchar(100) NOT NULL,
  `model` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `django_content_type_app_label_model_76bd3d3b_uniq` (`app_label`,`model`)
) ENGINE=InnoDB AUTO_INCREMENT=24 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_content_type`
--

LOCK TABLES `django_content_type` WRITE;
/*!40000 ALTER TABLE `django_content_type` DISABLE KEYS */;
INSERT INTO `django_content_type` VALUES
(1,'admin','logentry'),
(3,'auth','group'),
(2,'auth','permission'),
(4,'auth','user'),
(5,'contenttypes','contenttype'),
(21,'django_q','failure'),
(23,'django_q','ormq'),
(19,'django_q','schedule'),
(22,'django_q','success'),
(20,'django_q','task'),
(9,'salt','acl_manage'),
(14,'salt','authenticate_type'),
(15,'salt','general_audit'),
(16,'salt','host_group'),
(17,'salt','host_group_minion'),
(13,'salt','hosts'),
(10,'salt','resource_group'),
(11,'salt','rg_relationship'),
(7,'salt','salt_master'),
(8,'salt','shell_template'),
(18,'salt','task_list'),
(12,'salt','user_relationship'),
(6,'sessions','session');
/*!40000 ALTER TABLE `django_content_type` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_migrations`
--

DROP TABLE IF EXISTS `django_migrations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_migrations` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `app` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `applied` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=57 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_migrations`
--

LOCK TABLES `django_migrations` WRITE;
/*!40000 ALTER TABLE `django_migrations` DISABLE KEYS */;
INSERT INTO `django_migrations` VALUES
(1,'contenttypes','0001_initial','2024-12-27 02:06:04.804480');
/*!40000 ALTER TABLE `django_migrations` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_q_ormq`
--

DROP TABLE IF EXISTS `django_q_ormq`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_q_ormq` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `key` varchar(100) NOT NULL,
  `payload` longtext NOT NULL,
  `lock` datetime(6) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2275 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_q_ormq`
--

LOCK TABLES `django_q_ormq` WRITE;
/*!40000 ALTER TABLE `django_q_ormq` DISABLE KEYS */;
/*!40000 ALTER TABLE `django_q_ormq` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_q_schedule`
--

DROP TABLE IF EXISTS `django_q_schedule`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_q_schedule` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `func` varchar(256) NOT NULL,
  `hook` varchar(256) DEFAULT NULL,
  `args` longtext DEFAULT NULL,
  `kwargs` longtext DEFAULT NULL,
  `schedule_type` varchar(2) NOT NULL,
  `repeats` int(11) NOT NULL,
  `next_run` datetime(6) DEFAULT NULL,
  `task` varchar(100) DEFAULT NULL,
  `name` varchar(100) DEFAULT NULL,
  `minutes` smallint(5) unsigned DEFAULT NULL CHECK (`minutes` >= 0),
  `cron` varchar(100) DEFAULT NULL,
  `cluster` varchar(100) DEFAULT NULL,
  `intended_date_kwarg` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=46 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

DROP TABLE IF EXISTS `django_q_task`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_q_task` (
  `name` varchar(100) NOT NULL,
  `func` varchar(256) NOT NULL,
  `hook` varchar(256) DEFAULT NULL,
  `args` longtext DEFAULT NULL,
  `kwargs` longtext DEFAULT NULL,
  `result` longtext DEFAULT NULL,
  `started` datetime(6) NOT NULL,
  `stopped` datetime(6) NOT NULL,
  `success` tinyint(1) NOT NULL,
  `id` varchar(32) NOT NULL,
  `group` varchar(100) DEFAULT NULL,
  `attempt_count` int(11) NOT NULL,
  `cluster` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `success_index` (`group`,`name`,`func`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

DROP TABLE IF EXISTS `django_session`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_session` (
  `session_key` varchar(40) NOT NULL,
  `session_data` longtext NOT NULL,
  `expire_date` datetime(6) NOT NULL,
  PRIMARY KEY (`session_key`),
  KEY `django_session_expire_date_a5c62663` (`expire_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `salt_acl_manage`
--

DROP TABLE IF EXISTS `salt_acl_manage`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `salt_acl_manage` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  `description` varchar(300) NOT NULL,
  `content` varchar(600) NOT NULL,
  `create_time` datetime(6) NOT NULL,
  `update_time` datetime(6) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `salt_authenticate_type`
--

DROP TABLE IF EXISTS `salt_authenticate_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `salt_authenticate_type` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `type` int(11) NOT NULL,
  `name` varchar(50) NOT NULL,
  `client_id` varchar(100) NOT NULL,
  `client_secret` varchar(200) NOT NULL,
  `redirect_url` varchar(300) NOT NULL,
  `authorization_url` varchar(300) NOT NULL,
  `access_token_url` varchar(300) NOT NULL,
  `resource_url` varchar(300) NOT NULL,
  `grant_type` varchar(200) NOT NULL,
  `create_time` datetime(6) NOT NULL,
  `update_time` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `salt_general_audit`
--

DROP TABLE IF EXISTS `salt_general_audit`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `salt_general_audit` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `action` varchar(50) NOT NULL,
  `extra_content` varchar(200) NOT NULL,
  `create_time` datetime(6) NOT NULL,
  `user_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `salt_general_audit_user_id_d076a8fa_fk_auth_user_id` (`user_id`),
  CONSTRAINT `salt_general_audit_user_id_d076a8fa_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3663 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `salt_host_group`
--

DROP TABLE IF EXISTS `salt_host_group`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `salt_host_group` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  `description` varchar(300) NOT NULL,
  `host_num` int(11) NOT NULL,
  `create_time` datetime(6) NOT NULL,
  `update_time` datetime(6) NOT NULL,
  `user_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  KEY `salt_host_group_user_id_ee21ea89_fk_auth_user_id` (`user_id`),
  CONSTRAINT `salt_host_group_user_id_ee21ea89_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `salt_host_group_minion`
--

DROP TABLE IF EXISTS `salt_host_group_minion`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `salt_host_group_minion` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `minion_name` varchar(300) NOT NULL,
  `create_time` datetime(6) NOT NULL,
  `update_time` datetime(6) NOT NULL,
  `host_group_name_id` bigint(20) DEFAULT NULL,
  `salt_name_id` bigint(20) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `salt_host_group_mini_host_group_name_id_7e1975a3_fk_salt_host` (`host_group_name_id`),
  KEY `salt_host_group_mini_salt_name_id_dfc7b59e_fk_salt_salt` (`salt_name_id`),
  CONSTRAINT `salt_host_group_mini_host_group_name_id_7e1975a3_fk_salt_host` FOREIGN KEY (`host_group_name_id`) REFERENCES `salt_host_group` (`id`),
  CONSTRAINT `salt_host_group_mini_salt_name_id_dfc7b59e_fk_salt_salt` FOREIGN KEY (`salt_name_id`) REFERENCES `salt_salt_master` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=53 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `salt_hosts`
--

DROP TABLE IF EXISTS `salt_hosts`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `salt_hosts` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `name` varchar(300) NOT NULL,
  `status` int(11) NOT NULL,
  `create_time` datetime(6) NOT NULL,
  `update_time` datetime(6) NOT NULL,
  `salt_id` bigint(20) DEFAULT NULL,
  `label` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `salt_hosts_salt_id_11462b13_fk_salt_salt_master_id` (`salt_id`),
  CONSTRAINT `salt_hosts_salt_id_11462b13_fk_salt_salt_master_id` FOREIGN KEY (`salt_id`) REFERENCES `salt_salt_master` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=367179 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `salt_resource_group`
--

DROP TABLE IF EXISTS `salt_resource_group`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `salt_resource_group` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  `description` varchar(300) NOT NULL,
  `create_time` datetime(6) NOT NULL,
  `update_time` datetime(6) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `salt_rg_relationship`
--

DROP TABLE IF EXISTS `salt_rg_relationship`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `salt_rg_relationship` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `create_time` datetime(6) NOT NULL,
  `update_time` datetime(6) NOT NULL,
  `rg_id` bigint(20) DEFAULT NULL,
  `salt_id` bigint(20) DEFAULT NULL,
  `acl_id` bigint(20) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `salt_rg_relationship_rg_id_42752ef5_fk_salt_resource_group_id` (`rg_id`),
  KEY `salt_rg_relationship_salt_id_f0b605aa_fk_salt_salt_master_id` (`salt_id`),
  KEY `salt_rg_relationship_acl_id_12a89c7e_fk_salt_acl_manage_id` (`acl_id`),
  CONSTRAINT `salt_rg_relationship_acl_id_12a89c7e_fk_salt_acl_manage_id` FOREIGN KEY (`acl_id`) REFERENCES `salt_acl_manage` (`id`),
  CONSTRAINT `salt_rg_relationship_rg_id_42752ef5_fk_salt_resource_group_id` FOREIGN KEY (`rg_id`) REFERENCES `salt_resource_group` (`id`),
  CONSTRAINT `salt_rg_relationship_salt_id_f0b605aa_fk_salt_salt_master_id` FOREIGN KEY (`salt_id`) REFERENCES `salt_salt_master` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `salt_salt_master`
--

DROP TABLE IF EXISTS `salt_salt_master`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `salt_salt_master` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  `description` varchar(300) NOT NULL,
  `host` varchar(200) NOT NULL,
  `user` varchar(200) NOT NULL,
  `password` varchar(300) NOT NULL,
  `create_time` datetime(6) NOT NULL,
  `update_time` datetime(6) NOT NULL,
  `file_roots` varchar(300) NOT NULL,
  `minion_name` varchar(300) NOT NULL,
  `sftp_user` varchar(200) NOT NULL,
  `sftp_password` varchar(300) NOT NULL,
  `sftp_port` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `salt_shell_template`
--

DROP TABLE IF EXISTS `salt_shell_template`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `salt_shell_template` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `description` varchar(500) NOT NULL,
  `create_time` datetime(6) NOT NULL,
  `update_time` datetime(6) NOT NULL,
  `user_id` int(11) DEFAULT NULL,
  `file_name` varchar(100) NOT NULL,
  `func_content` longtext NOT NULL,
  `main_content` longtext NOT NULL,
  `type` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  KEY `salt_shell_template_user_id_d8ac0389_fk_auth_user_id` (`user_id`),
  CONSTRAINT `salt_shell_template_user_id_d8ac0389_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `salt_task_list`
--

DROP TABLE IF EXISTS `salt_task_list`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `salt_task_list` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `name` varchar(500) NOT NULL,
  `execute_content` longtext NOT NULL,
  `execute_policy` varchar(50) NOT NULL,
  `status` int(11) NOT NULL,
  `execute_result` varchar(600) NOT NULL,
  `related_schedule` int(11) NOT NULL,
  `create_time` datetime(6) NOT NULL,
  `update_time` datetime(6) NOT NULL,
  `host_group_name_id` bigint(20) DEFAULT NULL,
  `user_id` int(11) DEFAULT NULL,
  `approve_result` longtext NOT NULL,
  `approver_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `salt_task_list_host_group_name_id_73d2eb5e_fk_salt_host_group_id` (`host_group_name_id`),
  KEY `salt_task_list_user_id_54bb8222_fk_auth_user_id` (`user_id`),
  KEY `salt_task_list_approver_id_544f4531_fk_auth_user_id` (`approver_id`),
  CONSTRAINT `salt_task_list_approver_id_544f4531_fk_auth_user_id` FOREIGN KEY (`approver_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `salt_task_list_host_group_name_id_73d2eb5e_fk_salt_host_group_id` FOREIGN KEY (`host_group_name_id`) REFERENCES `salt_host_group` (`id`),
  CONSTRAINT `salt_task_list_user_id_54bb8222_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=45 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `salt_transfer_file`
--

DROP TABLE IF EXISTS `salt_transfer_file`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `salt_transfer_file` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `name` varchar(300) NOT NULL,
  `create_time` datetime(6) NOT NULL,
  `update_time` datetime(6) NOT NULL,
  `user_id` int(11) DEFAULT NULL,
  `dest_dir` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL CHECK (json_valid(`dest_dir`)),
  PRIMARY KEY (`id`),
  UNIQUE KEY `salt_transfer_file_name_1cfbf2df_uniq` (`name`),
  KEY `salt_transfer_file_user_id_2c55a619_fk_auth_user_id` (`user_id`),
  CONSTRAINT `salt_transfer_file_user_id_2c55a619_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=35 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `salt_user_relationship`
--

DROP TABLE IF EXISTS `salt_user_relationship`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `salt_user_relationship` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `create_time` datetime(6) NOT NULL,
  `update_time` datetime(6) NOT NULL,
  `rg_id` bigint(20) DEFAULT NULL,
  `user_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `salt_user_all_relati_rg_id_745e7224_fk_salt_reso` (`rg_id`),
  KEY `salt_user_all_relationship_user_id_c1a9ea4c_fk_auth_user_id` (`user_id`),
  CONSTRAINT `salt_user_all_relati_rg_id_745e7224_fk_salt_reso` FOREIGN KEY (`rg_id`) REFERENCES `salt_resource_group` (`id`),
  CONSTRAINT `salt_user_all_relationship_user_id_c1a9ea4c_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*M!100616 SET NOTE_VERBOSITY=@OLD_NOTE_VERBOSITY */;

-- Dump completed on 2025-03-30 15:39:31
