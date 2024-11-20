-- Team 8: TradeYourStyle --

use team8_db; 

drop table if exists `message`;
drop table if exists listing;
drop table if exists user;


CREATE TABLE `user` (
  `uid` integer not null PRIMARY KEY AUTO_INCREMENT,
  `username` varchar(30),
  `display_name` varchar(30),
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

CREATE TABLE `message` (
  `mid` int PRIMARY KEY AUTO_INCREMENT,
  `lis_id` int not null,
  `lister_uid` int not null,
  `comment_uid` int not null,
  `time_stamp` datetime
)
ENGINE = InnoDB;

ALTER TABLE `listing` ADD FOREIGN KEY (`uid`) REFERENCES `user` (`uid`) on update cascade on delete cascade;

ALTER TABLE `message` ADD FOREIGN KEY (`lis_id`) REFERENCES `listing` (`lis_id`) on update cascade on delete cascade;

ALTER TABLE `message` ADD FOREIGN KEY (`lister_uid`) REFERENCES `user` (`uid`) on update cascade on delete cascade;

ALTER TABLE `message` ADD FOREIGN KEY (`comment_uid`) REFERENCES `user` (`uid`) on update cascade on delete cascade;
