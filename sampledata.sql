use team8_db;

insert into `user` (`username`, `display_name`, `email`)
values 
('user1', 'User One', 'use1@fake.com'),
('user2', 'User Two', 'use2@fake.com'),
('user3', 'User Three', 'use3@fake.com');

insert into `listing` (`uid`, `item_image`, `item_desc`, `item_type`, `item_color`, `item_usage`, `item_price`, `item_size`, `trade_type`, `item_status`, `post_date`)
values 
(1, 'shirt.jpg', 'red brandy melville shirt worn once', 'shirt', 'red', 'like-new', '$$', 'M', true, true, '2024-11-19 10:00:00'),
(2, 'pants.jpg', 'Blue vintage Levi jeans with a slight tear on the pocket', 'pants', 'blue', 'well-loved', '$$', 'L', false, true, '2024-11-19 12:00:00'),
(3, 'skirt.jpg', 'Skirt from Forever 21 with some loose threads', 'skirt', 'black', 'needs work', '$', 'XL', true, false, '2024-11-19 14:00:00');
