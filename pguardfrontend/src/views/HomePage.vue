<template>
  <ion-page>
    <ion-header>
      <ion-toolbar>
        <ion-searchbar placeholder="搜索地块" @ionInput="handleSearch"></ion-searchbar>
      </ion-toolbar>
    </ion-header>
    <ion-content>
      <ion-grid>
        <ion-row>
          <ion-col size="6" v-for="(card, index) in cards" :key="index">
            <ion-card button :router-link="`/strip/${card.id}`">
              <img alt="地块图片" :src="card.image" />
              <ion-card-header>
                <ion-card-title>{{ card.name }}</ion-card-title>
              </ion-card-header>
            </ion-card>
          </ion-col>
        </ion-row>
      </ion-grid>
    </ion-content>
  </ion-page>
</template>

<script setup lang="ts">
import { IonPage, IonHeader, IonToolbar, IonTitle, IonContent,IonCard,IonCardHeader,IonCardTitle,IonGrid,IonRow,IonCol,IonSearchbar } from '@ionic/vue';
import { ref, onMounted} from 'vue';
import { backendUrl } from '@/config';
import { presentAlert,errorAlert } from '@/alert';
import axios from 'axios'; 
const cards = ref();
const fetchCards = async () => {
  try {
    const params = { username: 'aaa' }; 

    const response = await axios.get(backendUrl+'/cards', { params });

    if (response.status === 200) {
      cards.value = response.data; 
    } else {
      presentAlert("错误","",response.statusText);
    }
  } catch (error:any) {
    errorAlert(error)

  }
};
const searchQuery = ref('');
const filteredCards = ref(cards.value);
const handleSearch = (event: Event) => {
  const query = (event.target as HTMLIonSearchbarElement).value?.toLowerCase() || '';
  searchQuery.value = query;
  filteredCards.value = cards.value.filter((card: { name: string; }) => card.name.toLowerCase().includes(query));
};
onMounted(() => {
  fetchCards();
});
</script>
