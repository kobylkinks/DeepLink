CREATE TABLE `rhlink`.`repo` (
  `id` INT NOT NULL AUTO_INCREMENT COMMENT '',
  `repo_id` INT NOT NULL COMMENT '',
  `url` VARCHAR(512) NOT NULL COMMENT '',
  `issues` INT NULL DEFAULT 0 COMMENT '',
  `true_links` INT NULL DEFAULT 0 COMMENT '',
  PRIMARY KEY (`id`)  COMMENT '');
