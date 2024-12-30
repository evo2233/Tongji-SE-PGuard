<template>
  <ion-page>
    <ion-header>
      <ion-toolbar>
        <ion-searchbar placeholder="搜索地块" @ionInput="handleSearch"></ion-searchbar>
      </ion-toolbar>
    </ion-header>
    <ion-content>
      <!-- 有数据时显示地块卡片 -->
      <ion-grid v-if="filteredCards.length > 0">
        <ion-row>
          <ion-col size="6" v-for="(card, index) in filteredCards" :key="index">
            <ion-card button :router-link="`/tabs/strip/${card.plotId}`">
              <ion-img alt="图片" :src="backendUrl+card.plantIconURL" />
              <ion-card-header>
                <ion-card-title>{{ card.plotName }}</ion-card-title>
                <ion-card-subtitle>{{ card.plantName }}</ion-card-subtitle>
              </ion-card-header>
            </ion-card>
          </ion-col>
        </ion-row>
      </ion-grid>

      <!-- 无数据时显示空状态 -->
      <ion-card v-else>
        <ion-card-header>
          <ion-card-title>暂无地块数据</ion-card-title>
        </ion-card-header>
        <ion-card-content>
          <p>目前没有可显示的地块。您可以点击下方的添加按钮，创建新的地块。</p>
        </ion-card-content>
      </ion-card>
    </ion-content>


    <ion-fab vertical="bottom" horizontal="end" slot="fixed">
      <ion-fab-button @click="openModal">
        <ion-icon :icon="addOutline"></ion-icon>
      </ion-fab-button>
    </ion-fab>

    <ion-modal :is-open="isModalOpen" @will-dismiss="closeModal">
      <ion-header>
        <ion-toolbar>
          <ion-title>创建地块</ion-title>
          <ion-buttons slot="end">
            <ion-button @click="closeModal">关闭</ion-button>
          </ion-buttons>
        </ion-toolbar>
      </ion-header>
      <ion-content>
        <ion-list>
          <ion-item>
            <ion-label position="stacked">地块名称</ion-label>
            <ion-input v-model="newPlot.plotName" placeholder="请输入地块名称"></ion-input>
          </ion-item>
          <ion-item>
            <ion-label position="stacked">作物名称</ion-label>
            <ion-input v-model="newPlot.plantName" placeholder="请输入作物名称"></ion-input>
          </ion-item>
        </ion-list>
        <ion-button expand="full" @click="submitNewPlot">提交</ion-button>
      </ion-content>
    </ion-modal>
  </ion-page>
</template>
<script setup lang="ts">
import { useIonRouter,IonPage, IonHeader, IonToolbar, IonContent,IonCard,IonCardHeader,IonCardTitle,
  IonGrid,IonRow,IonCol,IonSearchbar,IonCardSubtitle,IonFab,IonFabButton,IonIcon,IonModal,IonTitle,IonButtons,
  IonButton,IonList,IonItem,IonLabel,IonInput,IonImg, onIonViewWillEnter,IonCardContent } from '@ionic/vue';
import { addOutline } from 'ionicons/icons';
import { ref, computed, onMounted,defineComponent } from 'vue';
import { backendUrl } from '@/utils/config';
import { presentAlert, errorAlert } from '@/utils/alert';
import storage from '@/utils/storage';
import axios from 'axios';

interface PlotResponse {
  plotId: string;
  plantIconURL: string;
  plotName: string;
  plantName: string;
}

const ionRouter = useIonRouter();
const cards = ref<PlotResponse[]>([]); // 原始卡片数据
const searchQuery = ref(''); // 搜索关键词
const isModalOpen = ref(false); // 控制模态窗口开关
const newPlot = ref({ plotName: '', plantName: '' }); // 新地块数据

// 动态过滤卡片列表，支持主标题和副标题搜索
const filteredCards = computed(() =>
  cards.value.filter(
    (card) =>
      card.plotName.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
      card.plantName.toLowerCase().includes(searchQuery.value.toLowerCase())
  )
);

const fetchCards = async () => {
  try {
    const token = await storage.get('access_token');
    if (!token) {
      ionRouter.push('/login');
      return;
    }

    const response = await axios.get<PlotResponse[]>(backendUrl + '/plot', {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    if (response.status === 200) {
      cards.value = response.data && response.data.length > 0 ? response.data : [];
    } else {
      presentAlert('错误', '', response.statusText);
    }
  } catch (error: any) {
    errorAlert(error);
  }
};

// 打开模态窗口
const openModal = () => {
  isModalOpen.value = true;
};

// 关闭模态窗口
const closeModal = () => {
  isModalOpen.value = false;
  newPlot.value = { plotName: '', plantName: '' }; // 重置输入内容
};

// 提交新地块数据
const submitNewPlot = async () => {
  try {
    const token = await storage.get('access_token');
    if (!token) {
      ionRouter.push('/login');
      return;
    }

    const response = await axios.post(
      `${backendUrl}/plot/add`,
      {
        plotName: newPlot.value.plotName,
        plantName: newPlot.value.plantName,
      },
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    );

    if (response.status === 200 || response.status === 201) {
      presentAlert('成功', '', '地块创建成功！');
      closeModal();
      fetchCards(); 
    } else {
      presentAlert('错误', '', response.statusText);
    }
  } catch (error: any) {
    errorAlert(error);
  }
};

// 处理搜索输入
const handleSearch = (event: Event) => {
  const input = event.target as HTMLInputElement;
  searchQuery.value = input.value;
};

onMounted(() => {
  fetchCards();
});
onIonViewWillEnter(() => {
  fetchCards();
});
</script>