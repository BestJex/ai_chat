/*
Navicat MySQL Data Transfer

Source Server         : 172.21.66.211
Source Server Version : 50637
Source Host           : 172.21.66.211:3306
Source Database       : ai_chat

Target Server Type    : MYSQL
Target Server Version : 50637
File Encoding         : 65001

Date: 2018-08-03 02:10:14
*/

SET FOREIGN_KEY_CHECKS=0;

-- ----------------------------
-- Table structure for app_knowgraphs
-- ----------------------------
DROP TABLE IF EXISTS `app_knowgraphs`;
CREATE TABLE `app_knowgraphs` (
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `id` varchar(50) NOT NULL,
  `kg_version` int(11) NOT NULL,
  `train_state` smallint(6) NOT NULL,
  `in_use` tinyint(1) NOT NULL,
  `know_base_id` varchar(50) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `app_knowgraphs_know_base_id_8866824b_fk_app_lexiconindexes_id` (`know_base_id`),
  CONSTRAINT `app_knowgraphs_know_base_id_8866824b_fk_app_lexiconindexes_id` FOREIGN KEY (`know_base_id`) REFERENCES `app_lexiconindexes` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for app_lexiconindexes
-- ----------------------------
DROP TABLE IF EXISTS `app_lexiconindexes`;
CREATE TABLE `app_lexiconindexes` (
  `is_delete` tinyint(1) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `id` varchar(50) NOT NULL,
  `lexicon_type` smallint(6) NOT NULL,
  `is_general` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for app_lexiconmaps
-- ----------------------------
DROP TABLE IF EXISTS `app_lexiconmaps`;
CREATE TABLE `app_lexiconmaps` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `wb_type` smallint(6) NOT NULL,
  `know_base_id` varchar(50) NOT NULL,
  `word_bank_id` varchar(50) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `app_lexiconmaps_word_bank_id_know_base_id_7a414d3c_idx` (`word_bank_id`,`know_base_id`),
  KEY `app_lexiconmaps_know_base_id_b01b9da9_fk_app_lexiconindexes_id` (`know_base_id`),
  CONSTRAINT `app_lexiconmaps_know_base_id_b01b9da9_fk_app_lexiconindexes_id` FOREIGN KEY (`know_base_id`) REFERENCES `app_lexiconindexes` (`id`),
  CONSTRAINT `app_lexiconmaps_word_bank_id_437305b4_fk_app_lexiconindexes_id` FOREIGN KEY (`word_bank_id`) REFERENCES `app_lexiconindexes` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for app_questions
-- ----------------------------
DROP TABLE IF EXISTS `app_questions`;
CREATE TABLE `app_questions` (
  `is_delete` tinyint(1) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `id` varchar(50) NOT NULL,
  `content` varchar(256) NOT NULL,
  `is_subordinate` tinyint(1) NOT NULL,
  `answer` varchar(50) NOT NULL,
  `kb_id` varchar(50) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `app_questions_kb_id_561b6b38_fk_app_lexiconindexes_id` (`kb_id`),
  CONSTRAINT `app_questions_kb_id_561b6b38_fk_app_lexiconindexes_id` FOREIGN KEY (`kb_id`) REFERENCES `app_lexiconindexes` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for app_synonyms
-- ----------------------------
DROP TABLE IF EXISTS `app_synonyms`;
CREATE TABLE `app_synonyms` (
  `is_delete` tinyint(1) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `id` varchar(50) NOT NULL,
  `content` varchar(50) NOT NULL,
  `is_subordinate` tinyint(1) NOT NULL,
  `basic_id` varchar(50) NOT NULL,
  `wb_id` varchar(50) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `app_synonyms_basic_id_59404951_fk_app_synonyms_id` (`basic_id`),
  KEY `app_synonyms_wb_id_f52e11c3_fk_app_lexiconindexes_id` (`wb_id`),
  CONSTRAINT `app_synonyms_basic_id_59404951_fk_app_synonyms_id` FOREIGN KEY (`basic_id`) REFERENCES `app_synonyms` (`id`),
  CONSTRAINT `app_synonyms_wb_id_f52e11c3_fk_app_lexiconindexes_id` FOREIGN KEY (`wb_id`) REFERENCES `app_lexiconindexes` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for app_trainingmission
-- ----------------------------
DROP TABLE IF EXISTS `app_trainingmission`;
CREATE TABLE `app_trainingmission` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `is_delete` tinyint(1) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `company_id` varchar(50) NOT NULL,
  `kg_version` int(11) NOT NULL,
  `status` smallint(6) NOT NULL,
  `know_base_id` varchar(50) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `app_trainingmission_know_base_id_dd5fcbd7_fk_app_lexic` (`know_base_id`),
  CONSTRAINT `app_trainingmission_know_base_id_dd5fcbd7_fk_app_lexic` FOREIGN KEY (`know_base_id`) REFERENCES `app_lexiconindexes` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=463 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for app_trainpubhistory
-- ----------------------------
DROP TABLE IF EXISTS `app_trainpubhistory`;
CREATE TABLE `app_trainpubhistory` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `action` smallint(6) NOT NULL,
  `kb_id` varchar(50) NOT NULL,
  `kg_id` varchar(50) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `app_trainpubhistory_kb_id_ecad355e_fk_app_lexiconindexes_id` (`kb_id`),
  KEY `app_trainpubhistory_kg_id_2d68ddb9` (`kg_id`),
  CONSTRAINT `app_trainpubhistory_kb_id_ecad355e_fk_app_lexiconindexes_id` FOREIGN KEY (`kb_id`) REFERENCES `app_lexiconindexes` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=463 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for app_words
-- ----------------------------
DROP TABLE IF EXISTS `app_words`;
CREATE TABLE `app_words` (
  `is_delete` tinyint(1) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `id` varchar(50) NOT NULL,
  `content` varchar(50) NOT NULL,
  `word_character` smallint(6) NOT NULL,
  `wb_id` varchar(50) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `app_words_wb_id_92d9dd72_fk_app_lexiconindexes_id` (`wb_id`),
  CONSTRAINT `app_words_wb_id_92d9dd72_fk_app_lexiconindexes_id` FOREIGN KEY (`wb_id`) REFERENCES `app_lexiconindexes` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for auth_group
-- ----------------------------
DROP TABLE IF EXISTS `auth_group`;
CREATE TABLE `auth_group` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(80) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for auth_group_permissions
-- ----------------------------
DROP TABLE IF EXISTS `auth_group_permissions`;
CREATE TABLE `auth_group_permissions` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `group_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_group_permissions_group_id_permission_id_0cd325b0_uniq` (`group_id`,`permission_id`),
  KEY `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` (`permission_id`),
  CONSTRAINT `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_group_permissions_group_id_b120cbf9_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for auth_permission
-- ----------------------------
DROP TABLE IF EXISTS `auth_permission`;
CREATE TABLE `auth_permission` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `content_type_id` int(11) NOT NULL,
  `codename` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_permission_content_type_id_codename_01ab375a_uniq` (`content_type_id`,`codename`),
  CONSTRAINT `auth_permission_content_type_id_2f476e4b_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=43 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for auth_user
-- ----------------------------
DROP TABLE IF EXISTS `auth_user`;
CREATE TABLE `auth_user` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `password` varchar(128) NOT NULL,
  `last_login` datetime(6) DEFAULT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `username` varchar(150) NOT NULL,
  `first_name` varchar(30) NOT NULL,
  `last_name` varchar(150) NOT NULL,
  `email` varchar(254) NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `date_joined` datetime(6) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for auth_user_groups
-- ----------------------------
DROP TABLE IF EXISTS `auth_user_groups`;
CREATE TABLE `auth_user_groups` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `group_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_user_groups_user_id_group_id_94350c0c_uniq` (`user_id`,`group_id`),
  KEY `auth_user_groups_group_id_97559544_fk_auth_group_id` (`group_id`),
  CONSTRAINT `auth_user_groups_group_id_97559544_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`),
  CONSTRAINT `auth_user_groups_user_id_6a12ed8b_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for auth_user_user_permissions
-- ----------------------------
DROP TABLE IF EXISTS `auth_user_user_permissions`;
CREATE TABLE `auth_user_user_permissions` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_user_user_permissions_user_id_permission_id_14a6b632_uniq` (`user_id`,`permission_id`),
  KEY `auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm` (`permission_id`),
  CONSTRAINT `auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_user_user_permissions_user_id_a95ead1b_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for django_admin_log
-- ----------------------------
DROP TABLE IF EXISTS `django_admin_log`;
CREATE TABLE `django_admin_log` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `action_time` datetime(6) NOT NULL,
  `object_id` longtext,
  `object_repr` varchar(200) NOT NULL,
  `action_flag` smallint(5) unsigned NOT NULL,
  `change_message` longtext NOT NULL,
  `content_type_id` int(11) DEFAULT NULL,
  `user_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `django_admin_log_content_type_id_c4bce8eb_fk_django_co` (`content_type_id`),
  KEY `django_admin_log_user_id_c564eba6_fk` (`user_id`),
  CONSTRAINT `django_admin_log_content_type_id_c4bce8eb_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `django_admin_log_user_id_c564eba6_fk` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for django_content_type
-- ----------------------------
DROP TABLE IF EXISTS `django_content_type`;
CREATE TABLE `django_content_type` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `app_label` varchar(100) NOT NULL,
  `model` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `django_content_type_app_label_model_76bd3d3b_uniq` (`app_label`,`model`)
) ENGINE=InnoDB AUTO_INCREMENT=15 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for django_migrations
-- ----------------------------
DROP TABLE IF EXISTS `django_migrations`;
CREATE TABLE `django_migrations` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `app` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `applied` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for django_session
-- ----------------------------
DROP TABLE IF EXISTS `django_session`;
CREATE TABLE `django_session` (
  `session_key` varchar(40) NOT NULL,
  `session_data` longtext NOT NULL,
  `expire_date` datetime(6) NOT NULL,
  PRIMARY KEY (`session_key`),
  KEY `django_session_expire_date_a5c62663` (`expire_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
