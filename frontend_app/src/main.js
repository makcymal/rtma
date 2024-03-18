import "bootstrap/dist/css/bootstrap.css"
import router from './router'
import axios from 'axios'

import { createApp } from 'vue'
import App from './App.vue'

axios.defaults.xsrfCookieName = "csrftoken";
axios.defaults.xsrfHeaderName = "X-CSRFToken";
axios.defaults.baseURL = "http://127.0.0.1:8082/";

createApp(App).use(router).mount('#app')

import "bootstrap/dist/js/bootstrap.js"