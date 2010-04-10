


Data signatures
===============

The config object:

  config.sensors = []

  config.optic_sensor[i].type = 'optic'
  config.optic_sensor[i].id = 'id'

  config.optic_sensor[i].num_photoreceptors
  config.optic_sensor[i].directions
  config.optic_sensor[i].image_representation
  config.optic_sensor[i].image_sub_mask
  config.optic_sensor[i].image_sup_mask

  config.range_sensor[i].type = 'range'
  config.range_sensor[i].id   = 'id'
  config.range_sensor[i].directions  

  config.num_raw_pixels
  config.pixel2sensor[j] is 



The data object has everything the config has, plus the following:

	data.timestamp

	data.raw_pixels
	


	
