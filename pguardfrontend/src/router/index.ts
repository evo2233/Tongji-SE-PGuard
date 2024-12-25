import { createRouter, createWebHistory } from '@ionic/vue-router';
import { RouteRecordRaw } from 'vue-router';
import TabsPage from '../views/TabsPage.vue'

const routes: Array<RouteRecordRaw> = [
  {
    path: '/',
    redirect: '/tabs/home'
  },
  {
    path: '/tabs/',
    component: TabsPage,
    beforeEnter: (to, from, next) => {
      const isLoggedIn = checkLoginStatus(); 
      if (!isLoggedIn) {
        next('/login'); 
      } else {
        next(); 
      }
    },
    children: [
      {
        path: '',
        redirect: '/tabs/home'
      },
      {
        path: 'home',
        component: () => import('@/views/HomePage.vue')
      },
      {
        path: 'info',
        component: () => import('@/views/InfoPage.vue')
      },
      {
        path: '/strip/:id',
        component: () => import('@/views/StripPage.vue'),
      }
    ]
  },
  {
    path:'/login',
    component:()=> import('@/views/LoginPage.vue')
  },
  {
    path:'/signup',
    component:()=> import('@/views/SignupPage.vue')
  }
]
function checkLoginStatus() {
  return sessionStorage.getItem('isLoggedIn') === 'true';
}

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

export default router
