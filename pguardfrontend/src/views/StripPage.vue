<template>
  <ion-page>
    <ion-header>
      <ion-toolbar>
        <ion-buttons slot="start">
          <ion-back-button>返回</ion-back-button>
        </ion-buttons>
        <ion-buttons slot="end">
          <ion-button id="more-options-button">
            <ion-icon slot="end" :icon="ellipsisHorizontalOutline"></ion-icon>
          </ion-button>
        </ion-buttons>

        <ion-popover trigger="more-options-button" dismiss-on-select="true">
          <ion-content>
            <ion-list>
              <ion-item button @click="detectDisease">
                疾病检测
              </ion-item>
              <ion-item button @click="editPlotName">
                修改名称
              </ion-item>
              <ion-item button color="danger" @click="deletePlot">
                删除地块
              </ion-item>
            </ion-list>
          </ion-content>
        </ion-popover>
        <ion-title>{{ plotData.plotName || '地块详情' }}</ion-title>
      </ion-toolbar>
    </ion-header>

    <ion-content>
      <!-- 地块基本信息 -->
      <ion-card>
        <ion-item lines="none">
          <ion-thumbnail slot="start">
            <ion-img alt="地块图片" :src="`${backendUrl}${plotData.plantIconURL}`" />
          </ion-thumbnail>

          <ion-label>
            <h2>{{ plotData.plotName }}</h2>
            <p>作物: {{ plotData.plantName }}</p>
          </ion-label>
        </ion-item>

        <ion-card-content>
          <ion-label>
            植物特性:
            <span v-if="!showFullFeature">{{ truncatedFeature }}</span>
            <span v-else>{{ plotData.plantFeature }}</span>
            <ion-button fill="clear" size="small" @click="toggleFeature">
              {{ showFullFeature ? '收起' : '展开' }}
            </ion-button>
          </ion-label>
        </ion-card-content>
      </ion-card>

      <!-- 日志记录 -->
      <ion-list v-if="plotData.logs.length > 0">
        <ion-list-header>
          <ion-title>日志记录</ion-title>
        </ion-list-header>
        <ion-item v-for="(log, index) in plotData.logs" :key="index" lines="full">
          <ion-thumbnail slot="start" v-if="log.imagesURL">
            <ion-img alt="识别的图片" :src="backendUrl+log.imagesURL" />
          </ion-thumbnail>
          <ion-label>
            <h2>{{ log.timeStamp }}</h2>
            <p>{{ log.content }}</p>
          </ion-label>
        </ion-item>
      </ion-list>

      <!-- 无日志记录时的空状态 -->
      <ion-card v-else>
        <ion-card-header>
          <ion-card-title>暂无日志记录</ion-card-title>
        </ion-card-header>
        <ion-card-content>
          <p>当前地块没有日志记录。您可以通过检测功能生成日志。</p>
        </ion-card-content>
      </ion-card>
    </ion-content>
    <!-- 修改名称模态框 -->
    <ion-modal :is-open="showModal" @did-dismiss="closeModal">
      <ion-header>
        <ion-toolbar>
          <ion-title>修改地块名称</ion-title>
          <ion-buttons slot="start">
            <ion-button @click="closeModal">关闭</ion-button>
          </ion-buttons>
        </ion-toolbar>
      </ion-header>
      <ion-content>
        <ion-item>
          <ion-input v-model="newPlotName" placeholder="请输入新的地块名称" label="新地块名称" />
        </ion-item>
        <ion-button expand="full" @click="submitPlotNameChange">确认修改</ion-button>
      </ion-content>
    </ion-modal>
    <ion-modal :is-open="showDetectModal" @did-dismiss="closeDetectModal">
      <ion-header>
        <ion-toolbar>
          <ion-title>疾病检测</ion-title>
          <ion-buttons slot="start">
            <ion-button @click="closeDetectModal">关闭</ion-button>
          </ion-buttons>
        </ion-toolbar>
      </ion-header>
      <ion-content>
        <ion-item><input type="file" accept=".jpg,.jpeg,.png" @change="onFileChange" /></ion-item>

        <ion-button expand="full" @click="submitDetect" :disabled="!selectedFile">
          提交检测
        </ion-button>

        <ion-card v-if="detectionResult">
          <ion-card-header>
            <ion-card-title>检测结果</ion-card-title>
          </ion-card-header>
          <ion-card-content>
            <p>病害名称: {{ detectionResult.diseaseName }}</p>
            <p>建议: {{ detectionResult.advice }}</p>
            <p>置信度: {{ detectionResult.percent }}%</p>
            <ion-img :src="`${backendUrl}${detectionResult.imageURL}`" alt="检测图片"></ion-img>
          </ion-card-content>
        </ion-card>
      </ion-content>
    </ion-modal>
  </ion-page>
</template>

<script setup lang="ts">
import { useIonRouter, IonPage, IonContent, IonHeader, IonToolbar, IonTitle, IonCard, IonCardHeader, IonCardTitle,
   IonCardContent, IonItem, IonLabel, IonThumbnail, IonButton, IonButtons, IonBackButton, IonList, IonListHeader,
    IonIcon, IonPopover, IonImg, IonModal, IonInput, onIonViewWillEnter,} from '@ionic/vue';
import { ellipsisHorizontalOutline } from 'ionicons/icons';
import { ref, computed, nextTick } from 'vue';
import { useRoute } from 'vue-router';
import axios from 'axios';
import { backendUrl } from '@/utils/config';
import { presentAlert, errorAlert } from '@/utils/alert';
import storage from '@/utils/storage';

// 接口类型
interface Log {
  logId: string;
  timeStamp: string;
  content: string;
  imagesURL?: string;
}

interface PlotDetails {
  plotId: string;
  plotName: string;
  plantId: string;
  plantName: string;
  plantFeature: string;
  plantIconURL: string;
  logs: Log[];
}

// 路由与数据
const route = useRoute();
const ionRouter = useIonRouter();
const plotId = route.params.id as string;
const plotData = ref<PlotDetails>({
  plotId: '',
  plotName: '',
  plantId: '',
  plantName: '',
  plantFeature: '',
  plantIconURL: '',
  logs: [],
});

// 展开/收起功能
const showFullFeature = ref(false);
const toggleFeature = () => {
  showFullFeature.value = !showFullFeature.value;
};
const truncatedFeature = computed(() =>
  plotData.value.plantFeature.length > 50
    ? plotData.value.plantFeature.substring(0, 50) + '...'
    : plotData.value.plantFeature
);

// 获取地块详情
const fetchPlotDetails = async () => {
  try {
    const token = await (await storage).get('access_token');
    if (!token) {
      ionRouter.push('/login');
      return;
    }

    const response = await axios.get<PlotDetails>(`${backendUrl}/plot/${plotId}`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    if (response.status === 200) {
      plotData.value = response.data;
    } else {
      presentAlert('错误', '', response.statusText);
    }
  } catch (error: any) {
    errorAlert(error);
  }
};


// 删除地块
const deletePlot = async () => {
  try {
    const token = await (await storage).get('access_token');
    if (!token) {
      ionRouter.push('/login');
      return;
    }

    const response = await axios.delete(`${backendUrl}/plot/${plotId}`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    if (response.status === 200) {
      presentAlert('成功', '', '地块已删除');
      
      ionRouter.push('/tabs/home');
    } else {
      presentAlert('错误', '', response.statusText);
    }
  } catch (error: any) {
    errorAlert(error);
  }
};

onIonViewWillEnter(() => {
  fetchPlotDetails();
});

interface ChangeNameResponce {
  plotId: string,
  plotName: string,
  message: string
}

// 数据绑定
const showModal = ref(false);  // 控制模态框的显示
const newPlotName = ref('');   // 新的地块名称

// 修改名称逻辑
const editPlotName = () => {
  console.log("editPlotName triggered");
  showModal.value = true;
};

// 关闭模态框
const closeModal = () => {
  showModal.value = false;
};

// 提交名称更改
const submitPlotNameChange = async () => {
  try {
    const token = await (await storage).get('access_token');
    if (!token) {
      return ionRouter.push('/login');
    }

    if (!newPlotName.value.trim()) {
      return presentAlert('错误', '', '请输入有效的地块名称');
    }

    const response = await axios.patch<ChangeNameResponce>(
      `${backendUrl}/plot/${plotId}`,
      newPlotName.value,
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    );

    if (response.status === 200) {
      plotData.value.plotName = response.data.plotName;  // 更新地块名称
      presentAlert('成功', '', '地块名称已更新');
      closeModal();  // 关闭模态框
    } else {
      presentAlert('错误', '', response.data.message);
    }
  } catch (error: any) {
    errorAlert(error);
  }
};
const showDetectModal = ref(false); // 控制疾病检测模态框的显示
const selectedFile = ref<File | null>(null); // 用户选择的文件
const detectionResult = ref<any>(null); // 检测结果

// 打开疾病检测模态框
const detectDisease = () => {
  showDetectModal.value = true;
};

// 关闭疾病检测模态框
const closeDetectModal = () => {
  showDetectModal.value = false;
  selectedFile.value = null;
  detectionResult.value = null;
};

// 处理文件选择
const onFileChange = (event: Event) => {
  const target = event.target as HTMLInputElement;
  if (target.files && target.files[0]) {
    selectedFile.value = target.files[0];
  }
};

// 提交检测请求
const submitDetect = async () => {
  if (!selectedFile.value) {
    return presentAlert('错误', '', '请先选择图片文件');
  }

  try {
    const token = await (await storage).get('access_token');
    if (!token) {
      return ionRouter.push('/login');
    }

    const formData = new FormData();
    formData.append('file', selectedFile.value);

    const response = await axios.post(
      `${backendUrl}/plot/${plotId}/detect`,
      formData,
      {
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'multipart/form-data',
        },
      }
    );

    if (response.status === 200) {
      detectionResult.value = response.data;
      presentAlert('成功', '', '检测完成');
      fetchPlotDetails();
    } else {
      presentAlert('错误', '', response.statusText);
    }
  } catch (error: any) {
    errorAlert(error);
  }
};

</script>