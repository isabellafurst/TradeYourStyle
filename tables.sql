-- Team 8: TradeYourStyle --

use team8_db; 

DROP TABLE IF EXISTS comment;
drop table if exists listing;
drop table if exists user;

CREATE TABLE `user` (
  `uid` integer not null PRIMARY KEY AUTO_INCREMENT,
  `username` varchar(50) not null,
  `display_name` varchar(30),
  hashed char(60),
  unique(username),
  index(username),
  `email` varchar(50)
)
ENGINE = InnoDB;

CREATE TABLE `listing` (
  `lis_id` integer not null PRIMARY KEY AUTO_INCREMENT,
  `uid` int not null,
  `item_image` varchar(50),
  `item_desc` varchar(100),
  `item_type` enum("shirt","pants","shorts","skirt","outerwear","shoes","accessories","dress","other"),
  `item_color` enum("multicolor","black","white","brown","gray","red","orange","yellow","green","blue","purple","pink","gold","silver"),
  `item_usage` enum("new","like-new","well-loved","needs work","trash it"),
  `item_price` enum("$","$$","$$$"),
  `item_size` enum("XS","S","M","L","XL","XXL"),
  `trade_type` boolean,
  `item_status` boolean,
  `post_date` datetime DEFAULT CURRENT_TIMESTAMP
)
ENGINE = InnoDB;

CREATE TABLE `comment` (
  `cid` INT AUTO_INCREMENT PRIMARY KEY,
  `lis_id` INT NOT NULL,
  `uid` INT NOT NULL,
  `parent_id` INT DEFAULT NULL,
  `text` TEXT NOT NULL,
  `post_date` DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (`lis_id`) REFERENCES `listing`(`lis_id`) ON DELETE CASCADE,
  FOREIGN KEY (`uid`) REFERENCES `user`(`uid`) ON DELETE CASCADE,
  FOREIGN KEY (`parent_id`) REFERENCES `comment`(`cid`) ON DELETE SET NULL
)
ENGINE=InnoDB;


ALTER TABLE `listing` ADD FOREIGN KEY (`uid`) REFERENCES `user` (`uid`) on update cascade on delete cascade;