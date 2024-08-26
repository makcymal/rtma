import "bootstrap/dist/css/bootstrap.css"
import router from './router'
import axios from 'axios'
import { createPinia } from "pinia"


import { createApp } from 'vue'
import App from './App.vue'

import { baseProtocol, baseAddr, basePort }  from './serverConfig'

const pinia = createPinia();

axios.defaults.xsrfCookieName = "csrftoken";
axios.defaults.xsrfHeaderName = "X-CSRFToken";
axios.defaults.baseURL = baseProtocol + baseAddr + basePort + '/';

createApp(App).use(pinia).use(router).mount('#app')

import "bootstrap/dist/js/bootstrap.js"
