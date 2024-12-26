<template>
    <ion-page>
        <ion-header>
          <ion-toolbar>

            <ion-buttons slot="start">
                <ion-back-button></ion-back-button>
            </ion-buttons>
            <ion-buttons slot="end">
              <ion-button>病害检测</ion-button>
              <ion-button>虫害检测</ion-button>
              <ion-button>删除地块</ion-button>
            </ion-buttons>
            <ion-title>地块{{ $route.params.id }}</ion-title>
          </ion-toolbar>
        </ion-header>
        
        <ion-content>
          <img alt="地块图片" src="https://t7.baidu.com/it/u=4264092703,2967343056&fm=193&f=GIF" />
          <ion-item>
            <ion-label>相关信息</ion-label>
          </ion-item>
          <h1>历史记录</h1>
          <ion-card v-for="(history,index) in histories" :key="index" >
            <ion-card-header>
              <ion-card-title>{{ history.time }}</ion-card-title>
              <ion-card-subtitle>{{ history.type }}</ion-card-subtitle>
            </ion-card-header>
            <ion-card-content>
              <ion-item>
                <ion-thumbnail  slot="start">
                  <img alt="识别的图片" :src="history.image" />
                </ion-thumbnail>
                <ion-label>{{ history.result }}</ion-label>
              </ion-item>
            </ion-card-content>
          </ion-card>
        </ion-content>
    </ion-page>
  </template>
    
  <script setup lang="ts">
  import { 
    IonPage,
    IonContent,
    IonHeader,
    IonToolbar,
    IonTitle,
    IonCard,
    IonCardHeader,
    IonCardTitle,
    IonCardSubtitle,
    IonCardContent,
    IonItem,
    IonLabel,
    IonThumbnail,
    IonButton,
    IonButtons,
    IonBackButton
  } from '@ionic/vue';
  import { ref } from 'vue';
  const histories=ref([
    {time:"20241126-12:00",type:"病害检测",result:"无异常",image:"https://t7.baidu.com/it/u=4264092703,2967343056&fm=193&f=GIF"},
    {time:"20241126-13:00",type:"虫害检测",result:"有轻微虫害",image:"https://t7.baidu.com/it/u=4264092703,2967343056&fm=193&f=GIF"}
  ]);
  </script>
    