const defaultProfile = {
	't_relais_on': 40,
	't_relais_off': 70,
	't_air_intake_close_half': 35,
	't_air_intake_close': 45,
	't_air_intake_open': 65,
	'air_intake_opening_at_full_burn': 0
}

export const profiles = {
	'default':{
		...defaultProfile
	}, 
	'bjork': {
		...defaultProfile
	},
	'gran': {
		...defaultProfile,
		'air_intake_opening_at_full_burn': 20
	}
}
