CREATE DATABASE IF NOT EXISTS `dmarc_reports`;
USE `dmarc_reports`;

CREATE TABLE IF NOT EXISTS `report_metadata` (
  `uid` varchar(36) NOT NULL,
  `organization` varchar(255) DEFAULT NULL,
  `email` varchar(255) DEFAULT NULL,
  `extra_contact_info` varchar(255) DEFAULT NULL,
  `report_id` varchar(255) DEFAULT NULL,
  `date_begin` int(11) DEFAULT NULL,
  `date_end` int(11) DEFAULT NULL,
  PRIMARY KEY (`uid`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

CREATE TABLE IF NOT EXISTS `record` (
  `uid` varchar(36) NOT NULL,
  `source_ip` varchar(15) DEFAULT NULL,
  `count` int(11) DEFAULT NULL,
  `disposition` varchar(255) DEFAULT NULL,
  `dkim` varchar(255) DEFAULT NULL,
  `spf` varchar(255) DEFAULT NULL,
  `_type` varchar(255) DEFAULT NULL,
  `comment` varchar(255) DEFAULT NULL,
  `header_from` varchar(255) DEFAULT NULL,
  `dkim_domain` varchar(255) DEFAULT NULL,
  `dkim_result` varchar(255) DEFAULT NULL,
  `dkim_hresult` varchar(255) DEFAULT NULL,
  `spf_domain` varchar(255) DEFAULT NULL,
  `spf_result` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`uid`),
  CONSTRAINT `record_ibfk_1` FOREIGN KEY (`uid`) REFERENCES `report_metadata` (`uid`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

CREATE TABLE IF NOT EXISTS `policy_published` (
  `uid` varchar(255) NOT NULL,
  `domain` varchar(255) DEFAULT NULL,
  `adkim` varchar(255) DEFAULT NULL,
  `aspf` varchar(255) DEFAULT NULL,
  `p` varchar(255) DEFAULT NULL,
  `pct` int(11) DEFAULT NULL,
  PRIMARY KEY (`uid`),
  CONSTRAINT `policy_published_ibfk_1` FOREIGN KEY (`uid`) REFERENCES `report_metadata` (`uid`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
