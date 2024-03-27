import { createRouter, createWebHistory } from 'vue-router'
import MainPage from "@/pages/MainPage";
import LoginPage from "@/pages/LoginPage";
import MonitoringPage from "@/pages/MonitoringPage";

const routes = [
  {
    path: '/',
    name: '',
    component: MainPage
  },
  {
    path: '/login',
    name: 'login',
    component: LoginPage
  },
  {
    path: '/monitoring',
    name: 'monitoring',
    component: MonitoringPage
  },

]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

export default router