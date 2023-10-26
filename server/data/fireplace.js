export class Fireplace {

	constructor() {
		this.parameter = {
			't_relais_on': 40, //22, //40,
			't_relais_off': 70, //18, //70,
			't_air_intake_close_half': 35, //20, //35,
			't_air_intake_close': 45, //24, //45,
			't_air_intake_open': 65, //20, //65,
			'air_intake_opening_at_full_burn': 25, //0
		};

		this.state = {
			'heating_state': 0,
			'temperature': 0,
			'pump': 0,
			'servo': 100,
			'boost': 0,
			'final': 0
		};

		this.boost = {
			'started': -1,
			'duration': 2*60,  // Seconds
			'timeout': undefined
		}
	}

	/**
	 * Returns remaining time for fireplace boost
	 * 
	 * @returns {number}: Remaining time in seconds
	 */
	getBoostTime() {
		return parseInt(this.boost.duration - (Date.now() - this.boost.started)/1000);
	}

	/**
	 * Returns the current state of all profile values
	 * 
	 * @returns {object} Profile parameter values
	 */
	getParameter() {
		return this.parameter;
	}

	/**
	 * Update a specific profile value
	 * 
	 * @param {string} key Name of the parameter value
	 * @param {string|number} value Value of the parameter value
	 * 
	 * @returns {boolean} Flag indidicates if value was successfully updated or not
	 */
	updateParameter(key, value) {
		if (key in this.parameter) {
			this.parameter[key] = value;
			return true;
		} else {
			return false;
		}
	}

	/**
	 * Returns the current state of the fireplace
	 * 
	 * @returns {object} State values
	 */
	getState() {
		return this.state;
	}

	/**
	 * Update a specific state value
	 * 
	 * @param {string} key Name of the state value
	 * @param {string|number} value Value of the state value
	 * 
	 * @returns {boolean} Flag indidicates if value was successfully updated or not
	 */
	updateState(key, value) {
		if (key in this.state) {
			this.state[key] = value;
			return true;
		} else {
			return false;
		}
	}

}
