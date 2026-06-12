ALTER TABLE `nb_farm_market`
  ADD COLUMN `image` varchar(500) NULL DEFAULT NULL COMMENT 'market image' AFTER `region_id`;
