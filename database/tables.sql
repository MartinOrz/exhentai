 DROP TABLE IF EXISTS `tb_gallery`;
 CREATE TABLE `tb_gallery` (
   `id` BIGINT(20) UNSIGNED NOT NULL COMMENT '主键ID',
   `root_path` VARCHAR(100) NOT NULL COMMENT '根目录',
   `name` VARCHAR(255) NOT NULL COMMENT '名称',
   `name_n` VARCHAR(255) NOT NULL DEFAULT '' COMMENT '英文名称',
   `name_j` VARCHAR(255) NOT NULL DEFAULT '' COMMENT '日文名称',
   `type` TINYINT(4) NOT NULL DEFAULT 0 COMMENT '类型，1-同人志，2-漫画，3-CG，4-游戏CG，5-西方，6-无H，7-图集，8-COS，9-成人，10-杂项',
   `language` TINYINT(4) NOT NULL COMMENT '语言，1-日文，2-中文，3-英文',
   `translator` VARCHAR(255) NOT NULL DEFAULT '' COMMENT '汉化组',
   `pages` INT(11) NOT NULL DEFAULT 1 COMMENT '页面大小',
   `length` INT(11) NOT NULL COMMENT '长度',
   `posted` DATETIME NOT NULL COMMENT '发布时间',
   `is_anthology` TINYINT(4) NOT NULL DEFAULT 0 COMMENT '是否是杂志，0-不是，1-是',
   `rating` INT(11) NOT NULL DEFAULT 50 COMMENT '评分',
   `last_view` DATETIME NOT NULL DEFAULT NOW() COMMENT '最后浏览时间',
   PRIMARY KEY (`id`)
 ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='画集列表';
 
 DROP TABLE IF EXISTS `tb_artist`;
 CREATE TABLE `tb_artist` (
   `id` BIGINT(20) UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
   `name` VARCHAR(255) NOT NULL COMMENT '英文名称',
   `text` VARCHAR(255) NOT NULL COMMENT '中文名称',
   `refer` BIGINT(20) UNSIGNED NOT NULL DEFAULT 0 COMMENT '关联作者id，无则设置为0',
   `refer_name` VARCHAR(255) NOT NULL DEFAULT '' COMMENT '关联作者名称',
   `rating` INT(11) NOT NULL DEFAULT 50 COMMENT '评分',
   PRIMARY KEY (`id`)
 ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='画集列表';
 
 DROP TABLE IF EXISTS `tb_gallery_artist_relation`;
 CREATE TABLE `tb_gallery_artist_relation` (
   `id` BIGINT(20) UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
   `gallery_id` BIGINT(20) NOT NULL COMMENT '画集id',
   `artist_id` BIGINT(20) NOT NULL COMMENT '作者id',
   PRIMARY KEY (`id`),
   INDEX (`gallery_id`),
   INDEX (`artist_id`)
 ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='画集列表';
 
 DROP TABLE IF EXISTS `tb_group`;
 CREATE TABLE `tb_group` (
   `id` bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
   `name` VARCHAR(255) NOT NULL COMMENT '英文名称',
   `text` VARCHAR(255) NOT NULL COMMENT '中文名称',
   `refer` BIGINT(20) UNSIGNED NOT NULL DEFAULT 0 COMMENT '关联作者id，无则设置为0',
   `refer_name` VARCHAR(255) NOT NULL DEFAULT '' COMMENT '关联作者名称',
   `rating` INT(11) NOT NULL DEFAULT 50 COMMENT '评分',
   PRIMARY KEY (`id`)
 ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='画集列表';
 
 DROP TABLE IF EXISTS `tb_gallery_group_relation`;
 CREATE TABLE `tb_gallery_group_relation` (
   `id` BIGINT(20) UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
   `gallery_id` BIGINT(20) NOT NULL COMMENT '画集id',
   `group_id` BIGINT(20) NOT NULL COMMENT '作者id',
   PRIMARY KEY (`id`),
   INDEX (`gallery_id`),
   INDEX (`group_id`)
 ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='画集列表';