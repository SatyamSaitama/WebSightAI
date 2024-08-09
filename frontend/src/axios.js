import axios from 'axios';

// Create an instance of axios to use the same base url for all requests
const instance = axios.create({
  baseURL: 'http://localhost:5000/',
});

export default instance;