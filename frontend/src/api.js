import axios from 'axios';
const API_BASE = '/api';
export const getVideoState = () => axios.get(`${API_BASE}/video/state`);
export const getCameras = () => axios.get(`${API_BASE}/devices/cameras`);
export const setSource = (type, value) => axios.post(`${API_BASE}/control/source`, { type, value });
export const uploadVideo = (file) => {
  const formData = new FormData();
  formData.append('file', file);
  return axios.post(`${API_BASE}/control/upload`, formData);
};
export const setAnalytics = (enabled) => axios.post(`${API_BASE}/control/analytics`, { enabled });
export const setMode = (mode) => axios.post(`${API_BASE}/control/mode`, { mode });
export const getEvents = (limit = 50) => axios.get(`${API_BASE}/data/events?limit=${limit}`);
export const getLogs = (limit = 100) => axios.get(`${API_BASE}/data/logs?limit=${limit}`);
