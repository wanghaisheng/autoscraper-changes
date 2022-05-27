DROP TABLE IF EXISTS `shops`;
create table 'shops' (
  `id` integer unsigned not null primary key auto_increment comment 'pk',
  'domain' varchar(1200) CHARACTER SET utf8mb4  NOT NULL COMMENT 'domain url',
  'subdomains' varchar(1200) CHARACTER SET utf8mb4  NULL DEFAULT '[]' COMMENT '----',
  'ecommerce_platform' varchar(1200) CHARACTER SET utf8mb4  NULL DEFAULT '-' COMMENT '----',
  'logo' varchar(1200) CHARACTER SET utf8mb4  NULL DEFAULT '-' COMMENT '----',
  'monthly_traffic' varchar(1200) CHARACTER SET utf8mb4  NULL DEFAULT '-' COMMENT '----',
  'alexa_url_info_rank' varchar(1200) CHARACTER SET utf8mb4  NULL DEFAULT '-' COMMENT '----',
  'product_count' varchar(32) CHARACTER SET utf8mb4  NULL DEFAULT '0' COMMENT 'product page count',
  'collection_count' varchar(32) CHARACTER SET utf8mb4  NULL DEFAULT '0' COMMENT 'collection page count',
  'domain_register_date' varchar(1200) CHARACTER SET utf8mb4  NULL DEFAULT '-' COMMENT '----',
  'first_backlink_date' varchar(1200) CHARACTER SET utf8mb4  NULL DEFAULT '-' COMMENT '----',
  'backlink_count' varchar(32) CHARACTER SET utf8mb4  NULL DEFAULT '0' COMMENT 'backlink count',
  'dead_or_alive' boolean,
  'merchantgenius_url' varchar(1200) CHARACTER SET utf8mb4  NULL DEFAULT '-' COMMENT '----',
  'company_name' varchar(1200) CHARACTER SET utf8mb4  NULL DEFAULT '-' COMMENT '----',
  'ecommerce_categories' varchar(1200) CHARACTER SET utf8mb4  NULL DEFAULT '-' COMMENT '----',
  'blog_count' varchar(32) CHARACTER SET utf8mb4  NULL DEFAULT '0' COMMENT 'blog page count',
  `inserted_at` timestamp not NULL DEFAULT CURRENT_TIMESTAMP COMMENT '插入时间',
  `modify_at` timestamp DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '最后操作时间',  
  constraint unique index unq_index(`domain`)

)ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT 'shop info';

DROP TABLE IF EXISTS `shop_locs`;

create table 'shop_locs' (
  `id` integer unsigned not null primary key auto_increment comment 'pk',
  'domain' varchar(1200) CHARACTER SET utf8mb4  NOT NULL COMMENT '----',
  'shopid' integer unsigned,
  'loc' varchar(500) CHARACTER SET utf8mb4  NULL DEFAULT '-' COMMENT 'loc',
  'loc_lastmod' varchar(120) CHARACTER SET utf8mb4  NULL DEFAULT '-' COMMENT 'loc url modify',
  'sitemap' varchar(500) CHARACTER SET utf8mb4  NULL DEFAULT '-' COMMENT 'sitemap index url',
  'etag' varchar(120) CHARACTER SET utf8mb4  NULL DEFAULT '-' COMMENT '----',
  'sitemap_last_modified' varchar(120) CHARACTER SET utf8mb4  NULL DEFAULT '-' COMMENT '----',
  'sitemap_size_mb' varchar(30) CHARACTER SET utf8mb4  NULL DEFAULT '-' COMMENT '----',
  'download_date' varchar(120) CHARACTER SET utf8mb4  NULL DEFAULT '-' COMMENT '----',
  `inserted_at` timestamp not NULL DEFAULT CURRENT_TIMESTAMP COMMENT '插入时间',
  `modify_at` timestamp DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '最后操作时间',  
  FOREIGN KEY('shopid') REFERENCES shops('id')
)ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT 'shop url info';
