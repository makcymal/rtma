import { createRouter, createWebHistory } from 'vue-router'
import MainPage from "@/pages/MainPage";
import LoginPage from "@/pages/LoginPage";

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

]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

export default router