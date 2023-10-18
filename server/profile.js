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

	/**
	 * Returns the current state of all profile values
	 * 
	 * @returns {object} Profile parameter values
	 */
	getValues() {
		return this.values;
	}

	/**
	 * Update a specific profile value
	 * 
	 * @param {string} key Name of the parameter value
	 * @param {string|number} value Value of the parameter value
	 * 
	 * @returns {boolean} Flag indidicates if value was successfully updated or not
	 */
	updateValue(key, value) {
		if (key in this.values) {
			this.values[key] = value;
			return true;
		} else {
			return false;
		}
	}

}
