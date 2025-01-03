<template>
    <ion-page>
      <ion-header>
        <ion-toolbar>
          <ion-title>登录</ion-title>
        </ion-toolbar>
      </ion-header>
      <ion-content fullscreen>
        <ion-grid class="ion-text-center" style="height: 100%;">
          <ion-row class="ion-justify-content-center ion-align-items-center" style="height: 100%;">
            <ion-col size="12" size-sm="8" size-md="6" size-lg="4">
              <ion-item>
                <ion-input v-model="username" type="text" label="用户名"></ion-input>
              </ion-item>
              <ion-item>
                <ion-input v-model="password" type="password" label="密码">
                  <ion-input-password-toggle slot="end"></ion-input-password-toggle>
                </ion-input>
              </ion-item>
              <ion-button expand="block" @click="login">登录</ion-button>
              <ion-button expand="block" fill="outline" router-link="/signup">前往注册</ion-button>
              </ion-col>
          </ion-row>
        </ion-grid>
      </ion-content>
    </ion-page>
  </template>
  
  <script setup lang="ts">
  import { IonPage, IonHeader, IonToolbar, IonTitle, IonContent,IonInput,IonItem,IonInputPasswordToggle, IonButton,IonGrid,IonCol,IonRow,useIonRouter } from '@ionic/vue';
  import { ref } from 'vue';
  import { presentAlert, errorAlert } from '@/utils/alert';
  import { backendUrl } from '@/utils/config';
  import storage from "@/utils/storage";
  import axios from 'axios';
  import startTokenRefreshTask from '@/utils/refresh';;
  import { refreshGap } from '@/utils/refresh';
  const username = ref('');
  const password = ref('');
  const ionRouter = useIonRouter();
  interface LoginResponse {
    access_token: string;
    refresh_token: string;
  }
  const login = async () => {
  if (!username.value || !password.value) {
    presentAlert("请输入用户名和密码","","");
    return;
  }

  try {
    // 发送POST请求
    const response = await axios.post<LoginResponse>(backendUrl+'/user/signin', {
      userName: username.value,
      password: password.value
    });

    // 检查返回的状态
    if (response.status === 200) {
      const { access_token, refresh_token } = response.data;
      const now = new Date(); 
      const thirtyMinutesLater = new Date(now.getTime() + refreshGap); 
      const timestamp = thirtyMinutesLater.getTime(); 
      await Promise.all([
        (await storage).set('access_token', access_token),
        (await storage).set('refresh_token', refresh_token),
        (await storage).set('refresh_time', timestamp),
      ]);
      startTokenRefreshTask();
      ionRouter.push('/tabs/home');
    } else {
      presentAlert("登录失败，请检查用户名和密码","","");
    }
  } catch (error:any) {
    errorAlert(error);
  }
};

  </script>
  