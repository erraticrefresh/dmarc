CREATE DATABASE IF NOT EXISTS `dmarc_reports`;
USE `dmarc_reports`;

CREATE USER IF NOT EXISTS 'dmarc'@'localhost' IDENTIFIED BY 'password';
GRANT INSERT ON dmarc_reports.* TO 'dmarc'@'localhost';

CREATE TABLE IF NOT EXISTS `report_metadata` (
  `uid` varchar(36) NOT NULL,
  `organization` varchar(255) DEFAULT NULL,
  `email` varchar(255) DEFAULT NULL,
  `extra_contact_info` varchar(255) DEFAULT NULL,
  `report_id` varchar(36) DEFAULT NULL,
  `date_begin` DATETIME,
  `date_end` DATETIME,
  `errors` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`uid`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

CREATE TABLE IF NOT EXISTS `record` (
  `uid` varchar(36) NOT NULL,
  `source_ip` varchar(15) DEFAULT NULL,
  `count` int(11) DEFAULT NULL,
  `disposition` varchar(10) DEFAULT NULL,
  `dkim` varchar(4) DEFAULT NULL,
  `spf` varchar(4) DEFAULT NULL,
  `type` varchar(20) DEFAULT NULL,
  `comment` varchar(255) DEFAULT NULL,
  `header_from` varchar(255) DEFAULT NULL,
  `envelope_from` varchar(255) DEFAULT NULL,
  `dkim_domain` varchar(255) DEFAULT NULL,
  `dkim_result` varchar(9) DEFAULT NULL,
  `dkim_hresult` varchar(9) DEFAULT NULL,
  `spf_domain` varchar(255) DEFAULT NULL,
  `spf_result` varchar(9) DEFAULT NULL,
  PRIMARY KEY (`uid`),
  CONSTRAINT `record_ibfk_1` FOREIGN KEY (`uid`) REFERENCES `report_metadata` (`uid`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

CREATE TABLE IF NOT EXISTS `policy_published` (
  `uid` varchar(36) NOT NULL,
  `domain` varchar(255) DEFAULT NULL,
  `adkim` varchar(2) DEFAULT NULL,
  `aspf` varchar(2) DEFAULT NULL,
  `p` varchar(10) DEFAULT NULL,
  `pct` varchar(3) DEFAULT NULL,
  `fo` varchar(9) DEFAULT NULL,
  `rf` varchar(9) DEFAULT NULL,
  `ri` varchar(11) DEFAULT NULL,
  `rua` varchar(255) DEFAULT NULL,
  `ruf` varchar(255) DEFAULT NULL,
  `v` varchar(6) DEFAULT NULL,
  PRIMARY KEY (`uid`),
  CONSTRAINT `policy_published_ibfk_1` FOREIGN KEY (`uid`) REFERENCES `report_metadata` (`uid`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
