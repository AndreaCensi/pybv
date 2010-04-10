


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
	


	
Map format::

	{ 
		"class": "map", 

		"objects": [
			{ 
				"class": "polyline", 
				"surface_id": 0,  
				"points": [ [-1, -1], [-1, 1], [1, 1], [1, -1], [-1, -1] ], 
				"texture":  "lambda x: sign(sin(x))"
			},
			
			{ 
				"class": "circle", 
				"surface_id": 1,  
				"radius": 10, 
				"center": [0,0],
				"texture": "lambda x: 1" 
			}
		]
	}