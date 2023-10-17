export class Profile {

	constructor() {
		this.values = {
			't_relais_on': 40,
			't_relais_off': 70,
			't_air_intake_close_half': 35,
			't_air_intake_close': 45,
			't_air_intake_open': 65,
			'air_intake_opening_at_full_burn': 0
		}
	}

	getValues() {
		return this.values;
	}

	updateValue(key, value) {
		if (key in this.values) {
			this.values[key] = value;
			return 200;
		} else {
			return 400;
		}
	}

}
