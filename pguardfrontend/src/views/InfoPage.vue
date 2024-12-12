<template>
  <ion-page>
    <ion-content :fullscreen="true">
      <ion-item>
        <ion-thumbnail  slot="start">
          <img alt="识别的图片" :src="info.image" />
            </ion-thumbnail>
        <ion-label>{{ info.username }}</ion-label>
      </ion-item>
      <IonItem>
        <IonLabel>ID: {{ info.id }}</IonLabel>
      </IonItem>
      <IonItem>
        <IonLabel>所在地: {{ info.location }}</IonLabel>
      </IonItem>
      <IonItem>
        <IonLabel>剩余使用次数: {{ info.vip }}</IonLabel>
      </IonItem>
      <IonItem>
        <IonButton expand="block" @click="">年终总结</IonButton>
        <IonButton expand="block" @click="">套餐充值</IonButton>
        <IonButton expand="block" @click="">更改用户信息</IonButton>
        <IonButton expand="block" @click="logout">退出登录</IonButton>
      </IonItem>
    </ion-content>
  </ion-page>
</template>

<script setup lang="ts">
import { IonPage,  IonContent,IonItem,IonThumbnail,IonLabel, IonButton,useIonRouter } from '@ionic/vue';
import { ref } from 'vue';

const ionRouter = useIonRouter();
const info=ref({
  image:"https://t7.baidu.com/it/u=4264092703,2967343056&fm=193&f=GIF",
  username:"用户名",
  id:"uuid",
  location:"上海",
  vip:0,

});
const logout=async()=>{
  sessionStorage.removeItem('isLoggedIn');
  ionRouter.push("/login");
}
</script>
