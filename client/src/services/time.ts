/**
 * Pad values by leading zero
 * 
 * @returns {string} Hour, minute or second with a leading zero
 */
export function formatTime(value) {
	return value.toString().padStart(2, "0");
}

/**
 * Get time for clock
 * 
 * @returns {string} Time in format hh:mm
 */
export function getClockTime() {
	const date = new Date();
	let h = formatTime(date.getHours());
	let m = formatTime(date.getMinutes());
	return `${h}:${m}`;
}
