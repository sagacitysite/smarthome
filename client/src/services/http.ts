import axios from 'axios';

const URL = 'http://192.168.1.126:4000';

export async function get(path) {
	return axios.get(`${URL}${path}`);
}

export async function post(path, data) {
	return axios.post(`${URL}${path}`, data);
}

export async function patch(path, data) {
	return axios.patch(`${URL}${path}`, data);
}
